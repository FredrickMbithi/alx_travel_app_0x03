web: gunicorn alx_travel_app.wsgi --log-file -
worker: celery -A alx_travel_app worker --loglevel=info
release: python alx_travel_app/manage.py migrate --noinput
