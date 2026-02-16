# Railway - FAQ (Questions fréquentes)

## 💰 Tarification

### Les $5/mois c'est quoi exactement ?

Railway fonctionne en **"pay-as-you-go"** (tu paies ce que tu utilises) :

**Plan Hobby ($5/mois gratuit) :**
- $5 de crédit offert chaque mois
- Facturation à l'usage réel après les $5

**Métriques facturées :**
1. **CPU** : ~$0.000463/minute
   - Exemple : 1 vCPU à 100% = ~$20/mois
   - Ton backend : ~5-10% CPU moyen = ~$2-3/mois

2. **RAM** : ~$0.000231/GB/minute
   - Exemple : 1GB constant = ~$10/mois
   - Ton backend : ~256-512MB = ~$2-3/mois

3. **Réseau sortant** : $0.10/GB
   - Exemple : 10GB/mois = $1
   - Ton app (API REST) : ~1-2GB/mois = $0.10-0.20

4. **Stockage (DB)** : $0.25/GB/mois
   - Exemple : 5GB de données = $1.25/mois
   - Ton app (début) : 100MB = $0.03/mois

**Total estimé pour FreelanSign :**
- Backend Django : $2-3/mois
- PostgreSQL : $2-3/mois
- **= $4-6/mois → GRATUIT avec les $5 offerts**

---

### Comment surveiller ma consommation ?

1. Dashboard Railway → Onglet "Usage"
2. Tu vois en temps réel : CPU, RAM, réseau, stockage
3. **Recommandation** : Active les alertes à $4 pour être prévenu

---

### Que se passe-t-il si je dépasse les $5 ?

**Option 1** : Tu ajoutes une carte bancaire → facturé automatiquement
**Option 2** : Tu n'ajoutes pas de carte → ton app est mise en pause

**💡 Astuce** : Définis une limite de dépenses dans Railway :
- Settings → Billing → Spending Limit : $10/mois

---

## 🔧 Technique

### Pourquoi 3 fichiers (railway.json, Procfile, nixpacks.toml) ?

- **railway.json** : Config moderne Railway (recommandé)
- **Procfile** : Fallback Heroku-style (Railway le lit aussi)
- **nixpacks.toml** : Spécifie l'environnement (Python 3.11, PostgreSQL)

Railway lit dans cet ordre :
1. `railway.json` (priorité)
2. `Procfile` (si pas de railway.json)
3. Détection auto (si rien)

**Pourquoi on met les 3 ?**
- Redondance : si l'un fail, l'autre prend le relais
- Compatibilité : migration facile vers d'autres plateformes (Heroku, Render, etc.)

---

### C'est quoi `${{Postgres.DATABASE_URL}}` ?

Railway permet de **référencer les variables d'un service dans un autre**.

**Exemple :**
- Service 1 : PostgreSQL (génère `DATABASE_URL`)
- Service 2 : Backend Django (a besoin de `DATABASE_URL`)

**Sans référence :**
```env
# Tu dois copier-coller manuellement (erreur-prone)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Avec référence :**
```env
# Railway injecte automatiquement la valeur
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Avantages :**
- Automatique (Railway gère les mises à jour)
- Sécurisé (pas de copier-coller de secrets)
- Dynamique (si DB redémarre avec nouvelle URL, backend updated auto)

---

### Pourquoi `cd backend` dans les commandes ?

Ton repo est un **monorepo** :
```
FreelanSign/
├── backend/      ← Django
├── frontend/     ← React
```

Railway déploie **depuis la racine**. Donc pour lancer Django :
```bash
# ❌ FAUX (cherche manage.py à la racine)
python manage.py runserver

# ✅ BON (va dans backend/ puis lance)
cd backend && python manage.py runserver
```

**Alternative (plus complexe) :**
Tu peux déployer uniquement `backend/` en configurant :
- Railway Settings → Root Directory → `backend`

Mais ça limite la flexibilité (si tu veux ajouter des scripts à la racine plus tard).

---

### C'est quoi Gunicorn ? Pourquoi pas `python manage.py runserver` ?

**Django runserver :**
- ⚠️ **DEV ONLY** (mono-thread, pas sécurisé)
- Ne gère qu'1 requête à la fois
- Crashe facilement sous charge

**Gunicorn :**
- ✅ **Production-ready** (multi-workers)
- Gère plusieurs requêtes en parallèle
- Robuste, testé par des millions d'apps

**Config :**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

- `--workers 2` : 2 processus Python (2x plus de requêtes simultanées)
- `--timeout 120` : timeout de 120s pour les requêtes longues (PDF generation)
- `--bind 0.0.0.0:$PORT` : écoute sur tous les interfaces, port dynamique Railway

---

## 🚀 Déploiement

### Déploiement automatique ou manuel ?

**Par défaut : Automatique**
- Push sur `main` (ou branch configurée) → déploiement auto
- Pratique pour CI/CD

**Si tu préfères manuel :**
1. Railway Dashboard → Service Settings
2. "Deployments" → Désactive "Auto Deploy"
3. Tu cliques manuellement "Deploy" quand tu veux

---

### Comment déployer une branche autre que `main` ?

1. Railway Dashboard → Service Settings
2. "Source" → Change branch : `dev`, `staging`, etc.
3. Railway déploiera cette branche

**Recommandation** : 2 services Railway
- `freelansign-prod` → branche `main`
- `freelansign-staging` → branche `dev`

---

### Comment rollback si ça casse ?

1. Railway Dashboard → Service → Onglet "Deployments"
2. Tu vois l'historique des déploiements
3. Clique sur un déploiement précédent → "Redeploy"
4. ✅ Retour instantané

