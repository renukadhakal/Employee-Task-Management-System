from datetime import timedelta
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ETMS.settings")

app = Celery("ETMS")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.worker_pool_restarts = True
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "send_task_notifications": {
        "task": "task.tasks.send_task_notifications",
        "schedule": timedelta(seconds=10),
    },
}
