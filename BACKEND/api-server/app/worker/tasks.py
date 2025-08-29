from .celery import celery
from app.core.pocketbase import pb_client
from app.services.social_media import SocialMediaService
from app.services.ai_matching import AIMatchingService
import structlog
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = structlog.get_logger()

@celery.task(bind=True, max_retries=3)
def sync_social_media_metrics(self, athlete_id: str, social_accounts: Dict[str, str]):
    """Background task to sync social media metrics for an athlete"""
    try:
        social_service = SocialMediaService()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        updated_metrics = loop.run_until_complete(
            social_service.sync_athlete_metrics(athlete_id, social_accounts)
        )
        
        logger.info("Background metrics sync completed", 
                   athlete_id=athlete_id, 
                   platforms=list(social_accounts.keys()),
                   updated_count=len(updated_metrics))
        
        return {
            "status": "success",
            "athlete_id": athlete_id,
            "updated_metrics": updated_metrics
        }
        
    except Exception as exc:
        logger.error("Background metrics sync failed", 
                    athlete_id=athlete_id, 
                    error=str(exc),
                    retry_count=self.request.retries)
        
        if self.request.retries < self.max_retries:
            # Retry with exponential backoff
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"status": "failed", "error": str(exc)}

@celery.task
def sync_all_athlete_metrics():
    """Periodic task to sync metrics for all athletes"""
    try:
        # Get all athletes with social media accounts
        athletes = pb_client.client.collection("athletes").get_list(
            filter="social_media != null",
            per_page=500
        )
        
        synced_count = 0
        failed_count = 0
        
        for athlete in athletes.items:
            try:
                social_accounts = athlete.social_media or {}
                if social_accounts:
                    # Queue individual sync task
                    sync_social_media_metrics.delay(athlete.id, social_accounts)
                    synced_count += 1
            except Exception as e:
                logger.error("Failed to queue sync for athlete", athlete_id=athlete.id, error=str(e))
                failed_count += 1
        
        logger.info("All athlete metrics sync queued", 
                   total_athletes=len(athletes.items),
                   synced=synced_count, 
                   failed=failed_count)
        
        return {"synced": synced_count, "failed": failed_count}
        
    except Exception as e:
        logger.error("Failed to sync all athlete metrics", error=str(e))
        return {"error": str(e)}

@celery.task
def calculate_ai_matches(campaign_id: str):
    """Background task to calculate AI matches for a campaign"""
    try:
        ai_service = AIMatchingService()
        
        # Get campaign details
        campaign = pb_client.client.collection("campaigns").get_one(campaign_id, expand="brand")
        
        # Run async matching
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # This would store results in a matches table or cache
        logger.info("AI matches calculation started", campaign_id=campaign_id)
        
        # Get all eligible athletes based on campaign criteria
        athletes = pb_client.client.collection("athletes").get_list(
            per_page=500,
            expand="user"
        )
        
        # Get brand data for the campaign
        brand = campaign.expand.get('brand')
        if not brand:
            raise Exception("Campaign brand data not found")
        
        # Run AI matching using the AIMatchingService
        matches = loop.run_until_complete(
            ai_service.find_athlete_matches(
                brand_data=brand.__dict__,
                athletes_data=[athlete.__dict__ for athlete in athletes.items]
            )
        )
        
        # Store top matches in database
        top_matches = matches[:20]  # Store top 20 matches
        
        for match in top_matches:
            try:
                # Create or update match record
                match_data = {
                    "campaign": campaign_id,
                    "athlete": match["athlete_id"],
                    "brand": brand.id,
                    "overall_score": match["overall_score"],
                    "factors": match["factors"],
                    "estimated_rate": match["estimated_rate"],
                    "status": "pending",
                    "ai_recommendation": match.get("recommendation", "")
                }
                
                # Check if match already exists
                existing_matches = pb_client.client.collection("matches").get_list(
                    filter=f"campaign = '{campaign_id}' && athlete = '{match['athlete_id']}'"
                )
                
                if existing_matches.total_items > 0:
                    # Update existing match
                    pb_client.client.collection("matches").update(
                        existing_matches.items[0].id, match_data
                    )
                else:
                    # Create new match
                    pb_client.client.collection("matches").create(match_data)
                    
            except Exception as e:
                logger.error("Failed to store match", 
                           campaign_id=campaign_id, 
                           athlete_id=match["athlete_id"], 
                           error=str(e))
        
        # Send notification to brand about new matches
        if brand.user and top_matches:
            send_notification.delay(
                brand.user,
                "new_matches_available",
                {
                    "campaign_id": campaign_id,
                    "matches_count": len(top_matches),
                    "top_score": top_matches[0]["overall_score"]
                }
            )
        
        return {"status": "completed", "campaign_id": campaign_id}
        
    except Exception as e:
        logger.error("AI matches calculation failed", campaign_id=campaign_id, error=str(e))
        return {"status": "failed", "error": str(e)}