---

## 🐛 Debugging

### Où voir les logs ?

Railway Dashboard → Service → Onglet "Logs"

**Types de logs :**
- **Build logs** : installation des dépendances
- **Deploy logs** : démarrage de Gunicorn
- **Application logs** : logs de ton app (print, logger, etc.)

**💡 Astuce** : Filtre par type de log (Build/Deploy/App) en haut à droite

---

### Mon app crash au démarrage, que faire ?

**1. Check les logs Railway :**
```
Failed to bind to 0.0.0.0:8000
```
→ Utilise `$PORT` au lieu de 8000 fixe

**2. Check les variables d'env :**
- Vérifie que toutes les variables requises sont définies
- Teste en local avec les mêmes variables

**3. Test en local :**
```bash
cd backend
source venv/bin/activate
export SECRET_KEY="test"
export DATABASE_URL="postgresql://..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

### Erreur "Application failed to respond"

**Causes communes :**
1. **Gunicorn pas lancé** → Check logs
2. **Port incorrect** → Utilise `$PORT`
3. **ALLOWED_HOSTS** → Ajoute `*.railway.app`
4. **DB pas connectée** → Check `DATABASE_URL`

**Debug :**
```python
# backend/config/settings.py
print(f"DEBUG: SECRET_KEY={'*' * len(SECRET_KEY)}")
print(f"DEBUG: DATABASE_URL={'*' * 10}...")
print(f"DEBUG: ALLOWED_HOSTS={ALLOWED_HOSTS}")
```

Push → Check logs Railway → Tu verras les valeurs

---

## 🔒 Sécurité

### Mes variables d'env sont-elles sécurisées ?

✅ **OUI**
- Stockées chiffrées par Railway
- Injectées au runtime (pas dans le code)
- Pas visibles dans les logs publics
- Accessibles uniquement par toi (owner)

---

### Comment changer une variable d'env ?

1. Railway Dashboard → Service → Variables
2. Clique sur la variable → Edit
3. Save → **Redéploiement automatique**

**⚠️ Attention** : Changer une variable redéploie l'app (downtime ~30s)

---

### Comment gérer les secrets (API keys) ?

**❌ JAMAIS ça :**
```python
STRIPE_API_KEY = "sk_live_xxxxx"  # Hardcoded
```

**✅ TOUJOURS ça :**
```python
STRIPE_API_KEY = env("STRIPE_API_KEY")  # Depuis Railway Variables
```

**Stockage recommandé :**
1. **Secrets pas critiques** : Railway Variables
2. **Secrets ultra-critiques** : AWS Secrets Manager / Vault (overkill pour ton app)

---

## 💡 Astuces

### Preview Deployments (branches de feature)

Railway peut déployer automatiquement chaque PR GitHub :

1. Railway Dashboard → Service Settings
2. "PR Deploys" → Enable
3. Chaque PR → URL temporaire : `https://pr-123.up.railway.app`

**Utilité :**
- Tester une feature avant merge
- Partager avec un client
- CI/CD complet

---

### Custom Domain (ton propre domaine)

**Backend API :**
1. Railway → Service Settings → Networking
2. Add Custom Domain : `api.tondomaine.com`
3. Configure DNS (Railway te donne les enregistrements)

**Frontend Vercel :**
1. Vercel → Project Settings → Domains
2. Add Domain : `app.tondomaine.com`
3. Configure DNS (Vercel te donne les enregistrements)

**💰 Coût** : Domaine ~$10-15/an (Namecheap, OVH, etc.)

---

### Monitoring et Alertes

**Metrics Railway :**
- CPU, RAM, réseau, stockage en temps réel
- Graphiques des 7 derniers jours

**Alertes :**
- Settings → Notifications
- Email/Slack quand :
  - App crash
  - Déploiement échoue
  - Dépenses > seuil

---

### Base de données : Comment sauvegarder ?

**Option 1 : Railway Backups (automatique)**
- Railway sauvegarde automatiquement toutes les 24h
- Rétention : 7 jours (plan Hobby)
- Restore en 1 clic

**Option 2 : pg_dump manuel**
```bash
# Récupère DATABASE_URL depuis Railway
railway run env | grep DATABASE_URL

# Backup local
pg_dump "postgresql://user:pass@host:5432/db" > backup.sql

# Restore
psql "postgresql://user:pass@host:5432/db" < backup.sql
```

**Recommandation** : Backup manuel 1x/semaine en début de projet

---

## 🎓 Pour aller plus loin

### Migration vers un autre service (Render, Fly.io, etc.)

Tes fichiers `Procfile` et `requirements.txt` sont compatibles avec :
- ✅ Heroku
- ✅ Render
- ✅ Fly.io
- ✅ Google Cloud Run
- ✅ AWS Elastic Beanstalk

**Migration = 10 min** : change juste les variables d'env

---

### Scaling (quand ton app explose)

**Vertical Scaling (plus de ressources) :**
- Railway → Service → Resources
- Augmente CPU/RAM → coût augmente proportionnellement

**Horizontal Scaling (plus d'instances) :**
- Railway ne le fait pas automatiquement (pour l'instant)
- Tu dois gérer ça manuellement (load balancer + replicas)
- **Pas nécessaire avant 1000+ users/jour**

---

## 🆘 Support

**Railway Discord :**
- [discord.gg/railway](https://discord.gg/railway)
- Communauté active, équipe réactive

**Docs Railway :**
- [docs.railway.app](https://docs.railway.app)

**Status Page :**
- [status.railway.app](https://status.railway.app)
- Check si Railway a des incidents
