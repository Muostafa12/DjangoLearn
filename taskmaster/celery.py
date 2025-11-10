"""
Celery configuration for taskmaster project.
This allows us to run asynchronous tasks like sending emails,
processing notifications, and other background jobs.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')

app = Celery('taskmaster')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'send-daily-task-reminders': {
        'task': 'taskmaster.tasks.tasks.send_daily_task_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    'cleanup-old-notifications': {
        'task': 'taskmaster.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')
