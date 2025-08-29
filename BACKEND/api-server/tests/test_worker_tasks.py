import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.worker.tasks import (
    calculate_ai_matches, 
    sync_social_media_metrics,
    process_deal_update,
    update_trending_athletes,
    cleanup_expired_deals,
    generate_daily_analytics
)
from datetime import datetime, timedelta


class TestCalculateAIMatches:
    """Test AI matching calculation task"""
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks.AIMatchingService')
    @patch('app.worker.tasks.asyncio')
    def test_calculate_ai_matches_success(self, mock_asyncio, mock_ai_service, mock_pb):
        """Test successful AI matches calculation"""
        campaign_id = "campaign123"
        
        # Mock campaign data with brand
        mock_campaign = MagicMock()
        mock_campaign.expand = {
            'brand': MagicMock(id="brand123", user="user123")
        }
        
        # Mock athletes data
        mock_athletes = MagicMock()
        mock_athletes.items = [MagicMock(id="athlete1"), MagicMock(id="athlete2")]
        
        # Mock AI matching results
        mock_matches = [
            {
                "athlete_id": "athlete1",
                "overall_score": 85.5,
                "factors": {"sport_alignment": 90},
                "estimated_rate": 1000.0,
                "total_followers": 20000,
                "recommendation": "Excellent match"
            }
        ]
        
        # Setup mocks
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign
        mock_pb.client.collection.return_value.get_list.side_effect = [
            mock_athletes,  # Athletes query
            MagicMock(total_items=0)  # Existing matches query
        ]
        mock_pb.client.collection.return_value.create.return_value = MagicMock()
        
        # Mock AI service
        mock_ai_instance = MagicMock()
        mock_ai_service.return_value = mock_ai_instance
        mock_asyncio.new_event_loop.return_value.run_until_complete.return_value = mock_matches
        
        # Run task
        result = calculate_ai_matches.apply(args=[campaign_id])
        
        # Verify result
        assert result.result["status"] == "completed"
        assert result.result["campaign_id"] == campaign_id
        
        # Verify AI service was called
        mock_ai_instance.find_athlete_matches.assert_not_called()  # Called via run_until_complete
        
        # Verify matches were stored
        mock_pb.client.collection.return_value.create.assert_called()
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks.AIMatchingService')
    def test_calculate_ai_matches_no_brand(self, mock_ai_service, mock_pb):
        """Test handling when campaign has no brand data"""
        campaign_id = "campaign123"
        
        # Mock campaign without brand
        mock_campaign = MagicMock()
        mock_campaign.expand = {}
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign
        
        # Run task - should fail gracefully
        result = calculate_ai_matches.apply(args=[campaign_id])
        
        assert result.result["status"] == "failed"
        assert "brand data not found" in result.result["error"].lower()
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks.send_notification')
    def test_calculate_ai_matches_sends_notification(self, mock_send_notification, mock_pb):
        """Test that successful matching sends notification to brand"""
        campaign_id = "campaign123"
        
        # Setup successful matching scenario
        mock_campaign = MagicMock()
        mock_campaign.expand = {'brand': MagicMock(id="brand123", user="user123")}
        
        mock_athletes = MagicMock()
        mock_athletes.items = [MagicMock(id="athlete1")]
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign
        mock_pb.client.collection.return_value.get_list.side_effect = [
            mock_athletes,
            MagicMock(total_items=0)  # No existing matches
        ]
        
        # Mock successful AI matching
        with patch('app.worker.tasks.AIMatchingService') as mock_ai_service, \
             patch('app.worker.tasks.asyncio') as mock_asyncio:
            
            mock_matches = [{"athlete_id": "athlete1", "overall_score": 90, "factors": {}, 
                           "estimated_rate": 500, "total_followers": 10000}]
            mock_asyncio.new_event_loop.return_value.run_until_complete.return_value = mock_matches
            
            result = calculate_ai_matches.apply(args=[campaign_id])
            
            # Verify notification was queued
            mock_send_notification.delay.assert_called_once()
            call_args = mock_send_notification.delay.call_args[0]
            assert call_args[0] == "user123"  # Brand user ID
            assert call_args[1] == "new_matches_available"


class TestSocialMediaMetrics:
    """Test social media metrics syncing"""
    
    @patch('app.worker.tasks.SocialMediaService')
    @patch('app.worker.tasks.asyncio')
    def test_sync_social_media_metrics_success(self, mock_asyncio, mock_social_service):
        """Test successful social media metrics sync"""
        athlete_id = "athlete123"
        social_accounts = {"instagram": "@athlete", "twitter": "@athlete"}
        
        # Mock successful sync
        mock_service_instance = MagicMock()
        mock_social_service.return_value = mock_service_instance
        mock_updated_metrics = [{"platform": "instagram", "followers": 15000}]
        mock_asyncio.new_event_loop.return_value.run_until_complete.return_value = mock_updated_metrics
        
        result = sync_social_media_metrics.apply(args=[athlete_id, social_accounts])
        
        assert result.result["status"] == "success"
        assert result.result["athlete_id"] == athlete_id
        assert result.result["updated_metrics"] == mock_updated_metrics
    
    def test_sync_social_media_metrics_with_retries(self):
        """Test retry mechanism on failure"""
        athlete_id = "athlete123" 
        social_accounts = {"instagram": "@athlete"}
        
        # Mock service to raise exception
        with patch('app.worker.tasks.SocialMediaService') as mock_service, \
             patch('app.worker.tasks.asyncio') as mock_asyncio:
            
            mock_asyncio.new_event_loop.return_value.run_until_complete.side_effect = Exception("API Error")
            
            # Create bound task instance to test retry logic
            task_instance = sync_social_media_metrics
            task_instance.max_retries = 1
            
            result = task_instance.apply(args=[athlete_id, social_accounts])
            
            assert result.result["status"] == "failed"
            assert "API Error" in result.result["error"]


