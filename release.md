# 📦 RELEASING.md — FreelanSign

> Documentation interne pour la gestion des versions et des releases.

---

## 📁 Emplacement

Ce fichier doit être placé **à la racine du repository** (`/RELEASING.md`).

---

## 🧩 Pré-requis

* Utiliser des **conventional commits** (`feat:`, `fix:`, `chore:`, etc.)
* Toutes les branches fonctionnelles doivent être mergées dans `dev`
* Le fichier `/docs/release-plan-vX.Y.Z.md` doit exister et être à jour

---

## 🚀 Étapes de release

### 1. ✅ Créer une branche de release

```bash
git checkout dev
git pull
git checkout -b release/vX.Y.Z
```

### 2. 🛠 Générer changelog + bump version

```bash
pnpm run release --release-as X.Y.Z
```

Cela :

* Met à jour `package.json`
* Génère/complète `CHANGELOG.md`
* Commit automatique : `chore(release): X.Y.Z`

### 3. 📤 Push + PR vers `main`

```bash
git push origin release/vX.Y.Z
```

→ Ouvre une PR vers `main`

### 4. 🏷 Tag + GitHub Release

```bash
git checkout main
git pull
git tag freelansign/vX.Y.Z
git push origin main --tags
```

→ Puis créer une release GitHub :

* Tag : `freelansign/vX.Y.Z`
* Titre : `vX.Y.Z – Nom de version ou résumé`
* Body : copier le contenu du `/docs/release-plan-vX.Y.Z.md`

### 5. 🔄 Back-merge dans `dev`

```bash
git checkout dev
git merge main
git push origin dev
```

---

## 📎 Conseils

* Ne jamais éditer `CHANGELOG.md` à la main
* Toujours utiliser `--release-as` pour contrôler la version
* Garder une convention stricte dans les messages de commit

---

## 👨‍💻 Exemples

```bash
pnpm run release --release-as 0.2.0
```

```bash
git checkout -b release/v0.2.0
git push origin release/v0.2.0
```
