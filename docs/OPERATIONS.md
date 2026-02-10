# FreelanSign - Guide Opérationnel

> Guide de référence pour le build, le déploiement, la maintenance et le debugging.
> Adapté pour Railway (backend + frontend + PostgreSQL).

---

## Table des matières

1. [Base de données : synchro local / Docker / prod](#1-base-de-données)
2. [Versioning et release workflow](#2-versioning-et-release-workflow)
3. [Build Docker en local](#3-build-docker-en-local)
4. [Déploiement sur Railway](#4-déploiement-sur-railway)
5. [Migrations](#5-migrations)
6. [Maintenance et debugging](#6-maintenance-et-debugging)
7. [Checklist pre-deploy](#7-checklist-pre-deploy)
8. [Secrets et rotation](#8-secrets-et-rotation)
9. [Backups et disaster recovery](#9-backups-et-disaster-recovery)

---

## 1. Base de données

### 1.1 Dump depuis un environnement

```bash
# Depuis Docker local (dev)
make db-dump
# → database/dumps/dump_docker_YYYYMMDD_HHMMSS.sql

# Depuis PostgreSQL local (sans Docker)
./scripts/db-dump.sh local
# → database/dumps/dump_local_YYYYMMDD_HHMMSS.sql

# Depuis Railway (prod)
# Option A : via le plugin Railway CLI
railway run pg_dump --clean --if-exists > database/dumps/dump_prod_$(date +%Y%m%d).sql

# Option B : avec l'URL de connexion Railway
pg_dump "postgresql://USER:PASS@HOST:PORT/DB" --clean --if-exists > database/dumps/dump_prod_$(date +%Y%m%d).sql
```

### 1.2 Restaurer vers un environnement

```bash
# Vers Docker local
make db-restore DUMP=database/dumps/dump_prod_20260210.sql

# Vers PostgreSQL local (sans Docker)
./scripts/db-restore.sh database/dumps/dump_prod_20260210.sql local

# Vers Railway (prod) - ATTENTION : opération destructive
railway run psql < database/dumps/dump_local_20260210.sql
```

### 1.3 Synchro typique : prod → local

```bash
# 1. Dump la prod
railway run pg_dump --clean --if-exists > database/dumps/dump_prod_$(date +%Y%m%d).sql

# 2. Restaurer en local (Docker)
make db-restore DUMP=database/dumps/dump_prod_$(date +%Y%m%d).sql

# 3. Relancer les migrations si besoin (dev a pu avancer)
make migrate
```

### 1.4 Synchro typique : local → prod

```bash
# 1. Dump le local
make db-dump

# 2. Restaurer en prod - CONFIRMER AVANT
railway run psql < database/dumps/dump_docker_YYYYMMDD_HHMMSS.sql
```

> **Attention** : ne jamais restaurer un dump local vers la prod sans vérifier que les migrations sont alignées. En cas de doute, faire un backup prod d'abord.

---

## 2. Versioning et release workflow

### 2.1 Où sont les versions

| Fichier | Clé | Exemple |
|---------|-----|---------|
| `backend/config/settings.py` L301 | `SPECTACULAR_SETTINGS.VERSION` | `v0.3.0-SNAPSHOT` |
| `frontend/package.json` L4 | `version` | `0.4.0` |
| `CHANGELOG.md` | Historique | Dernière : v0.2.1 |
| Git tags | `vX.Y.Z` | `v0.3.0` |

### 2.2 Convention de version

Format : **SemVer** `MAJOR.MINOR.PATCH`

- `MAJOR` : breaking changes (ex: nouvelle API incompatible)
- `MINOR` : nouvelles features (ex: ajout du branding)
- `PATCH` : bug fixes

Suffixes :
- `-SNAPSHOT` : version en cours de développement (pas encore release)
- `-rc.1` : release candidate, prête pour test avant mise en prod
- (aucun suffixe) : version release stable

### 2.3 Workflow de release

```bash
# 1. S'assurer d'être sur dev, à jour
git checkout dev && git pull

# 2. Mettre à jour les versions
# backend/config/settings.py : "v0.3.0-SNAPSHOT" → "v0.3.0"
# frontend/package.json      : "0.4.0" → "0.3.0" (aligner si besoin)

# 3. Mettre à jour CHANGELOG.md (ajouter la section v0.3.0)

# 4. Commit de release
git add -A && git commit -m "chore: release v0.3.0"

# 5. Tag
git tag -a v0.3.0 -m "Release v0.3.0"

# 6. Push
git push origin dev --tags

# 7. PR dev → main (production)
gh pr create --base main --head dev --title "Release v0.3.0"

# 8. Après merge : remettre en SNAPSHOT pour le prochain cycle
# backend : "v0.3.0" → "v0.3.1-SNAPSHOT"
# frontend : bump le patch
git commit -m "chore: bump to v0.3.1-SNAPSHOT"
```

### 2.4 Tester une release candidate

```bash
# Créer une RC depuis dev
git tag -a v0.3.0-rc.1 -m "Release candidate 1 for v0.3.0"
git push origin v0.3.0-rc.1

# Déployer cette RC sur un env de staging (Railway preview environment)
# Tester manuellement
# Si OK → release finale (voir 2.3)
# Si KO → fix sur dev, créer v0.3.0-rc.2
```

---

## 3. Build Docker en local

### 3.1 Build complet (dev)

```bash
# Construire toutes les images
make build

# Démarrer tous les services
make up

# Vérifier le statut
make status

# Frontend : http://localhost:3000
# Backend  : http://localhost:8000
# Postgres : localhost:5432
```

### 3.2 Build production (test local)

```bash
# Build les images prod
make prod-build

# Lancer en mode prod
make prod-up

# Vérifier que tout tourne
docker compose -f docker-compose.prod.yml ps

# Tester le frontend via nginx : http://localhost
# API via proxy nginx : http://localhost/api/

# Arrêter
make prod-down
```

### 3.3 Build d'une seule image

```bash
# Backend uniquement
docker build -t freelansign-backend ./backend

# Frontend uniquement (stage production)
docker build --target production-server -t freelansign-frontend ./frontend

# Vérifier la taille (doit être < 500 MB pour le backend)
docker images | grep freelansign
```

### 3.4 Nettoyage Docker

```bash
# Supprimer conteneurs + images non utilisées
make clean

# Nettoyage total (incluant les volumes - PERD LES DONNEES DB)
make clean-all

# Nettoyage ciblé
docker system prune -af        # images, conteneurs, réseaux
docker volume prune -f         # volumes orphelins
docker builder prune -af       # cache de build
```

---

## 4. Déploiement sur Railway

### 4.1 Architecture cible

```
Railway Project
├── Backend service    (Django + Gunicorn, port 8000)
├── Frontend service   (Nginx + React static, port 80)
├── PostgreSQL         (Railway addon)
└── Cron worker        (RGPD retention, optionnel)
```

### 4.2 Setup initial Railway

```bash
# 1. Installer Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Créer le projet
railway init

# 4. Ajouter PostgreSQL
railway add --plugin postgresql
```

### 4.3 Configuration des services

**Backend** (Django) :
- Root directory : `/backend`
- Build command : (utilise le Dockerfile)
- Start command : géré par l'entrypoint (gunicorn)
- Port : `8000`
- Variables d'env : voir [section 4.4](#44-variables-denvironnement)

**Frontend** (React/Nginx) :
- Root directory : `/frontend`
- Build command : (utilise le Dockerfile, target `production-server`)
- Port : `80`
- Variables d'env : `VITE_API_URL=https://api.freelansign.fr`

**Cron** (RGPD) :
- Même image que le backend
- Custom start command :
  ```
  sh -c "echo '0 3 * * 0 cd /app && python manage.py apply_retention_policy >> /app/logs/retention.log 2>&1' | crontab - && crond -f"
  ```

### 4.4 Variables d'environnement

Configurer dans Railway Dashboard > Service > Variables :

```env
# Core
SECRET_KEY=<générer: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=api.freelansign.fr,freelansign.fr
LOG_LEVEL=WARNING

# DB (auto-injecté par Railway si plugin PostgreSQL ajouté)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Email (Brevo SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<brevo-smtp-login>
EMAIL_HOST_PASSWORD=<brevo-smtp-password>
EMAIL_FROM=contact@freelansign.fr

# URLs
RESET_PASSWORD_URL=https://app.freelansign.fr/reset-password
EMAIL_VERIFICATION_URL=https://app.freelansign.fr/verify-email
CORS_ALLOWED_ORIGINS=https://app.freelansign.fr,https://freelansign.fr

# Sécurité
FIELD_ENCRYPTION_KEY=<générer: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
SECURE_SSL_REDIRECT=True

# RGPD
RETENTION_POLICY_ENABLED=True

# Sentry (optionnel)
# SENTRY_DSN=https://...@sentry.io/...
# SENTRY_ENVIRONMENT=production
```

### 4.5 Déploiement

```bash
# Push déclenche le deploy automatiquement si Railway est connecté au repo
git push origin dev

# Ou deploy manuel
railway up

# Vérifier les logs
railway logs
```

### 4.6 Custom domains

Dans Railway Dashboard > Service > Settings > Domains :
- Backend : `api.freelansign.fr`
- Frontend : `app.freelansign.fr`

Configurer les DNS (CNAME) chez ton registrar vers les domaines Railway.

---

## 5. Migrations

### 5.1 En développement local

```bash
# Créer une migration après modification d'un modèle
cd backend && source venv/bin/activate
python manage.py makemigrations
python manage.py migrate

# Vérifier les migrations en attente
python manage.py showmigrations | grep "\[ \]"
```

### 5.2 En Docker local

```bash
# Via Makefile
make migrate

# Ou directement
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### 5.3 En production (Railway)

Les migrations s'exécutent **automatiquement** au démarrage via l'entrypoint :

```sh
# backend/Dockerfile entrypoint.sh
gosu app python manage.py migrate
gosu app python manage.py collectstatic --noinput
exec gosu app gunicorn ...
```

Pour une migration manuelle :
```bash
railway run python manage.py migrate
railway run python manage.py showmigrations
```

### 5.4 Migrations dangereuses

Pour les migrations destructives (suppression de colonne, rename de table) :

1. **Toujours** faire un backup DB avant : `railway run pg_dump --clean > backup_pre_migration.sql`
2. Tester la migration sur une copie locale de la DB prod
3. Planifier la migration en heures creuses
4. Avoir le rollback prêt : `python manage.py migrate app_name 00XX_previous`

---

## 6. Maintenance et debugging

### 6.1 Niveaux de log par environnement

| Environnement | `LOG_LEVEL` | Justification |
|---|---|---|
| **Local (dev)** | `DEBUG` | Tout voir, pas de données sensibles |
| **Docker local** | `DEBUG` | Idem, environnement isolé |
| **Staging/RC** | `INFO` | Voir le flux sans le bruit |
| **Production** | `WARNING` | **Données sensibles en DEBUG** (emails, SIRET, payload complets) |

> **CRITIQUE** : En production, `DEBUG` log des informations personnelles (emails clients, numéros SIRET, contenus de payload). Toujours utiliser `WARNING` ou `ERROR` en prod pour rester conforme RGPD.

### 6.2 Configuration du logging

Dans `.env` (ou Railway variables) :
```env
# Prod : ne loguer que les warnings et erreurs
LOG_LEVEL=WARNING

# Staging : infos + warnings + erreurs
LOG_LEVEL=INFO

# Debug temporaire en prod (JAMAIS longtemps, penser à remettre)
LOG_LEVEL=DEBUG
```

Le logging est configuré dans `backend/config/settings.py` L371-423 :
- **Console** : stdout (visible dans `railway logs`)
- **Fichier** : `logs/app.log` (rotation 10 MB, 5 backups)
- **Format** : `timestamp LEVEL [module] [req=ID user=ID] message`

### 6.3 Debugging en production

```bash
# Voir les logs en temps réel
railway logs --tail 100

# Accéder au shell Django
railway run python manage.py shell

# Vérifier l'état de la DB
railway run python manage.py showmigrations
railway run python manage.py dbshell

# Activer temporairement le debug logging (max 30 min)
# 1. Mettre LOG_LEVEL=DEBUG dans Railway variables
# 2. Redéployer (automatique avec Railway)
# 3. Observer les logs
# 4. REMETTRE LOG_LEVEL=WARNING immédiatement après
```

### 6.4 Erreurs courantes

| Symptome | Cause probable | Fix |
|---|---|---|
| 500 sur `/api/` | Migration manquante | `railway run python manage.py migrate` |
| 502 Bad Gateway | Backend crash au démarrage | `railway logs` pour voir l'erreur Python |
| CORS error | `CORS_ALLOWED_ORIGINS` mal configuré | Vérifier la variable Railway |
| PDF ne se génère pas | WeasyPrint libs manquantes | Vérifier le Dockerfile (pango, cairo) |
| Email non envoyé | Credentials Brevo incorrectes | Vérifier `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` |
| Token expiré immédiatement | Horloge serveur décalée | Vérifier `ACCESS_TOKEN_LIFETIME` |

### 6.5 Monitoring

- **Sentry** : activer en décommentant dans `settings.py` L428-449 + ajouter `SENTRY_DSN`
- **Railway metrics** : CPU, RAM, réseau dans le dashboard
- **Health check** : ajouter un endpoint `/api/health/` (simple 200 OK)
- **UptimeRobot** : monitoring externe (gratuit, 5 min intervals)

---

## 7. Checklist pre-deploy

Avant chaque déploiement en production :

### Code
- [ ] Tous les tests passent (`pytest` backend, `pnpm build` frontend)
- [ ] Pas de `console.log` dans le code frontend
- [ ] Pas de `DEBUG=True` dans les commits
- [ ] Pas de secrets hardcodés
- [ ] Conventional commits respectés

### Versions
- [ ] Version backend mise à jour (`settings.py`)
- [ ] Version frontend mise à jour (`package.json`)
- [ ] CHANGELOG.md mis à jour
- [ ] Tag git créé (`v0.X.Y`)

### Infrastructure
- [ ] Migrations testées localement sur une copie de la DB prod
- [ ] Variables d'environnement Railway à jour
- [ ] Backup DB prod effectué avant le déploiement
- [ ] `LOG_LEVEL=WARNING` en prod (pas DEBUG)

### Post-deploy
- [ ] Smoke test : login, créer un devis, générer un PDF
- [ ] Vérifier les logs Railway (pas d'erreurs)
- [ ] Vérifier Sentry (si activé)

---

## 8. Secrets et rotation

### 8.1 Secrets gérés

| Secret | Rotation | Où |
|--------|----------|-----|
| `SECRET_KEY` | A chaque compromission | Railway vars |
| `FIELD_ENCRYPTION_KEY` | Annuelle | Railway vars + backup offline |
| `EMAIL_HOST_PASSWORD` | Selon politique Brevo | Railway vars |
| `DATABASE_PASSWORD` | Trimestrielle recommandé | Railway vars |
| `SUPABASE_SERVICE_KEY` | Selon politique Supabase | Railway vars |

### 8.2 Générer un nouveau secret

```bash
# Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# FIELD_ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

> **ATTENTION** : changer `FIELD_ENCRYPTION_KEY` rend les données chiffrées illisibles. Planifier une migration de données si rotation nécessaire.

---

## 9. Backups et disaster recovery

### 9.1 Stratégie de backup

| Fréquence | Rétention | Commande |
|-----------|-----------|----------|
| Quotidien | 7 jours | `railway run pg_dump > backup_daily_$(date +%Y%m%d).sql` |
| Hebdomadaire | 4 semaines | Garder le dump du dimanche |
| Mensuel | 12 mois | Garder le dump du 1er |

### 9.2 Restauration d'urgence

```bash
# 1. Arrêter le backend (via Railway dashboard : pause le service)

# 2. Restaurer le dernier backup
railway run psql < backup_daily_YYYYMMDD.sql

# 3. Relancer les migrations (au cas où)
railway run python manage.py migrate

# 4. Redémarrer le backend (unpause)

# 5. Smoke test
```

### 9.3 Railway PostgreSQL backups

Railway propose des backups automatiques pour PostgreSQL (plan payant). Vérifier dans :
Dashboard > PostgreSQL service > Backups

---

## Annexe : Commandes rapides

```bash
# Dev local
make dev-docker                          # Tout lancer en Docker
make logs-backend                        # Logs backend
make shell                               # Django shell

# DB
make db-dump                             # Backup
make db-restore DUMP=fichier.sql         # Restaurer
make migrate                             # Migrations

# Build
make prod-build                          # Build prod
make prod-up                             # Lancer prod local

# Railway
railway logs                             # Logs prod
railway run python manage.py migrate     # Migration prod
railway run python manage.py shell       # Shell prod
railway run pg_dump > backup.sql         # Backup prod
```
