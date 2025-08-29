import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth import AuthService

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_athlete(self, client: TestClient):
        """Test athlete registration"""
        user_data = {
            "email": "test.athlete@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "athlete",
            "first_name": "Test",
            "last_name": "Athlete"
        }
        
        with patch('app.services.auth.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "id": "test_user_id",
                "email": "test.athlete@example.com",
                "role": "athlete"
            }
            
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201
    
    def test_register_brand(self, client: TestClient):
        """Test brand registration"""
        user_data = {
            "email": "test.brand@example.com",
            "password": "securepass123", 
            "password_confirm": "securepass123",
            "role": "brand",
            "first_name": "Test",
            "last_name": "Brand"
        }
        
        with patch('app.services.auth.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "id": "test_brand_id",
                "email": "test.brand@example.com",
                "role": "brand"
            }
            
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        credentials = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        with patch('app.services.auth.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            response = client.post("/api/auth/login", json=credentials)
            assert response.status_code == 401
    
    def test_password_mismatch(self, client: TestClient):
        """Test registration with password mismatch"""
        user_data = {
            "email": "test@example.com",
            "password": "password1",
            "password_confirm": "password2",
            "role": "athlete"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_login_success(self, client: TestClient):
        """Test successful login"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('app.services.auth.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "token": "test_jwt_token",
                "user": {
                    "id": "test_user_id",
                    "email": "test@example.com",
                    "role": "athlete"
                }
            }
            
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert data["user"]["email"] == "test@example.com"

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