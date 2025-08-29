import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import structlog

from app.core.config import settings
from app.core.pocketbase import pb_client

logger = structlog.get_logger()

class SocialMediaService:
    def __init__(self):
        self.instagram_client_id = settings.INSTAGRAM_CLIENT_ID
        self.instagram_client_secret = settings.INSTAGRAM_CLIENT_SECRET
        self.tiktok_client_key = settings.TIKTOK_CLIENT_KEY
        self.tiktok_client_secret = settings.TIKTOK_CLIENT_SECRET
        self.twitter_bearer_token = settings.TWITTER_BEARER_TOKEN
    
    async def sync_athlete_metrics(self, athlete_id: str, social_accounts: Dict[str, str]) -> List[Dict]:
        """Sync metrics from all linked social media accounts"""
        updated_metrics = []
        
        for platform, username in social_accounts.items():
            try:
                if platform == "instagram" and self.instagram_client_id:
                    metrics = await self._get_instagram_metrics(username)
                elif platform == "tiktok" and self.tiktok_client_key:
                    metrics = await self._get_tiktok_metrics(username)
                elif platform == "twitter" and self.twitter_bearer_token:
                    metrics = await self._get_twitter_metrics(username)
                else:
                    logger.warning(f"Platform {platform} not configured or not supported")
                    continue
                
                if metrics:
                    # Update or create metrics record
                    metric_record = await self._update_athlete_metric_record(
                        athlete_id, platform, metrics
                    )
                    updated_metrics.append(metric_record)
                    
            except Exception as e:
                logger.error(f"Failed to sync {platform} metrics", 
                           athlete_id=athlete_id, username=username, error=str(e))
                continue
        
        logger.info("Social media metrics synced", 
                   athlete_id=athlete_id, 
                   platforms=list(social_accounts.keys()),
                   updated_count=len(updated_metrics))
        
        return updated_metrics
    
    async def _get_instagram_metrics(self, username: str) -> Optional[Dict]:
        """Get Instagram metrics via Instagram Basic Display API"""
        try:
            # Note: This is a simplified version. In production, you'd need:
            # 1. Instagram Business Account verification
            # 2. Proper OAuth flow for user consent
            # 3. Instagram Graph API access
            
            # For demo purposes, return mock data
            mock_metrics = {
                "followers": 50000 + hash(username) % 100000,
                "engagement_rate": 5.5 + (hash(username) % 50) / 10,
                "avg_likes": 2000 + hash(username) % 5000,
                "avg_comments": 150 + hash(username) % 300,
                "avg_shares": 50 + hash(username) % 100,
                "audience_demographics": {
                    "age_groups": {
                        "18-24": 35,
                        "25-34": 40,
                        "35-44": 20,
                        "45+": 5
                    },
                    "gender": {
                        "male": 60,
                        "female": 40
                    },
                    "top_locations": ["United States", "Canada", "United Kingdom"]
                },
                "content_categories": ["sports", "lifestyle", "fitness"]
            }
            
            logger.info("Instagram metrics retrieved (mock)", username=username)
            return mock_metrics
            
        except Exception as e:
            logger.error("Instagram API error", username=username, error=str(e))
            return None
    
    async def _get_tiktok_metrics(self, username: str) -> Optional[Dict]:
        """Get TikTok metrics via TikTok for Business API"""
        try:
            # Mock TikTok data for demo
            mock_metrics = {
                "followers": 30000 + hash(username) % 80000,
                "engagement_rate": 8.2 + (hash(username) % 40) / 10,
                "avg_likes": 5000 + hash(username) % 10000,
                "avg_comments": 300 + hash(username) % 600,
                "avg_shares": 200 + hash(username) % 400,
                "audience_demographics": {
                    "age_groups": {
                        "16-20": 45,
                        "21-25": 30,
                        "26-30": 15,
                        "31+": 10
                    },
                    "gender": {
                        "male": 55,
                        "female": 45
                    }
                },
                "content_categories": ["sports", "entertainment", "lifestyle"]
            }
            
            logger.info("TikTok metrics retrieved (mock)", username=username)
            return mock_metrics
            
        except Exception as e:
            logger.error("TikTok API error", username=username, error=str(e))
            return None
    
    async def _get_twitter_metrics(self, username: str) -> Optional[Dict]:
        """Get Twitter metrics via Twitter API v2"""
        try:
            # Mock Twitter data for demo
            mock_metrics = {
                "followers": 20000 + hash(username) % 60000,
                "engagement_rate": 3.5 + (hash(username) % 30) / 10,
                "avg_likes": 500 + hash(username) % 2000,
                "avg_comments": 50 + hash(username) % 200,
                "avg_shares": 100 + hash(username) % 300,
                "audience_demographics": {
                    "age_groups": {
                        "18-24": 25,
                        "25-34": 35,
                        "35-44": 25,
                        "45+": 15
                    },
                    "interests": ["sports", "news", "technology"]
                },
                "content_categories": ["sports", "news", "personal"]
            }
            
            logger.info("Twitter metrics retrieved (mock)", username=username)
            return mock_metrics
            
        except Exception as e:
            logger.error("Twitter API error", username=username, error=str(e))
            return None
    
    async def _update_athlete_metric_record(self, athlete_id: str, platform: str, metrics: Dict) -> Dict:
        """Update or create athlete metrics record in PocketBase"""
        try:
            # Check if record exists
            try:
                existing_record = pb_client.client.collection("athlete_metrics").get_first_list_item(
                    f"athlete = '{athlete_id}' && platform = '{platform}'"
                )
                
                # Update existing record
                updated_record = pb_client.client.collection("athlete_metrics").update(
                    existing_record.id,
                    {
                        **metrics,
                        "last_updated": datetime.now().isoformat()
                    }
                )
                
            except Exception:
                # Create new record
                updated_record = pb_client.client.collection("athlete_metrics").create({
                    "athlete": athlete_id,
                    "platform": platform,
                    **metrics,
                    "last_updated": datetime.now().isoformat()
                })
            
            logger.info("Athlete metrics record updated", 
                       athlete_id=athlete_id, 
                       platform=platform,
                       followers=metrics.get("followers"))
            
            return updated_record.to_dict()
            
        except Exception as e:
            logger.error("Failed to update athlete metrics record", 
                        athlete_id=athlete_id, platform=platform, error=str(e))
            raise
    
    async def get_aggregated_metrics(self, athlete_id: str) -> Dict:
        """Get aggregated social media metrics for an athlete"""
        try:
            metrics = pb_client.client.collection("athlete_metrics").get_list(
                filter=f"athlete = '{athlete_id}'",
                sort="-last_updated"
            )
            
            if not metrics.items:
                return {
                    "total_followers": 0,
                    "avg_engagement_rate": 0,
                    "platform_count": 0,
                    "platforms": []
                }
            
            total_followers = sum(m.followers or 0 for m in metrics.items)
            engagement_rates = [m.engagement_rate for m in metrics.items if m.engagement_rate]
            avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
            
            platform_data = {}
            for metric in metrics.items:
                platform_data[metric.platform] = {
                    "followers": metric.followers,
                    "engagement_rate": metric.engagement_rate,
                    "last_updated": metric.last_updated
                }
            
            return {
                "total_followers": total_followers,
                "avg_engagement_rate": round(avg_engagement, 2),
                "platform_count": len(metrics.items),
                "platforms": platform_data,
                "last_sync": max(m.last_updated for m in metrics.items)
            }
            
        except Exception as e:
            logger.error("Failed to get aggregated metrics", athlete_id=athlete_id, error=str(e))
            raise
    
    async def schedule_metrics_refresh(self, athlete_id: str) -> bool:
        """Schedule background task to refresh athlete's social media metrics"""
        try:
            # Get athlete's social media accounts
            athlete = pb_client.client.collection("athletes").get_one(athlete_id)
            social_media = athlete.social_media
            
            if not social_media:
                return False
            
            # In a production environment, this would queue a background task
            # For now, we'll sync immediately
            await self.sync_athlete_metrics(athlete_id, social_media)
            
            logger.info("Metrics refresh scheduled", athlete_id=athlete_id)
            return True
            
        except Exception as e:
            logger.error("Failed to schedule metrics refresh", athlete_id=athlete_id, error=str(e))
            return False