#!/bin/bash

# Script pour restaurer la base de données
# Usage: ./scripts/db-restore.sh <fichier_dump> [docker|local]

DUMP_FILE=$1
ENV=${2:-docker}

if [ -z "$DUMP_FILE" ]; then
    echo "Erreur : Aucun fichier de dump spécifié."
    echo "Usage: $0 <fichier_dump> [docker|local]"
    exit 1
fi

if [ ! -f "$DUMP_FILE" ]; then
    echo "Erreur : Le fichier $DUMP_FILE n'existe pas."
    exit 1
fi

if [ "$ENV" == "docker" ]; then
    echo "Restauration vers Docker depuis $DUMP_FILE..."
    # On arrête le backend pour éviter les conflits de connexion si nécessaire,
    # mais ici on suppose qu'on peut restaurer à chaud ou que l'utilisateur a géré ça.
    # L'option --clean dans le dump devrait gérer le drop des tables.
    cat "$DUMP_FILE" | docker exec -i freelansign_postgres_prod psql -U fs_user -d freelansign
    echo "Restauration terminée."
elif [ "$ENV" == "local" ]; then
    echo "Restauration vers l'environnement local depuis $DUMP_FILE..."
    psql -U fs_user -d freelansign < "$DUMP_FILE"
    echo "Restauration terminée."
else
    echo "Environnement inconnu : $ENV"
    echo "Usage: $0 <fichier_dump> [docker|local]"
    exit 1
fi
