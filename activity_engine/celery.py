from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'activity_engine.settings')

app = Celery('activity_engine')

app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print ('Request: {0!r}'.format(self.request))