import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from app.services.ai_matching import AIMatchingService


class TestAudienceDemographics:
    """Test audience demographics calculation"""
    
    def setup_method(self):
        self.ai_service = AIMatchingService()
    
    def test_age_group_matching(self):
        """Test age group compatibility scoring"""
        athlete_data = {"age": 22, "sport": "basketball", "bio": "College athlete"}
        brand_data = {"target_demographics": {"age_group": "18_24"}}
        athlete_metrics = [{"followers": 10000, "engagement_rate": 5.0}]
        
        score = self.ai_service._calculate_audience_demographics_score(
            athlete_data, brand_data, athlete_metrics
        )
        
        # Should get high score for exact age group match
        assert score >= 80
    
    def test_age_group_distance(self):
        """Test age group distance calculation"""
        # Exact match
        distance = self.ai_service._age_group_distance("25_34", "25_34")
        assert distance == 0
        
        # Adjacent groups
        distance = self.ai_service._age_group_distance("18_24", "25_34")
        assert distance == 1
        
        # Distant groups
        distance = self.ai_service._age_group_distance("under_18", "45_plus")
        assert distance == 4
    
    def test_gender_matching(self):
        """Test gender compatibility"""
        athlete_data = {"gender": "female", "age": 25, "sport": "tennis"}
        brand_data = {"target_demographics": {"gender": "female"}}
        athlete_metrics = [{"followers": 5000, "engagement_rate": 3.0}]
        
        score = self.ai_service._calculate_audience_demographics_score(
            athlete_data, brand_data, athlete_metrics
        )
        
        assert score >= 70  # Should get good score for gender match
    
    def test_interest_alignment(self):
        """Test interest-based matching"""
        athlete_data = {
            "sport": "basketball", 
            "bio": "Love fitness and healthy lifestyle",
            "age": 23
        }
        brand_data = {
            "target_demographics": {
                "interests": ["basketball", "fitness", "health"]
            }
        }
        athlete_metrics = [{"followers": 8000, "engagement_rate": 4.0}]
        
        score = self.ai_service._calculate_audience_demographics_score(
            athlete_data, brand_data, athlete_metrics
        )
        
        # Should get high score for multiple interest matches
        assert score >= 85
    
    def test_income_level_matching(self):
        """Test income/lifestyle compatibility"""
        athlete_data = {"age": 26, "sport": "golf"}
        brand_data = {"target_demographics": {"income_level": "high"}}
        athlete_metrics = [{"followers": 500000, "engagement_rate": 6.0}]  # High influence
        
        score = self.ai_service._calculate_audience_demographics_score(
            athlete_data, brand_data, athlete_metrics
        )
        
        assert score >= 75  # High follower count should match high income target
    
    def test_no_demographics_default(self):
        """Test default score when no demographics specified"""
        athlete_data = {"age": 25, "sport": "soccer"}
        brand_data = {}  # No target demographics
        athlete_metrics = [{"followers": 1000, "engagement_rate": 2.0}]
        
        score = self.ai_service._calculate_audience_demographics_score(
            athlete_data, brand_data, athlete_metrics
        )
        
        assert score == 70  # Should return default score