@celery.task
def send_notification(user_id: str, notification_type: str, data: Dict):
    """Background task to send notifications to users"""
    try:
        # This would integrate with email service, push notifications, etc.
        logger.info("Notification sent", 
                   user_id=user_id, 
                   type=notification_type,
                   data_keys=list(data.keys()))
        
        # Get user details for notification
        user = pb_client.client.collection("users").get_one(user_id)
        
        # Create in-app notification record
        notification_record = {
            "user": user_id,
            "type": notification_type,
            "title": _get_notification_title(notification_type, data),
            "message": _get_notification_message(notification_type, data),
            "data": data,
            "read": False,
            "created": datetime.now().isoformat()
        }
        
        pb_client.client.collection("notifications").create(notification_record)
        
        # Send email notification based on user preferences
        if _should_send_email(notification_type, user):
            _send_email_notification(user.email, notification_type, data)
        
        # Send push notification if user has push tokens
        if hasattr(user, 'push_token') and user.push_token:
            _send_push_notification(user.push_token, notification_type, data)
        
        # Send SMS for urgent notifications
        if notification_type in ['deal_expired', 'payment_failed', 'urgent_update'] and hasattr(user, 'phone') and user.phone:
            _send_sms_notification(user.phone, notification_type, data)
        
        return {"status": "sent", "user_id": user_id, "type": notification_type}
        
    except Exception as e:
        logger.error("Notification failed", user_id=user_id, error=str(e))
        return {"status": "failed", "error": str(e)}

@celery.task
def process_deal_update(deal_id: str, old_status: str, new_status: str):
    """Background task to process deal status changes"""
    try:
        # Get deal details
        deal = pb_client.client.collection("deals").get_one(deal_id, expand="athlete,brand,agent")
        
        # Send notifications to relevant parties
        notifications = []
        
        # Notify athlete
        if hasattr(deal.expand, 'athlete') and deal.expand['athlete']:
            athlete_user_id = deal.expand['athlete'].user
            send_notification.delay(
                athlete_user_id,
                "deal_status_update",
                {"deal_id": deal_id, "old_status": old_status, "new_status": new_status}
            )
            notifications.append(f"athlete:{athlete_user_id}")
        
        # Notify brand
        if hasattr(deal.expand, 'brand') and deal.expand['brand']:
            brand_user_id = deal.expand['brand'].user
            send_notification.delay(
                brand_user_id,
                "deal_status_update", 
                {"deal_id": deal_id, "old_status": old_status, "new_status": new_status}
            )
            notifications.append(f"brand:{brand_user_id}")
        
        # Notify agent if assigned
        if deal.agent:
            send_notification.delay(
                deal.agent,
                "deal_status_update",
                {"deal_id": deal_id, "old_status": old_status, "new_status": new_status}
            )
            notifications.append(f"agent:{deal.agent}")
        
        logger.info("Deal update processed", 
                   deal_id=deal_id, 
                   old_status=old_status,
                   new_status=new_status,
                   notifications_sent=len(notifications))
        
        return {"status": "processed", "notifications": notifications}
        
    except Exception as e:
        logger.error("Deal update processing failed", deal_id=deal_id, error=str(e))
        return {"status": "failed", "error": str(e)}

