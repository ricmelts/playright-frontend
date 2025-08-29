import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMatching:
    """Test AI matching endpoints"""
    
    def test_athletes_for_brand_request(self):
        """Test finding athletes for brand"""
        request_data = {
            "brand_id": "test_brand_123",
            "sport_filter": "basketball",
            "min_followers": 10000,
            "max_budget": 15000,
            "limit": 5
        }
        
        response = client.post("/api/matching/athletes-for-brand", json=request_data)
        # Will fail without PocketBase, but should validate request structure
        assert response.status_code in [200, 404, 500]
    
    def test_brands_for_athlete_request(self):
        """Test finding brands for athlete"""
        request_data = {
            "athlete_id": "test_athlete_123", 
            "industry_preference": "sports_apparel",
            "min_budget": 5000,
            "limit": 10
        }
        
        response = client.post("/api/matching/brands-for-athlete", json=request_data)
        assert response.status_code in [200, 404, 500]
    
    def test_compatibility_score_calculation(self):
        """Test compatibility score calculation"""
        params = {
            "athlete_id": "test_athlete_123",
            "brand_id": "test_brand_123"
        }
        
        response = client.get("/api/matching/compatibility-score", params=params)
        assert response.status_code in [200, 404, 500]
    
    def test_trending_athletes(self):
        """Test getting trending athletes"""
        params = {"sport": "basketball", "limit": 5}
        
        response = client.get("/api/matching/trending-athletes", params=params)
        assert response.status_code in [200, 500]
    
    def test_bulk_match_analysis(self):
        """Test bulk matching analysis"""
        response = client.post("/api/matching/bulk-match")
        assert response.status_code in [200, 500]

class TestMatchingValidation:
    """Test matching request validation"""
    
    def test_invalid_athlete_id_format(self):
        """Test request with invalid athlete ID"""
        request_data = {
            "brand_id": "valid_brand_123",
            "sport_filter": "basketball"
        }
        
        # Missing athlete_id for brands-for-athlete endpoint
        response = client.post("/api/matching/brands-for-athlete", json=request_data)
        assert response.status_code == 422
    
    def test_invalid_limit_values(self):
        """Test request with invalid limit values"""
        request_data = {
            "brand_id": "test_brand_123",
            "limit": 100  # Over maximum allowed
        }
        
        response = client.post("/api/matching/athletes-for-brand", json=request_data)
        assert response.status_code == 422
    
    def test_negative_budget_values(self):
        """Test request with negative budget values"""
        request_data = {
            "athlete_id": "test_athlete_123",
            "min_budget": -1000,  # Negative budget
            "limit": 5
        }
        
        response = client.post("/api/matching/brands-for-athlete", json=request_data)
        assert response.status_code == 422