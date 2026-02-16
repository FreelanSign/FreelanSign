web: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
release: cd backend && python manage.py migrate --noinput
