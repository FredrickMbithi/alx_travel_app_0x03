# Running Celery + RabbitMQ (dev notes)

This companion README explains how I started RabbitMQ, Django and Celery when testing in this workspace.

From project root (/home/ghost/alx_travel_app_0x03):

1. Activate venv

```bash
source venv/bin/activate
```

2. Apply migrations and start Django

```bash
cd alx_travel_app
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

3. Start RabbitMQ (system or docker). Example (docker):

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

4. Start Celery worker (dev: console email backend)

```bash
cd alx_travel_app
# prints emails to celery stdout
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend celery -A alx_travel_app worker --loglevel=info
```

5. Quick test

- From another terminal (with venv active):

```bash
python manage.py shell
>>> from listings.tasks import test_celery_task
>>> test_celery_task.delay()
```

- Or run the included test script: `/alx_travel_app/tmp_booking_test.py` to create a booking and dispatch `send_booking_confirmation_email`.

Notes

- For real email sending, set `EMAIL_BACKEND`, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in the `.env` file and restart Celery without the console override.
- The Celery app is configured in `alx_travel_app/celery.py` and tasks are defined in `listings/tasks.py`.
