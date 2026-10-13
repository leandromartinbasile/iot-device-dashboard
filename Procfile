web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn myproject.wsgi --log-file -
worker: celery -A myproject worker --loglevel=info
