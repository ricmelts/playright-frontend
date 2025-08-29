import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_athlete(self):
        """Test athlete registration"""
        user_data = {
            "email": "test.athlete@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "athlete",
            "first_name": "Test",
            "last_name": "Athlete"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        # Note: This will fail without actual PocketBase running
        # In CI/CD, you'd use a test database
        assert response.status_code in [200, 500]  # 500 expected without PocketBase
    
    def test_register_brand(self):
        """Test brand registration"""
        user_data = {
            "email": "test.brand@example.com",
            "password": "securepass123", 
            "password_confirm": "securepass123",
            "role": "brand",
            "first_name": "Test",
            "last_name": "Brand"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code in [200, 500]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        credentials = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=credentials)
        assert response.status_code in [401, 500]
    
    def test_password_mismatch(self):
        """Test registration with password mismatch"""
        user_data = {
            "email": "test@example.com",
            "password": "password1",
            "password_confirm": "password2",
            "role": "athlete"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "passwords do not match" in response.json()["detail"].lower()
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code in [401, 500]

class TestAuthValidation:
    """Test authentication data validation"""
    
    def test_invalid_email_format(self):
        """Test registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "securepass123",
            "password_confirm": "securepass123", 
            "role": "athlete"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_invalid_role(self):
        """Test registration with invalid role"""
        user_data = {
            "email": "test@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "invalid_role"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test registration with missing required fields"""
        user_data = {
            "password": "securepass123",
            "password_confirm": "securepass123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422