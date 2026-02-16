# ✅ Checklist Déploiement Railway + Vercel

## 📦 Fichiers créés
- ✅ `railway.json` - Config Railway
- ✅ `Procfile` - Commandes de déploiement
- ✅ `nixpacks.toml` - Config Python

---

## 🚀 Étapes rapides

### 1️⃣ Railway (Backend + DB)

**a) Créer le projet :**
1. [railway.app](https://railway.app) → Login GitHub
2. "New Project" → "Deploy from GitHub repo" → Sélectionne FreelanSign

**b) ⚠️ CONFIGURER LE ROOT DIRECTORY (CRITIQUE) :**
1. Railway Dashboard → Service Backend → **Settings**
2. Section **"Source"** → **"Root Directory"** → Entre `backend`
3. **Save** → Railway redéploie

**c) Ajouter PostgreSQL :**
1. Dans ton projet : "+ New" → "Database" → "Add PostgreSQL"
2. ✅ Railway crée automatiquement `DATABASE_URL`

**d) Variables d'env backend :**
Dans l'onglet "Variables" du service backend :

```env
# Core
SECRET_KEY=<génère-avec: python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
FIELD_ENCRYPTION_KEY=<génère-avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# Database (référence automatique)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Email Brevo
EMAIL_HOST_USER=<ton-email-brevo>
EMAIL_HOST_PASSWORD=<ton-api-key-brevo>
EMAIL_FROM=noreply@tondomaine.com

# CORS (à mettre à jour après Vercel)
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app

# URLs Frontend (à mettre à jour après Vercel)
RESET_PASSWORD_URL=https://ton-app.vercel.app/reset-password
EMAIL_VERIFICATION_URL=https://ton-app.vercel.app/verify-email
```

**e) Tester :**
- Ouvre l'URL Railway (ex: `https://xxx.up.railway.app`)
- Teste `/api/schema/swagger/`

---

### 2️⃣ Vercel (Frontend)

**a) Déployer :**
1. [vercel.com](https://vercel.com) → Login GitHub
2. "Add New..." → "Project" → Sélectionne FreelanSign

**b) ⚠️ Config build (Root Directory CRITIQUE) :**
- Framework: Vite
- **Root Directory: `frontend`** ← IMPORTANT !
- Build Command: `pnpm build`
- Output Directory: `dist`
- Install Command: `pnpm install`

**c) Variable d'env :**
```env
VITE_API_URL=https://ton-backend.up.railway.app
```
*(Remplace par ton URL Railway)*

**d) Deploy :**
- Clique "Deploy"
- Copie l'URL Vercel (ex: `https://xxx.vercel.app`)

---

### 3️⃣ Finaliser

**a) Retourne sur Railway** et update les variables :
```env
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app
RESET_PASSWORD_URL=https://ton-app.vercel.app/reset-password
EMAIL_VERIFICATION_URL=https://ton-app.vercel.app/verify-email
```

**b) Test final :**
- Ouvre ton app Vercel : `https://ton-app.vercel.app`
- Crée un compte
- Vérifie que l'email de confirmation arrive

---

## 💰 Coûts

| Service | Coût/mois | Note |
|---------|-----------|------|
| Railway Backend | $3-5 | Gratuit avec $5 offerts |
| Railway PostgreSQL | $2-3 | Gratuit avec $5 offerts |
| Vercel Frontend | $0 | Plan Hobby gratuit |
| **TOTAL** | **$0-3** | Après crédits gratuits |

---

## 🆘 En cas de problème

**Backend ne démarre pas :**
- Check les logs Railway
- Vérifie que toutes les variables d'env sont définies

**Frontend ne charge pas :**
- Vérifie `VITE_API_URL` dans Vercel
- Vérifie que CORS est bien configuré sur Railway

**Erreur Database :**
- Vérifie `DATABASE_URL=${{Postgres.DATABASE_URL}}` dans Railway

---

## 📚 Guides détaillés

Ouvre `RAILWAY_SETUP.md` pour le guide complet étape par étape.
