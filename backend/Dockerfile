# backend/Dockerfile

# Builder stage
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libpango1.0-dev \
    libcairo2-dev \
    libgdk-pixbuf-2.0-dev \
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
    cron \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*


COPY . /app/

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Install gosu for dropping privileges
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Create directories that will be mounted as volumes
RUN mkdir -p /app/logs /app/static /app/media && \
    chown -R app:app /app

EXPOSE 8000

# Entrypoint script to handle migrations and static files
COPY <<EOF /entrypoint.sh
#!/bin/sh
set -e

# Fix permissions for volumes (run as root, then drop to app user)
chown -R app:app /app/logs /app/static /app/media 2>/dev/null || true

if [ "\$1" = 'gunicorn' ]; then
    gosu app python manage.py migrate
    gosu app python manage.py collectstatic --noinput
    exec gosu app gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60 --max-requests 1000 --max-requests-jitter 50
fi

exec gosu app "\$@"
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn"]
