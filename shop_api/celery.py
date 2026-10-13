import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.beat import crontab

app.conf.beat_schedule = {
    "delete-unactive-users": {
        "task": "users.tasks.delete_unactive_users",
        "schedule": crontab(minute=0, hour=3),
    },
    "daily-user-report": {
        "task": "users.tasks.send_daily_report_email",
        "schedule": crontab(minute=30, hour=9),
    },
}
