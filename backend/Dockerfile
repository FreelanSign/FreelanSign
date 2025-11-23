# backend/Dockerfile

# Builder stage
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

# Install Playwright browsers and dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium


COPY . /app/

# Create a non-root user
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
RUN chown -R app:app /ms-playwright

USER app

EXPOSE 8000

# Entrypoint script to handle migrations and static files
COPY --chown=app:app <<EOF /entrypoint.sh
#!/bin/sh
set -e

# Wait for postgres (optional, handled by depends_on usually but good practice)
# until pg_isready -h \$DATABASE_HOST -p \$DATABASE_PORT -U \$DATABASE_USER; do
#   echo "Waiting for postgres..."
#   sleep 2
# done

if [ "\$1" = 'gunicorn' ]; then
    python manage.py migrate
    python manage.py collectstatic --noinput
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60 --max-requests 1000 --max-requests-jitter 50
fi

exec "\$@"
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn"]
