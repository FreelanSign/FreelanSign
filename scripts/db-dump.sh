#!/bin/bash

# Script pour dumper la base de données
# Usage: ./scripts/db-dump.sh [docker|local]

ENV=${1:-docker}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_DIR="database/dumps"

mkdir -p $DUMP_DIR

if [ "$ENV" == "docker" ]; then
    echo "Création d'un dump depuis Docker..."
    # On utilise l'utilisateur et la base définis dans le docker-compose
    docker exec -t freelansign_postgres_prod pg_dump -U fs_user -d freelansign --clean --if-exists > "$DUMP_DIR/dump_docker_$TIMESTAMP.sql"
    echo "Dump créé : $DUMP_DIR/dump_docker_$TIMESTAMP.sql"
elif [ "$ENV" == "local" ]; then
    echo "Création d'un dump depuis l'environnement local..."
    # Assurez-vous que pg_dump est installé et accessible
    # On suppose que les credentials sont dans .env ou accessibles via ~/.pgpass
    # Ou on utilise les valeurs par défaut
    pg_dump -U fs_user -d freelansign --clean --if-exists > "$DUMP_DIR/dump_local_$TIMESTAMP.sql"
    echo "Dump créé : $DUMP_DIR/dump_local_$TIMESTAMP.sql"
else
    echo "Environnement inconnu : $ENV"
    echo "Usage: $0 [docker|local]"
    exit 1
fi
