from .celery import celery
from app.core.pocketbase import pb_client
from app.services.social_media import SocialMediaService
from app.services.ai_matching import AIMatchingService
import structlog
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio

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
        
        # Placeholder for actual matching logic
        # In production, this would:
        # 1. Get all eligible athletes
        # 2. Run AI matching algorithm
        # 3. Store results in database or cache
        # 4. Send notifications to brand
        
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
        
        # Placeholder for actual notification logic:
        # - Email notifications
        # - Push notifications
        # - In-app notifications
        # - SMS for urgent updates
        
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