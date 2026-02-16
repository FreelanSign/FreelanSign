# Déployer un Monorepo sur Railway + Vercel

## 🎯 Architecture

```
GitHub Repo: FreelanSign/
├── backend/          ← Railway Service (Backend API)
│   ├── config/
│   ├── apps/
│   └── requirements/
│
└── frontend/         ← Vercel Project (Frontend React)
    ├── src/
    └── package.json
```

**2 services, 1 repo, 0 problème !**

---

## 🚀 Comment ça marche ?

### Railway (Backend)

Railway peut déployer depuis un **sous-dossier** du repo :

**Configuration :**
1. Railway Dashboard → Service Backend
2. Settings → **Source**
3. **Root Directory** → `backend`

**Résultat :**
- Railway travaille comme si `backend/` était la racine
- Il ne voit pas `frontend/`
- Les commandes dans `Procfile`, `railway.json`, `nixpacks.toml` s'exécutent dans `backend/`

**Exemple :**
```toml
# nixpacks.toml
[phases.install]
cmds = ["pip install -r requirements/requirements.txt"]
# ↑ Railway exécute ça dans backend/ → donc backend/requirements/requirements.txt
```

---

### Vercel (Frontend)

Même principe pour Vercel :

**Configuration :**
1. Vercel Dashboard → Project Settings
2. **Root Directory** → `frontend`

**Résultat :**
- Vercel travaille comme si `frontend/` était la racine
- Il ne voit pas `backend/`
- Les commandes `pnpm build`, `pnpm install` s'exécutent dans `frontend/`

---

## 📋 Étapes de déploiement mises à jour

### 1️⃣ Railway (Backend Django)

