# Gestion de la Base de Données

Ce document explique comment gérer la base de données PostgreSQL dans l'environnement Docker de FreelansSign, ainsi que comment interagir avec les données locales.

## 1. Gestion des Migrations en Production

Une fois votre application en production (ou en mode `dev-docker`), les migrations de schéma de base de données doivent être appliquées à l'intérieur du conteneur Docker.

### Appliquer les migrations

Pour appliquer les migrations en attente, utilisez la commande `make` suivante :

```bash
make migrate
```

Cette commande exécute `python manage.py migrate` à l'intérieur du conteneur `backend`.

Si vous préférez utiliser directement Docker Compose :

```bash
docker compose exec backend python manage.py migrate
```

### Créer de nouvelles migrations

Si vous avez modifié vos modèles et devez créer de nouveaux fichiers de migration :

```bash
docker compose exec backend python manage.py makemigrations
```

Notez que les fichiers de migration créés appartiendront à l'utilisateur `root` (car créés dans le conteneur). Vous devrez peut-être changer leur propriétaire sur votre machine hôte :

```bash
sudo chown -R $USER:$USER backend/*/migrations/
```

## 2. Import des Données Locales vers Docker

Si vous avez des données sur votre installation PostgreSQL locale et souhaitez les transférer vers votre environnement Docker, suivez ces étapes.

### Prérequis

Assurez-vous que les scripts de gestion sont exécutables :

```bash
chmod +x scripts/*.sh
```

### Étape 1 : Créer un dump de la base locale

Utilisez le script `db-dump.sh` avec l'argument `local` :

```bash
./scripts/db-dump.sh local
```

Cela créera un fichier `.sql` dans le dossier `database/dumps/` (par exemple `database/dumps/dump_local_20231027_100000.sql`).

> **Note** : Ce script utilise `pg_dump`. Assurez-vous que vous avez accès à votre base locale (fichier `.pgpass` ou configuration par défaut).

### Étape 2 : Restaurer le dump dans Docker

Utilisez le script `db-restore.sh` en spécifiant le fichier de dump et l'environnement cible `docker` :

```bash
./scripts/db-restore.sh database/dumps/dump_local_YYYYMMDD_HHMMSS.sql docker
```

Ce script va :
1. Lire le fichier de dump.
2. L'injecter dans le conteneur `postgres` via `psql`.

Une fois terminé, votre base de données Docker contiendra les données de votre base locale.

## 3. Sauvegarder la Base de Données Docker

Pour sauvegarder les données de votre environnement Docker :

```bash
make db-dump
```
Ou manuellement :
```bash
./scripts/db-dump.sh docker
```

Le dump sera stocké dans `database/dumps/`.

## 4. Commandes Utiles (Makefile)

Le fichier `Makefile` contient des raccourcis pour faciliter ces opérations :

- `make migrate` : Applique les migrations.
- `make db-dump` : Crée un dump de la base Docker.
- `make db-restore DUMP=database/dumps/mon_dump.sql` : Restaure un dump spécifique dans Docker.
