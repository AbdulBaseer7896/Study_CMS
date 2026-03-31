# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyCMS.settings')

# app = Celery('studyCMS')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()



import os
from celery import Celery
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyCMS.settings')
 
app = Celery('studyCMS')
app.config_from_object('django.conf:settings', namespace='CELERY')
 
# Explicitly list task modules so the worker always finds them
app.autodiscover_tasks([
    'myapp.Utils.email_tasks',
])
 