#### a) Créer le service
1. [railway.app](https://railway.app) → New Project
2. **Deploy from GitHub repo** → Sélectionne `FreelanSign`

#### b) Configurer le Root Directory
⚠️ **ÉTAPE CRITIQUE** :
1. Railway Dashboard → Service Backend → **Settings**
2. Section **"Source"** → Clique sur **"Configure"**
3. **Root Directory** → Entre `backend`
4. **Save**

#### c) Ajouter PostgreSQL
1. Dans le projet : **+ New** → **Database** → **Add PostgreSQL**
2. ✅ Railway crée `DATABASE_URL`

#### d) Variables d'environnement
Dans l'onglet **Variables** du service backend :

```env
SECRET_KEY=<généré-avec-scripts/generate_secrets.py>
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
FIELD_ENCRYPTION_KEY=<généré-avec-scripts/generate_secrets.py>
DATABASE_URL=${{Postgres.DATABASE_URL}}
EMAIL_HOST_USER=<brevo>
EMAIL_HOST_PASSWORD=<brevo>
EMAIL_FROM=noreply@tondomaine.com
CORS_ALLOWED_ORIGINS=https://ton-app.vercel.app
RESET_PASSWORD_URL=https://ton-app.vercel.app/reset-password
EMAIL_VERIFICATION_URL=https://ton-app.vercel.app/verify-email
```

#### e) Déployer
Railway détecte automatiquement les changements et déploie.

**Check les logs :**
- Build : installation des dépendances
- Deploy : démarrage de Gunicorn
- Si OK : URL accessible `https://xxx.up.railway.app`

---

### 2️⃣ Vercel (Frontend React)

#### a) Créer le projet
1. [vercel.com](https://vercel.com) → Add New → Project
2. **Import Git Repository** → Sélectionne `FreelanSign`

#### b) Configurer le Root Directory
⚠️ **ÉTAPE CRITIQUE** :
1. Dans la config de déploiement :
   - **Framework Preset** : Vite
   - **Root Directory** : `frontend` ← IMPORTANT
   - **Build Command** : `pnpm build`
   - **Output Directory** : `dist`
   - **Install Command** : `pnpm install`

#### c) Variable d'environnement
Onglet **Environment Variables** :

```env
VITE_API_URL=https://ton-backend.up.railway.app
```
*(Remplace par ton URL Railway)*

#### d) Déployer
Clique **Deploy** → Vercel build et déploie

**Résultat :** `https://ton-app.vercel.app`

---

## 🔄 Workflow de développement

### Branche `dev` (développement)

```bash
# Local
git checkout dev
# Modifie backend ou frontend
git add .
git commit -m "feat: nouvelle feature"
git push origin dev
```

**Ce qui se passe :**
- ✅ Rien ! Les déploiements sont sur `main` par défaut

### Branche `main` (production)

```bash
# Merge dev → main
git checkout main
git merge dev
git push origin main
```

**Ce qui se passe :**
- 🚀 **Railway** détecte le push → déploie `backend/`
- 🚀 **Vercel** détecte le push → déploie `frontend/`

---

## 🎛️ Configurations avancées

### Option 1 : Déploiements séparés (Recommandé)

**Railway :**
- Service `backend-prod` → branche `main`
- Service `backend-staging` → branche `dev`

**Vercel :**
- Project `frontend-prod` → branche `main` → `app.tondomaine.com`
- Project `frontend-staging` → branche `dev` → `staging.tondomaine.com`

**Avantages :**
- Tester en staging avant prod
- Rollback facile
- Isolation complète

---

### Option 2 : PR Deployments (Preview)

**Railway :**
1. Service Settings → **PR Deploys** → Enable
2. Chaque PR GitHub → URL temporaire

**Vercel :**
1. Automatique ! Chaque PR → URL de preview
2. Format : `https://freelansign-git-feature-123-user.vercel.app`

**Utilité :**
- Tester une feature avant merge
- Partager avec un testeur
- CI/CD complet

---

## 🐛 Troubleshooting

### Erreur : "Cannot find module 'django'"

**Cause :** Railway n'a pas configuré le Root Directory

**Solution :**
1. Railway → Service → Settings → Source
2. Root Directory → `backend`
3. Redéployer

---

### Erreur : Frontend ne trouve pas les fichiers

**Cause :** Vercel n'a pas configuré le Root Directory

**Solution :**
1. Vercel → Project Settings → General
2. Root Directory → `frontend`
3. Redéployer

---

### Railway build un Dockerfile au lieu de Nixpacks

**Cause :** Railway détecte `Dockerfile` à la racine

**Solution 1 (Recommandé) :**
- Configure Root Directory → `backend`
- Railway ignore les fichiers hors de `backend/`

**Solution 2 :**
- Railway Settings → Builder → Force Nixpacks

---

## 📊 Comparaison des approches

| Approche | Avantages | Inconvénients |
|----------|-----------|---------------|
| **Root Directory** | ✅ Simple<br>✅ Fichiers de config courts<br>✅ Isolation claire | ❌ Config UI nécessaire |
| **`cd backend`** | ✅ Fonctionne sans config UI | ❌ Commandes longues<br>❌ Erreur-prone |
| **2 repos séparés** | ✅ Isolation totale | ❌ Gestion compliquée<br>❌ Duplication |

**Notre choix : Root Directory** (mise à jour des fichiers faite ✅)

---

## ✅ Checklist finale

### Railway (Backend)
- [ ] Service créé depuis GitHub
- [ ] **Root Directory = `backend`** ⚠️ CRITIQUE
- [ ] PostgreSQL ajouté
- [ ] Variables d'env configurées
- [ ] Déploiement réussi
- [ ] API accessible : `/api/schema/swagger/`

### Vercel (Frontend)
- [ ] Projet créé depuis GitHub
- [ ] **Root Directory = `frontend`** ⚠️ CRITIQUE
- [ ] Framework Preset = Vite
- [ ] Variable `VITE_API_URL` configurée
- [ ] Déploiement réussi
- [ ] App accessible : page de login

### Finalisation
- [ ] CORS configuré sur Railway (URL Vercel)
- [ ] Test end-to-end : création de compte
- [ ] Email de vérification reçu

---

## 🎓 Ressources

**Railway Docs :**
- [Monorepo Support](https://docs.railway.app/deploy/monorepo)
- [Root Directory](https://docs.railway.app/deploy/deployments#root-directory)

**Vercel Docs :**
- [Monorepos](https://vercel.com/docs/monorepos)
- [Root Directory](https://vercel.com/docs/concepts/deployments/build-step#root-directory)

---

## 🎯 TL;DR

1. **Railway** : Service Settings → Root Directory → `backend`
2. **Vercel** : Project Settings → Root Directory → `frontend`
3. **Fichiers de config** : Déjà mis à jour ✅ (plus de `cd backend`)
4. **Résultat** : 2 services indépendants, 1 seul repo
