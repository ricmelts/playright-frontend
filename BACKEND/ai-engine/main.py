from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.matching import router as matching_router
from api.analytics import router as analytics_router
from api.training import router as training_router

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🤖 Starting PlayRight AI Engine")
    
    # Pre-load ML models
    try:
        from models.embedding_model import EmbeddingModel
        EmbeddingModel.load_model()
        logger.info("✅ ML models loaded successfully")
    except Exception as e:
        logger.error("❌ Failed to load ML models", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down PlayRight AI Engine")

# Create FastAPI app
app = FastAPI(
    title="PlayRight AI Engine",
    description="Machine Learning and AI services for NIL deals matching",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # API server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check if models are loaded
        from models.embedding_model import EmbeddingModel
        model_status = "healthy" if EmbeddingModel.is_loaded() else "loading"
        
        return {
            "status": "healthy",
            "models": model_status,
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}

# Include routers
app.include_router(matching_router, prefix="/matching", tags=["AI Matching"])
app.include_router(analytics_router, prefix="/analytics", tags=["AI Analytics"])
app.include_router(training_router, prefix="/training", tags=["Model Training"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("AI Engine unhandled exception", error=str(exc), path=request.url.path)
    return {"error": "AI processing error", "message": str(exc)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)