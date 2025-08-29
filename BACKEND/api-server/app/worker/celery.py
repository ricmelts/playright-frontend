from celery import Celery
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Initialize Celery
celery = Celery(
    'playright_worker',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.worker.tasks']
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_routes={
        'app.worker.tasks.sync_social_media_metrics': {'queue': 'social_media'},
        'app.worker.tasks.calculate_ai_matches': {'queue': 'ai_processing'},
        'app.worker.tasks.send_notification': {'queue': 'notifications'},
        'app.worker.tasks.process_deal_update': {'queue': 'deals'},
    },
    beat_schedule={
        'sync-all-athlete-metrics': {
            'task': 'app.worker.tasks.sync_all_athlete_metrics',
            'schedule': 3600.0,  # Every hour
        },
        'update-trending-athletes': {
            'task': 'app.worker.tasks.update_trending_athletes',
            'schedule': 1800.0,  # Every 30 minutes
        },
        'cleanup-expired-deals': {
            'task': 'app.worker.tasks.cleanup_expired_deals',
            'schedule': 86400.0,  # Daily
        },
        'generate-daily-analytics': {
            'task': 'app.worker.tasks.generate_daily_analytics',
            'schedule': 86400.0,  # Daily at midnight
        }
    }
)