"""
Celery tasks for background processing
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "jasmin_sms_dashboard",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.campaign_tasks",
        "app.tasks.message_tasks",
        "app.tasks.connector_tasks",
        "app.tasks.billing_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    # Campaign processing
    'process-scheduled-campaigns': {
        'task': 'app.tasks.campaign_tasks.process_scheduled_campaigns',
        'schedule': 60.0,  # Every minute
    },
    
    # Message queue processing
    'process-message-queue': {
        'task': 'app.tasks.message_tasks.process_message_queue',
        'schedule': 30.0,  # Every 30 seconds
    },
    
    # Connector monitoring
    'monitor-connectors': {
        'task': 'app.tasks.connector_tasks.monitor_connectors',
        'schedule': 60.0,  # Every minute
    },
    
    # Analytics aggregation
    'aggregate-hourly-analytics': {
        'task': 'app.tasks.analytics_tasks.aggregate_hourly_analytics',
        'schedule': 3600.0,  # Every hour
    },
    
    # Billing processing
    'process-billing-cycles': {
        'task': 'app.tasks.billing_tasks.process_billing_cycles',
        'schedule': 3600.0,  # Every hour
    },
    
    # Maintenance tasks
    'cleanup-old-logs': {
        'task': 'app.tasks.maintenance_tasks.cleanup_old_logs',
        'schedule': 86400.0,  # Daily
    },
    
    # WebSocket connection cleanup
    'cleanup-websocket-connections': {
        'task': 'app.tasks.maintenance_tasks.cleanup_websocket_connections',
        'schedule': 300.0,  # Every 5 minutes
    },
}

# Import all task modules to register them
from . import (
    campaign_tasks,
    message_tasks,
    connector_tasks,
    billing_tasks,
    analytics_tasks,
    maintenance_tasks
)

__all__ = [
    "celery_app",
    "campaign_tasks",
    "message_tasks", 
    "connector_tasks",
    "billing_tasks",
    "analytics_tasks",
    "maintenance_tasks"
]