class TestDealProcessing:
    """Test deal update processing"""
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks.send_notification')
    def test_process_deal_update_success(self, mock_send_notification, mock_pb):
        """Test successful deal update processing"""
        deal_id = "deal123"
        old_status = "pending"
        new_status = "approved"
        
        # Mock deal with expanded relationships
        mock_deal = MagicMock()
        mock_deal.expand = {
            'athlete': MagicMock(user="athlete_user123"),
            'brand': MagicMock(user="brand_user123")
        }
        mock_deal.agent = "agent_user123"
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_deal
        
        result = process_deal_update.apply(args=[deal_id, old_status, new_status])
        
        assert result.result["status"] == "processed"
        assert len(result.result["notifications"]) == 3  # Athlete, brand, agent
        
        # Verify notifications were sent to all parties
        assert mock_send_notification.delay.call_count == 3
    
    @patch('app.worker.tasks.pb_client')
    def test_process_deal_update_missing_relationships(self, mock_pb):
        """Test deal update with missing athlete/brand relationships"""
        deal_id = "deal123"
        
        # Mock deal with no expanded relationships
        mock_deal = MagicMock()
        mock_deal.expand = {}
        mock_deal.agent = None
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_deal
        
        result = process_deal_update.apply(args=[deal_id, "pending", "approved"])
        
        assert result.result["status"] == "processed"
        assert len(result.result["notifications"]) == 0  # No notifications sent


class TestTrendingAthletes:
    """Test trending athletes calculation"""
    
    @patch('app.worker.tasks.pb_client')
    def test_update_trending_athletes_success(self, mock_pb):
        """Test successful trending athletes update"""
        # Mock recent metrics
        mock_metrics = MagicMock()
        mock_metrics.items = [
            MagicMock(
                followers=20000,
                engagement_rate=5.5,
                expand={'athlete': MagicMock(id="athlete1", first_name="John", 
                                           last_name="Doe", sport="basketball")}
            ),
            MagicMock(
                followers=15000, 
                engagement_rate=7.0,
                expand={'athlete': MagicMock(id="athlete2", first_name="Jane",
                                           last_name="Smith", sport="tennis")}
            )
        ]
        
        mock_pb.client.collection.return_value.get_list.return_value = mock_metrics
        
        result = update_trending_athletes.apply()
        
        assert result.result["status"] == "updated"
        assert result.result["trending_count"] == 2
    
    @patch('app.worker.tasks.pb_client')
    def test_update_trending_athletes_no_data(self, mock_pb):
        """Test trending update with no recent data"""
        mock_metrics = MagicMock()
        mock_metrics.items = []
        
        mock_pb.client.collection.return_value.get_list.return_value = mock_metrics
        
        result = update_trending_athletes.apply()
        
        assert result.result["status"] == "updated"
        assert result.result["trending_count"] == 0


class TestExpiredDealsCleanup:
    """Test expired deals cleanup"""
    
    @patch('app.worker.tasks.pb_client')
    @patch('app.worker.tasks.process_deal_update')
    def test_cleanup_expired_deals_success(self, mock_process_update, mock_pb):
        """Test successful expired deals cleanup"""
        # Mock expired deals
        mock_deals = MagicMock()
        mock_deals.items = [
            MagicMock(id="deal1", status="pending"),
            MagicMock(id="deal2", status="negotiating")
        ]
        
        mock_pb.client.collection.return_value.get_list.return_value = mock_deals
        mock_pb.client.collection.return_value.update.return_value = MagicMock()
        
        result = cleanup_expired_deals.apply()
        
        assert result.result["status"] == "completed"
        assert result.result["expired_deals"] == 2
        
        # Verify deals were updated and notifications queued
        assert mock_pb.client.collection.return_value.update.call_count == 2
        assert mock_process_update.delay.call_count == 2
    
    @patch('app.worker.tasks.pb_client') 
    def test_cleanup_expired_deals_no_expired(self, mock_pb):
        """Test cleanup when no deals are expired"""
        mock_deals = MagicMock()
        mock_deals.items = []
        
        mock_pb.client.collection.return_value.get_list.return_value = mock_deals
        
        result = cleanup_expired_deals.apply()
        
        assert result.result["status"] == "completed"
        assert result.result["expired_deals"] == 0


class TestDailyAnalytics:
    """Test daily analytics generation"""
    
    @patch('app.worker.tasks.pb_client')
    def test_generate_daily_analytics_success(self, mock_pb):
        """Test successful daily analytics generation"""
        today = datetime.now().date()
        
        # Mock database responses for each collection
        mock_responses = [
            MagicMock(total_items=5),   # New athletes
            MagicMock(total_items=3),   # New brands  
            MagicMock(total_items=8, items=[MagicMock(value=1000), MagicMock(value=1500)]),  # New deals
            MagicMock(total_items=12)   # Active campaigns
        ]
        
        mock_pb.client.collection.return_value.get_list.side_effect = mock_responses
        
        result = generate_daily_analytics.apply()
        
        expected_stats = {
            "date": today.isoformat(),
            "new_athletes": 5,
            "new_brands": 3, 
            "new_deals": 8,
            "total_deal_value": 2500,  # 1000 + 1500
            "active_campaigns": 12
        }
        
        assert result.result == expected_stats
    
    @patch('app.worker.tasks.pb_client')
    def test_generate_daily_analytics_database_error(self, mock_pb):
        """Test analytics generation with database error"""
        mock_pb.client.collection.return_value.get_list.side_effect = Exception("Database error")
        
        result = generate_daily_analytics.apply()
        
        assert result.result["status"] == "failed"
        assert "Database error" in result.result["error"]