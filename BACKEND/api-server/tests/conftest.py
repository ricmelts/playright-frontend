import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from app.core.config import get_settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.testing = True
    settings.pocketbase_url = "http://localhost:8090"
    return settings

@pytest.fixture
def sample_athlete_data():
    """Sample athlete data for testing."""
    return {
        "name": "Test Athlete",
        "sport": "basketball",
        "position": "guard",
        "year": "junior",
        "university": "Test University",
        "social_followers": 10000,
        "engagement_rate": 0.05,
        "niche": "sports performance"
    }

@pytest.fixture
def sample_brand_data():
    """Sample brand data for testing."""
    return {
        "name": "Test Brand",
        "industry": "fitness",
        "budget_range": "5000-15000",
        "target_demographics": "18-25",
        "marketing_goals": "brand awareness",
        "preferred_sports": ["basketball", "football"]
    }

@pytest.fixture
def sample_deal_data():
    """Sample deal data for testing."""
    return {
        "title": "Test NIL Deal",
        "athlete_id": "test_athlete_id",
        "brand_id": "test_brand_id",
        "value": 10000,
        "status": "pending",
        "deliverables": ["social media posts", "appearance"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }

@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }