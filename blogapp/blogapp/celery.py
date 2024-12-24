from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the correct settings path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp.settings')
app = Celery('blogapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['blogapp'])  # Ensure 'blogapp' is specified here
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp.settings')
