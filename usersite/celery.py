import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usersite.settings')

app = Celery('usersite')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()