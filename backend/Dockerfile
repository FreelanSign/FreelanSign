# backend/Dockerfile
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . /app/

# Port d'exposition
EXPOSE 8000

# Commande par défaut (sera overridée par docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