@celery.task
def update_trending_athletes():
    """Periodic task to update trending athletes rankings"""
    try:
        # Get recent metrics data
        recent_date = datetime.now() - timedelta(days=7)
        
        metrics = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"last_updated >= '{recent_date.isoformat()}'",
            expand="athlete",
            per_page=1000,
            sort="-engagement_rate"
        )
        
        # Calculate trending scores
        trending_data = {}
        
        for metric in metrics.items:
            if hasattr(metric, 'expand') and metric.expand.get('athlete'):
                athlete = metric.expand['athlete']
                athlete_id = athlete.id
                
                # Simple trending score calculation
                followers = metric.followers or 0
                engagement = metric.engagement_rate or 0
                trend_score = (followers / 1000) * engagement
                
                if athlete_id not in trending_data or trend_score > trending_data[athlete_id]["score"]:
                    trending_data[athlete_id] = {
                        "athlete_id": athlete_id,
                        "name": f"{athlete.first_name} {athlete.last_name}",
                        "sport": athlete.sport,
                        "score": trend_score,
                        "followers": followers,
                        "engagement_rate": engagement
                    }
        
        # This would typically store in Redis cache or trending table
        logger.info("Trending athletes updated", count=len(trending_data))
        
        return {"status": "updated", "trending_count": len(trending_data)}
        
    except Exception as e:
        logger.error("Failed to update trending athletes", error=str(e))
        return {"status": "failed", "error": str(e)}

@celery.task
def cleanup_expired_deals():
    """Daily task to clean up expired deals"""
    try:
        current_date = datetime.now().date()
        
        # Find deals past their deadline
        expired_deals = pb_client.client.collection("deals").get_list(
            filter=f"deadline < '{current_date}' && status != 'completed' && status != 'cancelled' && status != 'expired'",
            per_page=500
        )
        
        expired_count = 0
        
        for deal in expired_deals.items:
            try:
                # Update status to expired
                pb_client.client.collection("deals").update(deal.id, {
                    "status": "expired"
                })
                
                # Notify relevant parties
                process_deal_update.delay(deal.id, deal.status, "expired")
                
                expired_count += 1
                
            except Exception as e:
                logger.error("Failed to expire deal", deal_id=deal.id, error=str(e))
        
        logger.info("Expired deals cleanup completed", expired_count=expired_count)
        return {"status": "completed", "expired_deals": expired_count}
        
    except Exception as e:
        logger.error("Expired deals cleanup failed", error=str(e))
        return {"status": "failed", "error": str(e)}

@celery.task  
def generate_daily_analytics():
    """Daily task to generate and cache analytics data"""
    try:
        # Generate platform-wide analytics
        today = datetime.now().date()
        
        # Get daily stats
        daily_stats = {
            "date": today.isoformat(),
            "new_athletes": 0,
            "new_brands": 0,
            "new_deals": 0,
            "total_deal_value": 0,
            "active_campaigns": 0
        }
        
        # Count new records today
        today_filter = f"created >= '{today}'"
        
        new_athletes = pb_client.client.collection("athletes").get_list(
            filter=today_filter, per_page=1
        )
        daily_stats["new_athletes"] = new_athletes.total_items
        
        new_brands = pb_client.client.collection("brands").get_list(
            filter=today_filter, per_page=1
        )
        daily_stats["new_brands"] = new_brands.total_items
        
        new_deals = pb_client.client.collection("deals").get_list(
            filter=today_filter, per_page=500
        )
        daily_stats["new_deals"] = new_deals.total_items
        daily_stats["total_deal_value"] = sum(d.value or 0 for d in new_deals.items)
        
        active_campaigns = pb_client.client.collection("campaigns").get_list(
            filter="status = 'active'", per_page=1
        )
        daily_stats["active_campaigns"] = active_campaigns.total_items
        
        # Store analytics (would typically go to time-series database)
        logger.info("Daily analytics generated", stats=daily_stats)
        
        return daily_stats
        
    except Exception as e:
        logger.error("Daily analytics generation failed", error=str(e))
        return {"status": "failed", "error": str(e)}


# Notification helper functions
def _get_notification_title(notification_type: str, data: Dict) -> str:
    """Generate notification title based on type and data"""
    titles = {
        "deal_status_update": "Deal Status Updated",
        "new_matches_available": "New Matches Available",
        "payment_received": "Payment Received",
        "campaign_approved": "Campaign Approved",
        "deal_expired": "Deal Expired",
        "message_received": "New Message",
        "profile_viewed": "Profile Viewed",
        "payment_failed": "Payment Failed",
        "urgent_update": "Urgent Update"
    }
    return titles.get(notification_type, "Notification")

