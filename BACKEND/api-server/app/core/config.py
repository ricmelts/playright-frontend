from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Server Configuration
    PORT: int = 3001
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*.playright.ai"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://app.playright.ai"]
    
    # PocketBase Configuration
    POCKETBASE_URL: str = "http://localhost:8090"
    POCKETBASE_ADMIN_EMAIL: str = "admin@playright.ai"
    POCKETBASE_ADMIN_PASSWORD: str = "admin-password"
    
    # AI Service Configuration
    AI_ENGINE_URL: str = "http://localhost:8000"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Social Media APIs
    INSTAGRAM_CLIENT_ID: Optional[str] = None
    INSTAGRAM_CLIENT_SECRET: Optional[str] = None
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Payment Processing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Email Service
    EMAIL_SERVICE: str = "sendgrid"
    EMAIL_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@playright.ai"
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "playright-uploads"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # AI Model Configuration
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MATCHING_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()