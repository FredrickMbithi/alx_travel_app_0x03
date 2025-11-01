import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','alx_travel_app.settings')
django.setup()
from listings.tasks import test_celery_task
r = test_celery_task.delay()
print('Dispatched', r.id)
