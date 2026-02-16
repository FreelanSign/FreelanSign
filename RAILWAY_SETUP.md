# Guide de déploiement Railway - FreelanSign

## 🚀 Étape 1 : Créer un compte Railway

1. Va sur [railway.app](https://railway.app)
2. Clique sur "Start a New Project"
3. Connecte-toi avec GitHub (recommandé)
4. ✅ Tu as $5 de crédit gratuit/mois

---

## 🗄️ Étape 2 : Créer la base de données PostgreSQL

1. Dans ton projet Railway, clique sur **"+ New"**
2. Sélectionne **"Database" → "Add PostgreSQL"**
3. Railway créé automatiquement :
   - Une DB Postgres
   - Une variable `DATABASE_URL` (format: `postgresql://user:pass@host:port/dbname`)
4. ✅ Copie `DATABASE_URL` pour plus tard (tu la trouveras dans l'onglet "Variables")

---

## 🐍 Étape 3 : Déployer le Backend Django

### 3.1 Créer le fichier de config Railway

Railway détecte automatiquement Django mais on va créer des fichiers pour être sûr :

1. **Fichier `railway.json`** (racine du repo) :
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements/requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Fichier `Procfile`** (racine du repo, backup si railway.json ne marche pas) :
```
web: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
release: cd backend && python manage.py migrate --noinput
```

3. **Fichier `nixpacks.toml`** (racine du repo, spécifie Python 3.11) :
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["cd backend && pip install -r requirements/requirements.txt"]

[phases.build]
cmds = ["cd backend && python manage.py collectstatic --noinput"]

[start]
cmd = "cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2"
```

### 3.2 Déployer sur Railway

1. Dans ton projet Railway, clique sur **"+ New" → "GitHub Repo"**
2. Sélectionne **FreelanSign**
3. Railway va détecter que c'est un projet Python/Django

### 3.3 Configurer les variables d'environnement

Dans l'onglet **"Variables"** de ton service backend, ajoute :

```env
# Django Core
SECRET_KEY=<génère-une-clé-secrète-longue-et-aléatoire>
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
FIELD_ENCRYPTION_KEY=<génère-avec-commande-ci-dessous>

# Database (copie depuis le service PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Email (Brevo)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<ton-email-brevo>
EMAIL_HOST_PASSWORD=<ton-api-key-brevo>
EMAIL_FROM=noreply@tondomaine.com

# CORS (Frontend Vercel)
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app

# URLs Frontend
RESET_PASSWORD_URL=https://ton-app.vercel.app/reset-password
EMAIL_VERIFICATION_URL=https://ton-app.vercel.app/verify-email

# Supabase (optionnel)
SUPABASE_URL=<ton-url-supabase>
SUPABASE_SERVICE_KEY=<ton-service-key>
SUPABASE_STORAGE_BUCKET=avatars

# Sentry (optionnel)
SENTRY_DSN=<ton-dsn-sentry>
SENTRY_ENVIRONMENT=production

# RGPD
RETENTION_POLICY_ENABLED=True
RETENTION_AUDIT_LOGS_DAYS=395
RETENTION_ACCOUNTING_YEARS=10
```

**Générer `FIELD_ENCRYPTION_KEY` :**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Générer `SECRET_KEY` :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3.4 Référencer la DB Postgres dans le backend

Railway permet de référencer les variables d'un service dans un autre avec :
```
${{Postgres.DATABASE_URL}}
```

Cela va automatiquement injecter l'URL de la DB PostgreSQL dans ton backend.

---

## ⚙️ Étape 4 : Tester le déploiement

1. Railway va builder et déployer automatiquement
2. Ouvre l'URL donnée par Railway (ex: `https://ton-app.up.railway.app`)
3. Teste l'API : `https://ton-app.up.railway.app/api/schema/swagger/`

**Si ça marche pas :**
- Regarde les logs dans Railway (onglet "Logs")
- Vérifie que toutes les variables d'env sont correctes

---

## 🎨 Étape 5 : Déployer le Frontend sur Vercel (GRATUIT)

### 5.1 Créer un compte Vercel

1. Va sur [vercel.com](https://vercel.com)
2. Connecte-toi avec GitHub
3. Clique sur "Add New..." → "Project"
4. Sélectionne **FreelanSign**

### 5.2 Configurer le build

Dans la config Vercel :
- **Framework Preset** : Vite
- **Root Directory** : `frontend`
- **Build Command** : `pnpm build`
- **Output Directory** : `dist`
- **Install Command** : `pnpm install`

### 5.3 Variables d'environnement

Ajoute dans l'onglet "Environment Variables" :

```env
VITE_API_URL=https://ton-backend.up.railway.app
```

### 5.4 Déployer

1. Clique sur "Deploy"
2. Vercel va builder et déployer
3. Tu auras une URL : `https://ton-app.vercel.app`

### 5.5 Mettre à jour CORS sur Railway

Retourne sur Railway, backend, variables d'env, et update :
```env
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app
RESET_PASSWORD_URL=https://ton-app.vercel.app/reset-password
EMAIL_VERIFICATION_URL=https://ton-app.vercel.app/verify-email
```

---

## ✅ Checklist finale

- [ ] PostgreSQL déployé sur Railway
- [ ] Backend Django déployé sur Railway
- [ ] Toutes les variables d'env configurées
- [ ] Migrations exécutées (Railway les fait auto avec le Procfile)
- [ ] Frontend déployé sur Vercel
- [ ] CORS configuré correctement
- [ ] Test de l'API backend : `/api/schema/swagger/`
- [ ] Test du frontend : page de login

---

## 💰 Coûts

**Railway (Backend + DB) :**
- PostgreSQL : ~$2-3/mois
- Backend Django : ~$3-5/mois
- **Total : ~$5-8/mois** → GRATUIT avec les $5 offerts

**Vercel (Frontend) :**
- GRATUIT (hobby plan)

**Total : ~$0-3/mois après les crédits gratuits**

---

## 🔧 Bonus : Domaine personnalisé

### Railway (Backend)
1. Va dans les settings du service backend
2. Clique sur "Generate Domain"
3. Tu peux aussi ajouter un domaine custom : `api.tondomaine.com`

### Vercel (Frontend)
1. Va dans les settings du projet
2. Clique sur "Domains"
3. Ajoute ton domaine : `app.tondomaine.com`

---

## 🐛 Troubleshooting

### Erreur "Application failed to respond"
- Vérifie que Gunicorn écoute sur `0.0.0.0:$PORT`
- Vérifie les logs Railway

### Erreur CORS
- Vérifie que `CORS_ALLOWED_ORIGINS` contient ton URL Vercel
- Format : `https://ton-app.vercel.app` (pas de slash à la fin)

### Erreur Database
- Vérifie que `DATABASE_URL` est bien référencée : `${{Postgres.DATABASE_URL}}`

### Frontend ne charge pas l'API
- Vérifie `VITE_API_URL` dans Vercel
- Vérifie que l'API est accessible : `https://ton-backend.up.railway.app/api/schema/swagger/`
