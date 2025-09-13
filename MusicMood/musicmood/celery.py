import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicmood.settings")
app = Celery("musicmood")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
