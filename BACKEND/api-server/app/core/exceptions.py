from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog
from typing import Dict, Any

logger = structlog.get_logger()

class PlayRightException(Exception):
    """Base exception class for PlayRight application"""
    def __init__(self, message: str, error_code: str = None, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)

class AuthenticationError(PlayRightException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR", 401)

class AuthorizationError(PlayRightException):
    """Authorization related errors"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHZ_ERROR", 403)

class ValidationError(PlayRightException):
    """Data validation errors"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR", 422)

class NotFoundError(PlayRightException):
    """Resource not found errors"""
    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, "NOT_FOUND", 404)

class ConflictError(PlayRightException):
    """Resource conflict errors"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, "CONFLICT_ERROR", 409)

class ExternalServiceError(PlayRightException):
    """External service integration errors"""
    def __init__(self, service: str, message: str = None):
        msg = message or f"{service} service unavailable"
        super().__init__(msg, "EXTERNAL_SERVICE_ERROR", 502)

class RateLimitError(PlayRightException):
    """Rate limiting errors"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR", 429)

class AIProcessingError(PlayRightException):
    """AI/ML processing errors"""
    def __init__(self, message: str = "AI processing failed"):
        super().__init__(message, "AI_ERROR", 500)

# Exception handlers
async def playright_exception_handler(request: Request, exc: PlayRightException):
    """Handle custom PlayRight exceptions"""
    logger.error("PlayRight exception occurred",
                error_code=exc.error_code,
                message=exc.message,
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code or "UNKNOWN_ERROR",
            "message": exc.message,
            "path": request.url.path,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.error("Validation error occurred",
                path=request.url.path,
                errors=exc.errors())
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": exc.errors(),
            "path": request.url.path,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.error("HTTP exception occurred",
                status_code=exc.status_code,
                detail=exc.detail,
                path=request.url.path)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "path": request.url.path,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error("Unexpected exception occurred",
                exception_type=type(exc).__name__,
                message=str(exc),
                path=request.url.path,
                method=request.method)
    
    # Don't expose internal errors in production
    message = "Internal server error"
    if logger.isEnabledFor(structlog.DEBUG):
        message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": message,
            "path": request.url.path,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )