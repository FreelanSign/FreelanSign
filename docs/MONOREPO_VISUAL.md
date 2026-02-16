# Monorepo : Comment Railway & Vercel lisent ton repo

## 🎯 Vue d'ensemble

```
┌────────────────────────────────────────────────────┐
│  GitHub Repo: FreelanSign                          │
│                                                     │
│  ├── backend/           ← Railway lit ICI          │
│  │   ├── config/                                   │
│  │   ├── apps/                                     │
│  │   ├── requirements/                             │
│  │   └── manage.py                                 │
│  │                                                  │
│  ├── frontend/          ← Vercel lit ICI           │
│  │   ├── src/                                      │
│  │   ├── package.json                              │
│  │   └── vite.config.ts                            │
│  │                                                  │
│  ├── railway.json       (lu par Railway)           │
│  ├── Procfile           (lu par Railway)           │
│  ├── nixpacks.toml      (lu par Railway)           │
│  └── docs/                                         │
└────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Railway (Backend)

### Avant (❌ ne marche pas)
```
Railway cherche à la racine :
❌ requirements/requirements.txt  (pas à la racine)
❌ manage.py                       (pas à la racine)
```

### Après (✅ marche)
```
Railway Settings → Root Directory = backend

Railway cherche dans backend/ :
✅ backend/requirements/requirements.txt
✅ backend/manage.py
✅ backend/config/wsgi.py
```

**Commandes exécutées :**
```bash
# Railway se place dans backend/ puis :
pip install -r requirements/requirements.txt
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

---

## 🎨 Configuration Vercel (Frontend)

### Avant (❌ ne marche pas)
```
Vercel cherche à la racine :
❌ package.json    (pas à la racine)
❌ src/            (pas à la racine)
```

### Après (✅ marche)
```
Vercel Settings → Root Directory = frontend

Vercel cherche dans frontend/ :
✅ frontend/package.json
✅ frontend/src/
✅ frontend/vite.config.ts
```

**Commandes exécutées :**
```bash
# Vercel se place dans frontend/ puis :
pnpm install
pnpm build
# Sert frontend/dist/
```

---

## 📊 Schéma de déploiement

```
┌─────────────────────────────────────────────────────────────┐
│                       GitHub Push                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   Railway    │      │    Vercel    │
│              │      │              │
│  Root: backend/     │  Root: frontend/ │
│              │      │              │
│  1. Install  │      │  1. Install  │
│  2. Build    │      │  2. Build    │
│  3. Deploy   │      │  3. Deploy   │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌─────────────┐
│   Backend   │      │  Frontend   │
│     API     │◄─────┤   React     │
│             │ API  │             │
│ Django +    │calls │ Vite build  │
│ PostgreSQL  │      │             │
└─────────────┘      └─────────────┘
```

---

## 🔍 Ce que voit chaque service

### Railway voit :
```
backend/
├── config/
│   ├── settings.py       ✅
│   ├── urls.py          ✅
│   └── wsgi.py          ✅
├── apps/                ✅
├── requirements/
│   └── requirements.txt ✅
├── manage.py            ✅
└── ...

frontend/                ❌ (ignoré)
docs/                    ❌ (ignoré)
```

### Vercel voit :
```
frontend/
├── src/
│   ├── App.tsx          ✅
│   └── main.tsx         ✅
├── package.json         ✅
├── vite.config.ts       ✅
└── ...

backend/                 ❌ (ignoré)
docs/                    ❌ (ignoré)
```

---

## ⚙️ Fichiers de config Railway

### railway.json (lu à la racine)
```json
{
  "build": {
    "buildCommand": "pip install -r requirements/requirements.txt"
  }
}
```

Railway exécute :
1. Se place dans `backend/` (Root Directory)
2. Lance `pip install -r requirements/requirements.txt`
3. Résout en `backend/requirements/requirements.txt` ✅

---

### Procfile (lu à la racine)
```
web: gunicorn config.wsgi:application
```

Railway exécute :
1. Se place dans `backend/` (Root Directory)
2. Lance `gunicorn config.wsgi:application`
3. Trouve `backend/config/wsgi.py` ✅

---

## 🚨 Erreurs courantes

### ❌ Erreur 1 : Root Directory pas configuré

**Symptôme :**
```
ERROR: Could not find requirements.txt
```

**Cause :**
Railway cherche `requirements.txt` à la racine (n'existe pas)

**Solution :**
Railway → Settings → Root Directory → `backend`

---

### ❌ Erreur 2 : Frontend ne build pas

**Symptôme :**
```
Error: Cannot find module 'package.json'
```

**Cause :**
Vercel cherche `package.json` à la racine (n'existe pas)

**Solution :**
Vercel → Settings → Root Directory → `frontend`

---

### ❌ Erreur 3 : Fichiers de config pas trouvés

**Symptôme :**
```
railway.json not found
```

**Cause :**
Les fichiers `railway.json`, `Procfile`, `nixpacks.toml` sont lus depuis la **racine du repo**, pas depuis le Root Directory.

**Solution :**
Place ces fichiers à la racine :
```
FreelanSign/
├── railway.json      ← ICI (racine)
├── Procfile          ← ICI (racine)
├── nixpacks.toml     ← ICI (racine)
├── backend/
└── frontend/
```

✅ **Ces fichiers sont déjà au bon endroit dans ton repo**

---

## 💡 Pourquoi Root Directory ?

### Alternative 1 : Tout dans les commandes (❌ compliqué)
```json
{
  "build": {
    "buildCommand": "cd backend && pip install -r requirements/requirements.txt && cd .."
  },
  "deploy": {
    "startCommand": "cd backend && gunicorn config.wsgi:application"
  }
}
```

**Inconvénients :**
- Répéter `cd backend` partout
- Erreur-prone (oubli de `cd backend`)
- Chemins relatifs complexes

---

### Alternative 2 : Root Directory (✅ recommandé)
```json
{
  "build": {
    "buildCommand": "pip install -r requirements/requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application"
  }
}
```

**Avantages :**
- Commandes simples et claires
- Railway gère le contexte automatiquement
- Moins d'erreurs

---

## ✅ Checklist de vérification

### Railway (Backend)
- [ ] Service Settings → Root Directory = `backend`
- [ ] `railway.json` à la racine du repo
- [ ] `Procfile` à la racine du repo
- [ ] `nixpacks.toml` à la racine du repo
- [ ] Logs : "Installing requirements.txt" ✅

### Vercel (Frontend)
- [ ] Project Settings → Root Directory = `frontend`
- [ ] Logs : "Installing dependencies from package.json" ✅
- [ ] Build Output : `dist/` directory created ✅

---

## 🎓 Résumé en 3 points

1. **Railway & Vercel** peuvent lire des sous-dossiers d'un monorepo
2. **Root Directory** = "où commence mon app" (backend/ ou frontend/)
3. **Fichiers de config** = toujours à la racine du repo (railway.json, Procfile, etc.)

---

## 🆘 En cas de problème

**Si Railway ne trouve pas tes fichiers :**
1. Check : Service Settings → Root Directory = `backend` ✅
2. Check : `railway.json`, `Procfile` à la racine ✅
3. Redéploie

**Si Vercel ne trouve pas package.json :**
1. Check : Project Settings → Root Directory = `frontend` ✅
2. Redéploie

---

**📚 Plus de détails dans `docs/MONOREPO_DEPLOYMENT.md`**
