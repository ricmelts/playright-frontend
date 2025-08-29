import structlog
import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configure structured logging for the application"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_timestamp,
        add_correlation_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add file output if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(file_handler)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Use colored output for console
        if sys.stdout.isatty():
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def add_timestamp(logger, method_name, event_dict):
    """Add ISO timestamp to log entries"""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID for request tracing"""
    # This would typically come from request context
    # For now, we'll use a simple approach
    import uuid
    if "correlation_id" not in event_dict:
        event_dict["correlation_id"] = str(uuid.uuid4())[:8]
    return event_dict

class PlayRightLogger:
    """Custom logger with PlayRight-specific functionality"""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
        self.name = name
    
    def log_api_request(self, method: str, path: str, user_id: str = None, **kwargs):
        """Log API request with standard format"""
        self.logger.info(
            "API request",
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )
    
    def log_api_response(self, method: str, path: str, status_code: int, 
                        response_time_ms: float, **kwargs):
        """Log API response with standard format"""
        self.logger.info(
            "API response", 
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            **kwargs
        )
    
    def log_ai_operation(self, operation: str, athlete_id: str = None, 
                        brand_id: str = None, score: float = None, **kwargs):
        """Log AI operations with standard format"""
        self.logger.info(
            "AI operation",
            operation=operation,
            athlete_id=athlete_id,
            brand_id=brand_id,
            score=score,
            **kwargs
        )
    
    def log_social_media_sync(self, athlete_id: str, platform: str, 
                             success: bool, followers: int = None, **kwargs):
        """Log social media sync operations"""
        self.logger.info(
            "Social media sync",
            athlete_id=athlete_id,
            platform=platform,
            success=success,
            followers=followers,
            **kwargs
        )
    
    def log_deal_event(self, deal_id: str, event: str, old_status: str = None, 
                      new_status: str = None, **kwargs):
        """Log deal lifecycle events"""
        self.logger.info(
            "Deal event",
            deal_id=deal_id,
            event=event,
            old_status=old_status,
            new_status=new_status,
            **kwargs
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with additional context"""
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        
        if context:
            error_context.update(context)
        
        self.logger.error("Error occurred", **error_context)
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              unit: str = "ms", **kwargs):
        """Log performance metrics"""
        self.logger.info(
            "Performance metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **kwargs
        )

# Global logger instances
api_logger = PlayRightLogger("playright.api")
ai_logger = PlayRightLogger("playright.ai") 
worker_logger = PlayRightLogger("playright.worker")

# Utility functions
def get_logger(name: str = None) -> PlayRightLogger:
    """Get a logger instance"""
    return PlayRightLogger(name or "playright")

def log_function_call(func_name: str, **kwargs):
    """Decorator to log function calls"""
    def decorator(func):
        async def wrapper(*args, **wrapper_kwargs):
            start_time = datetime.now()
            logger = get_logger()
            
            try:
                logger.logger.debug(
                    "Function call started",
                    function=func_name,
                    args_count=len(args),
                    kwargs_keys=list(wrapper_kwargs.keys()),
                    **kwargs
                )
                
                result = await func(*args, **wrapper_kwargs)
                
                end_time = datetime.now()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                logger.logger.debug(
                    "Function call completed",
                    function=func_name,
                    duration_ms=round(duration_ms, 2),
                    **kwargs
                )
                
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                logger.log_error_with_context(e, {
                    "function": func_name,
                    "duration_ms": round(duration_ms, 2),
                    **kwargs
                })
                raise
        
        return wrapper
    return decorator