class TestBrandSafety:
    """Test brand safety scoring"""
    
    def setup_method(self):
        self.ai_service = AIMatchingService()
    
    def test_clean_profile_high_score(self):
        """Test clean profile gets high brand safety score"""
        athlete_data = {
            "first_name": "John",
            "last_name": "Doe", 
            "sport": "tennis",
            "school": "State University",
            "bio": "Dedicated tennis player focused on excellence",
            "verified": True
        }
        athlete_metrics = [{"followers": 15000, "engagement_rate": 5.0}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert score >= 95  # Should get near perfect score
    
    def test_red_flag_keywords_penalty(self):
        """Test red flag keywords reduce safety score"""
        athlete_data = {
            "first_name": "John",
            "last_name": "Doe",
            "sport": "football", 
            "bio": "Had some controversy last year but moved past it",
            "verified": False
        }
        athlete_metrics = [{"followers": 20000, "engagement_rate": 4.0}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert score < 80  # Should be penalized for "controversy"
    
    def test_moderate_risk_keywords(self):
        """Test moderate risk keywords have smaller penalty"""
        athlete_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "sport": "basketball",
            "bio": "Love to party and have fun with friends",
            "verified": True
        }
        athlete_metrics = [{"followers": 12000, "engagement_rate": 6.0}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert 80 <= score < 95  # Moderate penalty for "party"
    
    def test_fake_engagement_detection(self):
        """Test detection of potentially fake engagement"""
        athlete_data = {
            "first_name": "Test",
            "last_name": "User",
            "sport": "soccer",
            "bio": "Soccer player",
            "verified": False
        }
        # Very high engagement with very low followers - suspicious
        athlete_metrics = [{"followers": 500, "engagement_rate": 20.0}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert score < 85  # Should be penalized for suspicious engagement
    
    def test_low_engagement_penalty(self):
        """Test penalty for low engagement on high follower accounts"""
        athlete_data = {
            "first_name": "Popular",
            "last_name": "User",
            "sport": "tennis",
            "bio": "Tennis player",
            "verified": False
        }
        # High followers but very low engagement
        athlete_metrics = [{"followers": 100000, "engagement_rate": 0.5}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert score < 90  # Should be penalized for low engagement
    
    def test_incomplete_profile_penalty(self):
        """Test penalty for incomplete profiles"""
        athlete_data = {
            "first_name": "John",
            # Missing last_name, sport, school, bio
            "verified": False
        }
        athlete_metrics = [{"followers": 5000, "engagement_rate": 3.0}]
        
        score = self.ai_service._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        assert score < 80  # Should be penalized for incomplete profile
    
    def test_verified_account_bonus(self):
        """Test bonus for verified accounts"""
        athlete_data_unverified = {
            "first_name": "John", "last_name": "Doe", "sport": "tennis",
            "school": "University", "bio": "Tennis player", "verified": False
        }
        athlete_data_verified = athlete_data_unverified.copy()
        athlete_data_verified["verified"] = True
        
        athlete_metrics = [{"followers": 10000, "engagement_rate": 4.0}]
        
        score_unverified = self.ai_service._calculate_brand_safety_score(
            athlete_data_unverified, athlete_metrics
        )
        score_verified = self.ai_service._calculate_brand_safety_score(
            athlete_data_verified, athlete_metrics  
        )
        
        assert score_verified > score_unverified  # Verified should score higher


class TestCampaignMatchingLogic:
    """Test campaign matching processing logic"""
    
    @patch('app.services.ai_matching.pb_client')
    async def test_process_campaign_matches_success(self, mock_pb):
        """Test successful campaign matches processing"""
        ai_service = AIMatchingService()
        
        # Mock campaign data
        mock_campaign_record = MagicMock()
        mock_campaign_record.id = "campaign123"
        mock_campaign_record.name = "Test Campaign"
        mock_campaign_record.target_sports = ["basketball"]
        mock_campaign_record.expand = {
            'brand': MagicMock(id="brand123", user="user123", **{"__dict__": {"id": "brand123"}})
        }
        
        # Mock athletes data
        mock_athletes_response = MagicMock()
        mock_athletes_response.items = [
            MagicMock(id="athlete1", **{"__dict__": {"id": "athlete1", "sport": "basketball"}})
        ]
        
        # Mock matching results
        mock_matches = [{
            "athlete_id": "athlete1",
            "overall_score": 85.5,
            "factors": {"sport_alignment": 100},
            "estimated_rate": 500.0,
            "total_followers": 15000
        }]
        
        # Setup mocks
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign_record
        mock_pb.client.collection.return_value.get_list.side_effect = [
            mock_athletes_response,  # Athletes query
            MagicMock(total_items=0)  # Existing matches query
        ]
        mock_pb.client.collection.return_value.create.return_value = MagicMock()
        mock_pb.client.collection.return_value.update.return_value = MagicMock()
        
        # Mock the AI matching method
        with patch.object(ai_service, 'find_athlete_matches', return_value=mock_matches):
            campaign_dict = {"id": "campaign123"}
            await ai_service._process_campaign_matches(campaign_dict)
        
        # Verify database operations were called
        assert mock_pb.client.collection.call_count >= 3  # campaigns, athletes, matches
    
    @patch('app.services.ai_matching.pb_client')
    async def test_process_campaign_matches_no_brand(self, mock_pb):
        """Test handling of campaign with no brand data"""
        ai_service = AIMatchingService()
        
        # Mock campaign without brand data
        mock_campaign_record = MagicMock()
        mock_campaign_record.expand = {}  # No brand data
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign_record
        
        campaign_dict = {"id": "campaign123"}
        
        # Should not raise exception, just log error and return
        await ai_service._process_campaign_matches(campaign_dict)
        
        # Should only call get_one for campaign lookup
        mock_pb.client.collection.return_value.get_one.assert_called_once()
    
    @patch('app.services.ai_matching.pb_client')
    async def test_process_campaign_matches_no_athletes(self, mock_pb):
        """Test handling when no eligible athletes found"""
        ai_service = AIMatchingService()
        
        # Mock campaign with brand but no matching athletes
        mock_campaign_record = MagicMock()
        mock_campaign_record.expand = {
            'brand': MagicMock(id="brand123", **{"__dict__": {"id": "brand123"}})
        }
        
        mock_athletes_response = MagicMock()
        mock_athletes_response.items = []  # No athletes found
        
        mock_pb.client.collection.return_value.get_one.return_value = mock_campaign_record
        mock_pb.client.collection.return_value.get_list.return_value = mock_athletes_response
        
        campaign_dict = {"id": "campaign123"}
        await ai_service._process_campaign_matches(campaign_dict)
        
        # Should return early without processing matches
        # Verify get_list was called for athletes but not for existing matches
        assert mock_pb.client.collection.return_value.get_list.call_count == 1


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def test_complete_compatibility_calculation(self):
        """Test complete compatibility calculation with all factors"""
        ai_service = AIMatchingService()
        
        athlete_data = {
            "id": "athlete123",
            "first_name": "Sarah",
            "last_name": "Johnson", 
            "sport": "tennis",
            "school": "Stanford University",
            "location": "California",
            "age": 21,
            "gender": "female",
            "bio": "Professional tennis player focused on fitness and health",
            "verified": True
        }
        
        brand_data = {
            "id": "brand123",
            "company_name": "FitGear Inc",
            "industry": "Sports Equipment",
            "location": "California",
            "preferred_sports": ["tennis", "fitness"],
            "budget_min": 1000,
            "budget_max": 5000,
            "target_demographics": {
                "age_group": "18_24",
                "gender": "female", 
                "interests": ["tennis", "fitness", "health"],
                "income_level": "medium"
            }
        }
        
        athlete_metrics = [{
            "followers": 25000,
            "engagement_rate": 6.5,
            "platform": "instagram"
        }]
        
        # Calculate all compatibility factors
        factors = ai_service._calculate_compatibility_factors(
            athlete_data, brand_data, athlete_metrics
        )
        
        # All factors should be calculated and reasonably high
        assert factors["sport_alignment"] >= 90  # Tennis matches preferred sports
        assert factors["location_proximity"] >= 90  # Same state
        assert factors["engagement_quality"] >= 75  # Good engagement rate
        assert factors["budget_fit"] >= 70  # Should fit within budget
        assert factors["audience_demographics"] >= 80  # Good demographic match
        assert factors["brand_safety"] >= 90  # Clean, verified profile
        
        # Overall score should be high
        overall_factors = factors.copy()
        semantic_score = 85  # Assume good semantic similarity
        
        weights = {
            "semantic_similarity": 0.3, "sport_alignment": 0.25, "engagement_quality": 0.2,
            "budget_fit": 0.15, "location_proximity": 0.05, "audience_demographics": 0.03,
            "brand_safety": 0.02
        }
        
        overall_score = (
            semantic_score * weights["semantic_similarity"] +
            sum(overall_factors[key] * weights[key] for key in overall_factors.keys() if key in weights)
        )
        
        assert overall_score >= 80  # Should be a strong match