def _get_notification_message(notification_type: str, data: Dict) -> str:
    """Generate notification message based on type and data"""
    if notification_type == "deal_status_update":
        return f"Your deal status has been updated to {data.get('new_status', 'unknown')}"
    elif notification_type == "new_matches_available":
        count = data.get('matches_count', 0)
        return f"{count} new athlete matches available for your campaign"
    elif notification_type == "payment_received":
        amount = data.get('amount', 0)
        return f"Payment of ${amount:,.2f} has been processed"
    elif notification_type == "campaign_approved":
        return "Your campaign has been approved and is now active"
    elif notification_type == "deal_expired":
        return "Your deal has expired. Please renew or create a new one"
    elif notification_type == "message_received":
        sender = data.get('sender_name', 'Someone')
        return f"You have a new message from {sender}"
    elif notification_type == "profile_viewed":
        viewer = data.get('viewer_name', 'Someone')
        return f"{viewer} viewed your profile"
    elif notification_type == "payment_failed":
        return "Payment failed. Please update your payment method"
    elif notification_type == "urgent_update":
        return data.get('message', 'Important update requiring your attention')
    else:
        return "You have a new notification"

def _should_send_email(notification_type: str, user) -> bool:
    """Determine if email notification should be sent based on user preferences"""
    # Check user email preferences if they exist
    if hasattr(user, 'email_preferences'):
        email_prefs = user.email_preferences or {}
        return email_prefs.get(notification_type, True)
    
    # Default email notifications for important events
    important_notifications = [
        "deal_status_update", "payment_received", "payment_failed", 
        "deal_expired", "urgent_update"
    ]
    return notification_type in important_notifications

def _send_email_notification(email: str, notification_type: str, data: Dict):
    """Send email notification using SMTP"""
    try:
        subject = _get_notification_title(notification_type, data)
        body = _get_notification_message(notification_type, data)
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = f"PlayRight - {subject}"
        
        # Create HTML body
        html_body = f"""
        <html>
            <body>
                <h2>PlayRight Notification</h2>
                <h3>{subject}</h3>
                <p>{body}</p>
                <hr>
                <p>This email was sent from PlayRight. To manage your notification preferences, 
                   log in to your account.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        server.send_message(msg)
        server.quit()
        
        logger.info("Email notification sent", email=email, type=notification_type)
        
    except Exception as e:
        logger.error("Failed to send email notification", email=email, error=str(e))

def _send_push_notification(push_token: str, notification_type: str, data: Dict):
    """Send push notification using FCM or similar service"""
    try:
        title = _get_notification_title(notification_type, data)
        body = _get_notification_message(notification_type, data)
        
        # Example using FCM (Firebase Cloud Messaging)
        fcm_payload = {
            "to": push_token,
            "notification": {
                "title": title,
                "body": body,
                "icon": "ic_notification",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            },
            "data": {
                "type": notification_type,
                **data
            }
        }
        
        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            json=fcm_payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Push notification sent", token=push_token[:10] + "...", type=notification_type)
        else:
            logger.error("Push notification failed", status=response.status_code, response=response.text)
            
    except Exception as e:
        logger.error("Failed to send push notification", token=push_token[:10] + "...", error=str(e))

def _send_sms_notification(phone: str, notification_type: str, data: Dict):
    """Send SMS notification using Twilio or similar service"""
    try:
        title = _get_notification_title(notification_type, data)
        body = _get_notification_message(notification_type, data)
        message = f"PlayRight: {title}\n{body}"
        
        # Example using Twilio
        twilio_payload = {
            "From": settings.TWILIO_PHONE_NUMBER,
            "To": phone,
            "Body": message[:160]  # SMS character limit
        }
        
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
            data=twilio_payload,
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 201:
            logger.info("SMS notification sent", phone=phone[-4:], type=notification_type)
        else:
            logger.error("SMS notification failed", status=response.status_code, response=response.text)
            
    except Exception as e:
        logger.error("Failed to send SMS notification", phone=phone[-4:], error=str(e))