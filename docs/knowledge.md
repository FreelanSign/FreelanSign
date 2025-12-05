# Project Specification - Knowledge Base

---

This project specification will help you understand the project architecture and features.

> Important : Some specifications are in french, and might not be implemented yet.

## Description du projet

Le projet consiste à développer une SaaS de génération de devis personnalisable automatique.

Le but est de se démarquer du marcher en proposant un outil simple d'utilisation qui propose : la génération de devis, la personnalisation de son devis, l'inclusion des aspects juridiques (CGV, CGU, Factures électroniques, etc)

### Objectifs

1. **Génération d'un devis :** une génération simple et intuitive pour gagner du temps dans l'aspect administratif de l'auto entreprenariat.
2. **Gain de temps significatif :** économiser du temps à chaque nouveau client, c'est gagner du temps pour ce qui compte vraiment.
3. **Expérience utilisateur "Wow" :** dès l'inscription, le freelance ou l'auto entrepreneur doit tout de suite facilement configurer son profil, ses prestations, sa charte graphique et générer ses premiers devis. Interface simple et efficace.
4. **Ciblage initial sur les domaines de l'IT :** point de départ stratégique puisque cela regroupe le plus d'auto-entrepreneur.

## Features principales

### Utilisateurs de l'application

1. **Utilisateur** :
    - Authentification par mail ou via Google OAuth 2.0
    - Création et modification rapide d'un profil
    - Accès à un dashboard pour suivre ses devis
    - Création rapide de thème de devis pour inclure sa charte graphique
    - Menu utilisateur avec déconnexion
2. **Administrateur** :
    - Accès à un tableau de bord pour gérer les utilisateurs
    - Suppression des utilisateurs et leurs données

### User-Stories principales

#### Utilisateurs finaux

1. **Authentification** :
    - En tant qu'utilisateur, je veux m'inscrire rapidement via Google Authentification pour commencer à utiliser l'application sans effort.
    - En tant qu'utilisateur, je veux m'inscrire rapidement par mail pour commencer à utiliser l'application sans effort.
    - En tant qu'utilisateur, je veux pouvoir me déconnecter rapidement.
    - En tant qu'utilisateur, je veux pouvoir supprimer mon compte et toutes mes données en conformité avec le RGPD.

2. **Onboarding & configuration du profil** :
    - En tant qu’utilisateur, je veux être guidé lors de ma première connexion pour configurer mon profil professionnel (nom, activité, coordonnées, logo, etc.), afin que mes devis soient personnalisés à mon image.
    - En tant qu’utilisateur, je veux pouvoir modifier facilement mon profil ultérieurement pour garder mes informations à jour.
    - En tant qu’utilisateur, je veux pouvoir importer mon logo et définir ma charte graphique pour que mes devis soient cohérents avec mon identité visuelle.
    - En tant qu’utilisateur, je veux que le système me propose des couleurs et polices cohérentes avec mon logo pour accélérer la configuration de ma charte graphique.

3. **Gestion des prestations** :
    - En tant qu’utilisateur, je veux pouvoir créer, modifier et supprimer des prestations que je propose, afin de pouvoir les réutiliser dans mes devis.
    - En tant qu’utilisateur, je veux pouvoir définir pour chaque prestation : un intitulé, une description, un tarif journalier (ou horaire), et un poids en jours pour estimer rapidement la durée du projet.
    - En tant qu’utilisateur, je veux pouvoir classer mes prestations par catégorie (développement web, design, rédaction, etc.) pour les retrouver facilement.
    - En tant qu’utilisateur, je veux que le système me suggère des prestations standards selon mon domaine d’activité pour accélérer la configuration initiale.

4. **Création de devis** :
    - En tant qu’utilisateur, je veux pouvoir créer un nouveau devis à partir d’une interface simple et claire.
    - En tant qu’utilisateur, je veux pouvoir sélectionner un client existant ou en créer un nouveau directement depuis la page de création du devis.
    - En tant qu’utilisateur, je veux pouvoir ajouter plusieurs lignes de prestations à mon devis avec des quantités, taux, et descriptions personnalisables.
    - En tant qu’utilisateur, je veux que le total (HT, TVA, TTC) soit calculé automatiquement selon mes paramètres.
    - En tant qu’utilisateur, je veux pouvoir appliquer une remise (en % ou en €) sur le devis.
    - En tant qu’utilisateur, je veux pouvoir enregistrer mon devis comme brouillon avant de le finaliser.
    - En tant qu’utilisateur, je veux pouvoir visualiser un aperçu PDF du devis avant sa génération finale.

5. **Personnalisation du devis (branding & template)** :
    - En tant qu’utilisateur, je veux pouvoir choisir un modèle de mise en page pour mes devis (layout, typographie, couleurs).
    - En tant qu’utilisateur, je veux que la prévisualisation du devis reflète en temps réel mes choix de couleurs et de polices.
    - En tant qu’utilisateur, je veux pouvoir sauvegarder plusieurs thèmes de devis pour alterner selon le type de client ou de projet.
    - En tant qu’utilisateur, je veux que mon thème par défaut soit automatiquement appliqué aux nouveaux devis.

6. **Gestion des clients** :
    - En tant qu’utilisateur, je veux pouvoir créer une fiche client complète (nom, entreprise, e-mail, téléphone, adresse) pour chaque nouveau client.
    - En tant qu’utilisateur, je veux pouvoir associer plusieurs devis à un même client pour centraliser son historique.
    - En tant qu’utilisateur, je veux pouvoir rechercher un client par nom ou e-mail afin de le retrouver rapidement.
    - En tant qu’utilisateur, je veux pouvoir modifier ou supprimer un client si ses informations changent ou s’il n’est plus actif.
    - En tant qu’utilisateur, je veux que le système m’empêche de supprimer un client ayant des devis actifs ou signés sans confirmation explicite.
    - En tant qu’utilisateur, je veux voir un aperçu de tous les devis liés à un client directement depuis sa fiche.
    - En tant qu’utilisateur, je veux pouvoir importer ma liste de clients depuis un fichier CSV pour gagner du temps lors de la configuration initiale.

7. **Envoi, signature et suivi des devis** :
    - En tant qu’utilisateur, je veux pouvoir générer un lien public unique vers mon devis pour le partager facilement avec mon client.
    - En tant qu’utilisateur, je veux pouvoir envoyer le devis directement par e-mail depuis l’application (avec un message personnalisé et mon branding).
    - En tant qu’utilisateur, je veux que mon client puisse visualiser le devis en ligne sur une page responsive et propre.
    - En tant qu’utilisateur, je veux que le client puisse signer le devis électroniquement (signature simple ou validation via code OTP).
    - En tant qu’utilisateur, je veux recevoir une notification (e-mail et dans le dashboard) dès que le client ouvre, commente ou signe un devis.
    - En tant qu’utilisateur, je veux pouvoir marquer manuellement un devis comme “Accepté” ou “Refusé” si la signature électronique n’est pas utilisée.
    - En tant qu’utilisateur, je veux voir l’état de chaque devis (Brouillon, Envoyé, Consulté, Signé, Refusé, Expiré) dans mon dashboard.
    - En tant qu’utilisateur, je veux pouvoir télécharger à tout moment le devis signé au format PDF.

---
### Initial Scope

#### Version 0 (MVP)

**Fonctionnalités**

1. **Inscription & Onboarding**:
    - [x] Authentification via e-mail
    - [ ] Authentification via Google Authentification
    - [ ] Création d'un compte avec vérification e-mail
    - [x] Modification du profil
    - [x] Sélection d'un domaine & des prestations
2. **Dashboard** :
    - [x] Dashboard minimal listant les devis
    - [ ] Filtrage par status
    - [ ] Statistiques de bases (nombre de devis créés / signés)
    - [x] Création d'un devis, preview d'un devis, génération du pdf
3. **Gestion des clients** :
    - [ ] CRUD complet des clients (backend + frontend)
    - [ ] Liaison devis <-> client
    - [ ] Création d'une fiche client (via menu ou à la volée dans la création d'un devis)
4. **Gestion des prestations** :
    - [ ] CRUD complet des prestations (backend + frontend)
    - [ ] Liaison prestations <-> utilisateur
    - [ ] Catégorisation des prestations
    - [ ] Création de prestations par l'utilisateur
    - [x] Import csv
5. **Gestion & Génération des devis** :
    - [x] Aperçu & génération PDF
    - [ ] Endpoint sendDocument (génération token + envoi e-mail)
    - [ ] Génération PDF côté serveur + stockage S3
    - [x] Choix du thème / charte graphique appliqué au devis
    - [x] Calcul automatique HT / TVA / TTC

### Choix initial des technologies

#### Main Technologies

- Django
- React, Typescript

#### Paradigms

- **Clean Architecture** : All business logic is isolated from external concerns (frameworks, databases, APIs). The application is structured into Domain / Application / Adapters / Interface layers. This ensures: Independence from frameworks, High testability, Easy replacement of infrastructure components (database, UI, etc.)

- **Clean Code**: Every module must be : Readable — names clearly reflect intent,Maintainable — single responsibility per file/class, Consistent — strict linting and formatting rules enforced, Self-documented — code should explain itself, comments only where logic isn’t obvious. The principle: “Code should read like well-written prose.”
- **TDD** : Each feature follows the Red → Green → Refactor cycle: 1- Write a failing test (specifying expected behavior), 2- Implement minimal code to make it pass, 3- Refactor for clarity and maintainability. This keeps logic testable, modular, and avoids regression. Unit tests (pytest, Jest) are mandatory on domain and application layers.
- **DDD** : Business logic drives the codebase structure.The Domain layer expresses the core rules and concepts of the business (quotes, clients, documents, templates). Ubiquitous language is shared between developers, domain experts, and documentation to avoid ambiguity. Bounded contexts are separated (e.g., User, Quote, Document, Branding) to maintain clear ownership and reduce coupling.


#### Secondary Technologies

##### Database

- **PostgreSQL**
- **Redis?** : caching and async task acceleration (sessions, notifications, rate limiting).

##### Backend

- **Django REST Framework (DRF)** : API layer, serializers, permissions
- **Celery + Redis** : async background jobs (email sending, PDF generation)
- **Swagger / drf-spectacular** : auto-generated API documentation
- **Pytest** : testing framework (unit + integration tests)


##### Authentication

- **Django Allauth + dj-rest-auth** — JWT authentication and social login (Google OAuth 2.0)
- **Custom User Model with profile completion tracking**
- **Secure password storage (PBKDF2 / Argon2)**
##### Security
- **Environment variables** for all secrets (API keys, DB credentials)
- **Rate limiting + CSRF protection on critical endpoints**
##### Others
- **S3 (MinIO / AWS)** for file storage (logos, generated PDFs)
- **Stripe (planned)** for payment and invoicing integration
- **Docker + Docker Compose** for reproducible environments
- **Pre-commit** hooks for linting and test checks
- **GitHub Actions CI/CD** for automatic testing and deployment

## Git Gestion
#### Monorepo
- One repo `FreelanSign` with /backend & /frontend packages.

---
### Conventional Commit Guide

https://github.com/BryanLomerio/conventional-commit-cheatsheet

#### Commit Message Format

Each commit message should follow this structure:

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

- **type**: a noun that describes the kind of change (see list below)
- **scope**: optional, a noun describing the section of the codebase impacted (e.g, auth, api, frontend)
- **short description**: imperative, present tense, no trailing period
- **body**: optional detailed explanation (if needed)
- **footer**: optional metadata (e.g., BREAKING CHANGE: or issue tracker references)

**Notes**:
- Use the imperative mood (“fix”, “add”, “remove”), as if giving an order.
- Keep the subject line under ~50 characters if possible.
- Use the body to explain why the change was made, not what was changed.
- Footer is used for major changes, breaking changes, or referencing issues.

⸻

#### Commit Types

Here are the standard types you should use:
```
feat: A new feature for the user or system.
```
> Example: feat(auth): add Google login feature
```
fix: A bug fix for the user or system.
```
> Example: fix(button): resolve issue with button hover state
```
docs: Documentation only changes.
```
> Example: docs(readme): update installation instructions
```
style: Changes that do not affect meaning of the code (white-space, formatting,
missing semi-colons, etc.).
```
> Example: style(button): fix button alignment in CSS
```
refactor: Code change neither adds a feature nor fixes a bug.
```
> Example: refactor(auth): simplify login form validation logic
```
test: Adding missing tests or correcting existing tests.
```
> Example: test(auth): add unit tests for login function
```
build: Changes that affect the build system or external dependencies (example:
gulp, Webpack, npm).

```
> Example: build(webpack): add webpack config for production build
```
ci: Changes to our CI configuration files and scripts (example: GitHub Actions,
GitLab CI).
```
> Example: ci(gitlab): update CI config for deployment pipeline
```
perf: A code change that improves performance.
```
> Example: perf(api): optimize database queries for faster responses
```
env: Changes relating to environment setup or configuration.
```
> Example: env(docker): update Dockerfile for staging environment
```
sec: A commit that addresses a security issue.
```
> Example: sec(auth): add encryption for user passwords
```
config: Changes to configuration files (could overlap with build/ci but
dedicated for config).
```
> Example: config: update .eslint rules for stricter code checks
```
api: Updates to API contracts or integrations.
```

> Example: api(user): add new endpoint for user profile updates
---

Additional types you may occasionally use:

```
revert: Reverts a previous commit.
```
> Example: revert(auth): rollback Google login feature
```
merge: Indicates a merge commit.
```
> Example: merge: branch 'feature/auth' into 'main'
```
deps: Dependency-specific updates (e.g., bumping a library).
```
> Example: deps: bump axios from 0.21.1 to 0.24.0
```
design: UI/UX or design improvements.
```
> Example: design(button): update hover effect

---

#### Semantic Versioning & Commit Impact
- Use semantic versioning: MAJOR.MINOR.PATCH
- PATCH: backward-compatible bug fixes (fix:).
- MINOR: backward-compatible new features (feat:).
- MAJOR: incompatible API changes or breaking changes.
- When your commit introduces a breaking change, add ! after type or include BREAKING CHANGE: in the footer.
Example: feat!: drop support for Node 10 / or add BREAKING CHANGE: ….
- The version bump should be inferred from the commit types and notes rather than manually picked.

---

#### Development Workflow
1. Create a branch from main (or your stable branch). Branch names should reflect what you’re working on (see branch section below).
2.	Make your changes locally.
3.	Stage and commit changes using the Conventional Commit format.
4.	Push your branch to remote and open a pull request.
5.	Code review happens, changes may be requested — update accordingly with new commits still following conventions.
6.	Once approved, merge (preferably via Squash + Merge or Rebase + Merge) so the commit history remains clean and follows conventions.
7.	Upon merging, the version bump is applied (automatically or manually) depending on your release process.
8.	Tag the release in Git with the new version.

---
#### Pull Request Checklist

Before you request a merge or complete a PR, ensure:
- Commit messages follow the Conventional Commit format.
- Scope (if applicable) is correctly specified.
- Description clearly states why the changes were made.
- No large or irrelevant unrelated changes are bundled.
- Tests were added/updated for new behavior or bug fix.
- CI builds pass without errors.
- Documentation (if needed) has been updated.
- Branch name follows naming rules (see next section).
- If the change introduces a breaking change, BREAKING CHANGE: footer is present and version bump to MAJOR is planned.
- No sensitive data (passwords, keys) committed.

---

#### Branch Naming Conventions
- **main or master**: production-ready branch.
- **dev**: integration branch for completed PRs.
- **Feature branches**: `feature/<ticket-id>-<short-description>`.
Example: feature/ABC-123-add-google-login
- **Bugfix branches**: `bugfix/<ticket-id>-<short-description>`
- **Hotfix branches**: `hotfix/<ticket-id>-<short-description>`
- **Release branches**: `release/<version>`.

Avoid long or vague names; use kebab-case and reference issue/ticket IDs if relevant.

---

#### Important Notes for Commit Messages
- One commit = one logical change. Don’t combine unrelated fixes/features in a single commit.
- Write messages that explain why the change was made, not just what was done.
- Use imperative mood: “add”, “fix”, “update”, not “added” or “fixes”.
- Use scopes wisely to convey area impacted (helpful for tooling and readability).
- Keep the subject line short and clear; if details are needed, add a body.
- Use ! after type (e.g., feat!:) or BREAKING CHANGE: in the footer for breaking changes.
- Use multi-line commits only when needed.
- Avoid generic messages like “update” or “changes”. Be specific: e.g., chore(deps): update Django to 4.2.1.

---

#### Version Control
- Use tags in Git to mark releases: v1.0.0, v1.1.0, etc.
- Automate changelog generation if possible (tools like conventional-changelog).
- Review the commit history for the release branch to determine version bump (PATCH/MINOR/MAJOR).
- Post-release, merge back hotfix or release branch into develop (if branching model uses it).
- Ensure that after a release, main always reflects the production version and develop (if any) includes ongoing work.
- Protect main (and develop) branches: require pull request, code review, passing CI, and correct commit messages before merging.

### Release Strategy

> La documentation interne pour la gestion des versions et des releases est également stockée dans `release.md`.

---

#### 🧩 Pré-requis

* Utiliser des **conventional commits** indiqués dans ce chapitre (`feat:`, `fix:`, `chore:`, etc.)
* Toutes les branches fonctionnelles doivent être mergées dans `dev`
* Le fichier `/docs/release-plan-vX.Y.Z.md` doit exister et être à jour

---

#### 🚀 Étapes de release

##### 1. ✅ Créer une branche de release

```bash
git checkout dev
git pull
git checkout -b release/vX.Y.Z
```

##### 2. 🛠 Générer changelog + bump version

```bash
pnpm run release --release-as X.Y.Z
```

Cela :

* Met à jour `package.json`
* Génère/complète `CHANGELOG.md`
* Commit automatique : `chore(release): X.Y.Z`

##### 3. 📤 Push + PR vers `main`

```bash
git push origin release/vX.Y.Z
```

→ Ouvre une PR vers `main`

##### 4. 🏷 Tag + GitHub Release

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

##### 5. 🔄 Back-merge dans `dev`

```bash
git checkout dev
git merge main
git push origin dev
```

---

#### 📎 Conseils

* Ne jamais éditer `CHANGELOG.md` à la main
* Toujours utiliser `--release-as` pour contrôler la version
* Garder une convention stricte dans les messages de commit

---

#### 👨‍💻 Exemples

```bash
pnpm run release --release-as 0.2.0
```

```bash
git checkout -b release/v0.2.0
git push origin release/v0.2.0
```

---

In summary: Adopting the Conventional Commit standard promotes clarity, quality and traceability. For a collaborative project like Freelansign, following these rules will make your commit history meaningful, your releases predictable, and your codebase easier to maintain.

## Project structure
<!-- BEGIN AUTO: PROJECT_STRUCTURE -->
```text
.
├── .agent
│   └── rules
│       └── overall-guide.md
├── .claude
│   ├── commands
│   │   ├── dev-docs-update.md
│   │   └── dev-docs.md
│   ├── settings.json
│   └── settings.local.json
├── .coverage
├── .dockerignore
├── .env
├── .env.docker
├── .env.example
├── .env.local
├── .github
│   ├── CODEOWNERS
│   ├── hooks
│   ├── test
│   └── workflows
│       ├── ci.yml
│       └── enforce-dev-to-main.yml
├── .gitignore
├── .mcp.json
├── .pre-commit-config.yaml
├── .sonarcloud.properties
├── .sonarignore
├── AGENT.md
├── backend
│   ├── .claude
│   │   └── settings.local.json
│   ├── .coverage
│   ├── .coveragerc
│   ├── .dockerignore
│   ├── apps
│   │   ├── __init__.py
│   │   ├── branding
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   ├── __init__.py
│   │   │   │   ├── persistence
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── django_theme_repository.py
│   │   │   │   └── storage
│   │   │   │       ├── __init__.py
│   │   │   │       └── django_logo_storage.py
│   │   │   ├── admin.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dto
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── theme_inputs.py
│   │   │   │   │   └── theme_viewmodels.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── ports
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── logo_storage.py
│   │   │   │   │   └── theme_repository.py
│   │   │   │   └── usecases
│   │   │   │       ├── __init__.py
│   │   │   │       ├── activate_theme.py
│   │   │   │       ├── create_theme.py
│   │   │   │       ├── deactivate_theme.py
│   │   │   │       ├── delete_theme.py
│   │   │   │       ├── get_active_theme.py
│   │   │   │       ├── get_theme_for_rendering.py
│   │   │   │       ├── list_themes.py
│   │   │   │       └── update_theme.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── entities
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── brand_theme.py
│   │   │   │   ├── policies
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── theme_policy.py
│   │   │   │   ├── services
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── theme_normalizer.py
│   │   │   │   │   └── theme_validator.py
│   │   │   │   └── value_objects
│   │   │   │       ├── __init__.py
│   │   │   │       ├── color_palette.py
│   │   │   │       ├── spacing_config.py
│   │   │   │       └── typography_config.py
│   │   │   ├── interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── permissions.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   ├── 0002_add_account_fk.py
│   │   │   │   ├── 0003_migrate_to_account.py
│   │   │   │   └── 0004_account_not_null_drop_professional.py
│   │   │   ├── models.py
│   │   │   └── tests
│   │   │       ├── __init__.py
│   │   │       ├── adapters
│   │   │       │   └── __init__.py
│   │   │       ├── application
│   │   │       │   └── __init__.py
│   │   │       ├── conftest.py
│   │   │       ├── domain
│   │   │       │   └── __init__.py
│   │   │       └── interface
│   │   │           └── __init__.py
│   │   ├── catalog
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   └── persistence
│   │   │   │       └── django_prestation_repository.py
│   │   │   ├── admin.py
│   │   │   ├── application
│   │   │   │   ├── dto
│   │   │   │   │   ├── prestation_inputs.py
│   │   │   │   │   └── prestation_viewmodels.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── ports
│   │   │   │   │   └── prestation_repository.py
│   │   │   │   └── usecases
│   │   │   │       ├── get_prestation.py
│   │   │   │       └── list_prestations.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── errors.py
│   │   │   │   ├── policies
│   │   │   │   │   └── prestation_policy.py
│   │   │   │   └── services
│   │   │   │       └── prestation_calculator.py
│   │   │   ├── interface
│   │   │   │   ├── error_handler.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   ├── 0002_remove_prestation_unique_area_prestation_name_and_more.py
│   │   │   │   ├── 0003_add_account_fk.py
│   │   │   │   ├── 0004_migrate_to_account.py
│   │   │   │   ├── 0005_account_not_null_drop_professional_user.py
│   │   │   │   ├── 0006_remove_prestation_unique_area_prestation_name_global_and_more.py
│   │   │   │   └── 0007_remove_prestation_unique_area_prestation_name_global.py
│   │   │   ├── models.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── domain
│   │   │   │   │   ├── test_prestation_calculator.py
│   │   │   │   │   └── test_prestation_policy.py
│   │   │   │   ├── test_api_catalog.py
│   │   │   │   └── test_models.py
│   │   │   └── views.py
│   │   ├── client
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   └── persistence
│   │   │   │       └── django_client_repository.py
│   │   │   ├── admin.py
│   │   │   ├── application
│   │   │   │   ├── dto
│   │   │   │   │   ├── client_inputs.py
│   │   │   │   │   └── client_viewmodels.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── ports
│   │   │   │   │   ├── client_repository.py
│   │   │   │   │   └── clock.py
│   │   │   │   └── usecases
│   │   │   │       ├── create_client.py
│   │   │   │       ├── delete_client.py
│   │   │   │       ├── get_client.py
│   │   │   │       ├── list_clients.py
│   │   │   │       └── update_client.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── errors.py
│   │   │   │   └── policies
│   │   │   │       └── client_policies.py
│   │   │   ├── interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   ├── 0002_client_account.py
│   │   │   │   ├── 0003_migrate_client_to_account.py
│   │   │   │   ├── 0004_alter_client_account.py
│   │   │   │   └── 0005_update_client_index.py
│   │   │   ├── models.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapters
│   │   │   │   │   └── test_django_client_repository.py
│   │   │   │   ├── application
│   │   │   │   │   └── test_create_client.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── domain
│   │   │   │   │   └── test_name_policy.py
│   │   │   │   ├── test_api_client_endpoint.py
│   │   │   │   ├── test_client_policies.py
│   │   │   │   └── test_create_client.py
│   │   │   └── views.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── enums.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   ├── managers.py
│   │   │   ├── middleware
│   │   │   │   └── request_logging.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   └── 0001_initial.py
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   └── mixins.py
│   │   │   ├── models.py
│   │   │   ├── permissions.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_enums.py
│   │   │   │   ├── test_mixins.py
│   │   │   │   └── test_money.py
│   │   │   ├── utils
│   │   │   │   ├── __init__.py
│   │   │   │   └── money.py
│   │   │   └── views.py
│   │   ├── email
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   ├── __init__.py
│   │   │   │   └── rendering
│   │   │   │       ├── __init__.py
│   │   │   │       └── django_quote_email_renderer.py
│   │   │   ├── admin.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dto
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── prepared_email_data.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── ports
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── email_template_renderer.py
│   │   │   │   │   └── quote_repository.py
│   │   │   │   └── usecases
│   │   │   │       ├── __init__.py
│   │   │   │       └── prepare_quote_email.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── entities
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── prepared_email.py
│   │   │   │   ├── policies
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── services
│   │   │   │   │   └── __init__.py
│   │   │   │   └── value_objects
│   │   │   │       └── __init__.py
│   │   │   ├── interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── permissions.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── models.py
│   │   │   ├── templates
│   │   │   │   └── emails
│   │   │   │       ├── quote_fr.html
│   │   │   │       └── quote_fr.txt
│   │   │   └── tests
│   │   │       ├── __init__.py
│   │   │       ├── adapters
│   │   │       │   └── rendering
│   │   │       │       └── test_django_quote_email_renderer.py
│   │   │       ├── application
│   │   │       │   ├── ports
│   │   │       │   │   └── test_email_template_renderer_contract.py
│   │   │       │   └── usecases
│   │   │       │       └── test_prepare_quote_email.py
│   │   │       ├── bdd
│   │   │       │   ├── features
│   │   │       │   │   └── get_prepared_email.feature
│   │   │       │   ├── steps
│   │   │       │   │   └── email_steps.py
│   │   │       │   └── test_prepared_email.py
│   │   │       └── interface
│   │   │           └── test_prepared_email_view.py
│   │   ├── legal_terms
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   ├── __init__.py
│   │   │   │   ├── persistence
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── django_attached_terms_repository.py
│   │   │   │   │   ├── django_legal_profile_repository.py
│   │   │   │   │   ├── django_legal_template_repository.py
│   │   │   │   │   └── models.py
│   │   │   │   ├── rendering
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── template_renderer.py
│   │   │   │   └── services
│   │   │   │       ├── __init__.py
│   │   │   │       └── account_service_adapter.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dtos
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── attach_dto.py
│   │   │   │   │   ├── legal_profile_dto.py
│   │   │   │   │   └── preview_dto.py
│   │   │   │   ├── ports
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── account_service.py
│   │   │   │   │   ├── attached_terms_repository.py
│   │   │   │   │   ├── legal_profile_repository.py
│   │   │   │   │   ├── legal_template_repository.py
│   │   │   │   │   └── template_renderer.py
│   │   │   │   └── use_cases
│   │   │   │       ├── __init__.py
│   │   │   │       ├── attach_terms_to_quote.py
│   │   │   │       ├── preview_legal_terms.py
│   │   │   │       └── update_legal_profile.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── entities
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── attached_terms.py
│   │   │   │   │   ├── legal_profile.py
│   │   │   │   │   └── legal_template.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── services
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── legal_terms_assembler.py
│   │   │   │   └── value_objects
│   │   │   │       ├── __init__.py
│   │   │   │       ├── clause_category.py
│   │   │   │       ├── clause_content.py
│   │   │   │       ├── rendered_clause.py
│   │   │   │       └── template_variables.py
│   │   │   ├── interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── serializers.py
│   │   │   │   │   └── views.py
│   │   │   │   └── urls.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── 0002_seed_base_fr_template.py
│   │   │   ├── models.py
│   │   │   └── tests
│   │   │       ├── __init__.py
│   │   │       ├── bdd
│   │   │       │   ├── __init__.py
│   │   │       │   ├── features
│   │   │       │   │   ├── attach_legal_terms_to_quote.feature
│   │   │       │   │   └── legal_terms_assembly.feature
│   │   │       │   ├── manage_legal_profile.feature
│   │   │       │   └── steps
│   │   │       │       ├── test_bdd_attach.py
│   │   │       │       ├── test_legal_terms_assembly_steps.py
│   │   │       │       └── test_manage_legal_profile_steps.py
│   │   │       ├── conftest.py
│   │   │       ├── test_api_legal_profile.py
│   │   │       ├── test_api_preview.py
│   │   │       ├── test_app_smoke.py
│   │   │       ├── test_domain_assembler.py
│   │   │       ├── test_domain_entities.py
│   │   │       ├── test_domain_value_objects.py
│   │   │       ├── test_persistence_repositories.py
│   │   │       ├── test_rendering_template_renderer.py
│   │   │       ├── test_use_case_attach.py
│   │   │       ├── test_use_case_preview.py
│   │   │       └── test_use_case_update_profile.py
│   │   ├── quote
│   │   │   ├── __init__.py
│   │   │   ├── adapters
│   │   │   │   ├── __init__.py
│   │   │   │   ├── email
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── django_email_sender.py
│   │   │   │   ├── pdf
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── playwright_generator.py
│   │   │   │   ├── persistence
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── django_prestation_repository.py
│   │   │   │   │   └── django_quote_repository.py
│   │   │   │   ├── reference
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── django_quote_reference_generator.py
│   │   │   │   └── rendering
│   │   │   │       ├── __init__.py
│   │   │   │       ├── django_template_renderer.py
│   │   │   │       └── pdf_context_presenter.py
│   │   │   ├── admin.py
│   │   │   ├── application
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dto
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── quote_inputs.py
│   │   │   │   │   └── quote_viewmodels.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── ports
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── client_repository.py
│   │   │   │   │   ├── clock.py
│   │   │   │   │   ├── email_sender.py
│   │   │   │   │   ├── pdf_generator.py
│   │   │   │   │   ├── prestation_repository.py
│   │   │   │   │   ├── quote_repository.py
│   │   │   │   │   ├── reference_gen.py
│   │   │   │   │   └── template_renderer.py
│   │   │   │   └── usecases
│   │   │   │       ├── __init__.py
│   │   │   │       ├── add_prestation_line.py
│   │   │   │       ├── change_status.py
│   │   │   │       ├── create_quote.py
│   │   │   │       ├── download_pdf.py
│   │   │   │       ├── duplicate_quote.py
│   │   │   │       ├── generate_preview.py
│   │   │   │       ├── send_quote.py
│   │   │   │       └── update_quote.py
│   │   │   ├── apps.py
│   │   │   ├── domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── policies
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── status_policy.py
│   │   │   │   │   └── tax_policy.py
│   │   │   │   └── services
│   │   │   │       ├── __init__.py
│   │   │   │       └── totals.py
│   │   │   ├── interface
│   │   │   │   ├── __init__.py
│   │   │   │   ├── permissions.py
│   │   │   │   ├── renderers.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   ├── 0002_alter_quotelineitem_options_and_more.py
│   │   │   │   ├── 0003_alter_paymentterms_owner_and_more.py
│   │   │   │   ├── 0004_alter_quote_reference.py
│   │   │   │   ├── 0005_add_account_fk.py
│   │   │   │   ├── 0006_migrate_to_account.py
│   │   │   │   ├── 0007_account_not_null.py
│   │   │   │   └── 0008_alter_quote_account.py
│   │   │   ├── models.py
│   │   │   ├── signals.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapters
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_django_quote_repository.py
│   │   │   │   │   ├── test_playwright_pdf.py
│   │   │   │   │   ├── test_reference_generator_concurrency.py
│   │   │   │   │   └── test_reference_generator.py
│   │   │   │   ├── application
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_add_prestation_line.py
│   │   │   │   │   ├── test_generate_preview.py
│   │   │   │   │   └── usecases
│   │   │   │   │       ├── test_create_quote.py
│   │   │   │   │       └── test_update_quote.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── domain
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_tax_policy.py
│   │   │   │   │   └── test_totals.py
│   │   │   │   ├── temp_fixtures.py
│   │   │   │   ├── test_add_prestation_line_api.py
│   │   │   │   ├── test_mock_verification.py
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_pdf_download_api.py
│   │   │   │   ├── test_permissions.py
│   │   │   │   ├── test_preview.py
│   │   │   │   ├── test_quote_actions_api.py
│   │   │   │   └── test_serializers.py
│   │   │   └── views.py
│   │   └── user
│   │       ├── __init__.py
│   │       ├── adapters
│   │       │   ├── __init__.py
│   │       │   ├── persistence
│   │       │   │   ├── __init__.py
│   │       │   │   ├── django_account_repository.py
│   │       │   │   └── django_user_repository.py
│   │       │   ├── providers
│   │       │   │   ├── logging_token_sender.py
│   │       │   │   └── smtp_token_provider.py
│   │       │   └── system_clock.py
│   │       ├── admin.py
│   │       ├── application
│   │       │   ├── dto
│   │       │   │   ├── account_inputs.py
│   │       │   │   ├── account_viewmodels.py
│   │       │   │   ├── user_inputs.py
│   │       │   │   └── user_viewmodels.py
│   │       │   ├── errors.py
│   │       │   ├── ports
│   │       │   │   ├── account_repository.py
│   │       │   │   ├── clock.py
│   │       │   │   ├── token_sender.py
│   │       │   │   └── user_repository.py
│   │       │   └── usecases
│   │       │       ├── change_password.py
│   │       │       ├── create_account.py
│   │       │       ├── deactivate_account.py
│   │       │       ├── get_user_accounts.py
│   │       │       ├── list_users.py
│   │       │       ├── register_user.py
│   │       │       ├── request_password_reset.py
│   │       │       ├── reset_password.py
│   │       │       ├── update_account.py
│   │       │       └── update_profile.py
│   │       ├── apps.py
│   │       ├── backend
│   │       │   └── apps
│   │       │       └── user
│   │       │           └── logs
│   │       ├── domain
│   │       │   ├── entities
│   │       │   │   ├── __init__.py
│   │       │   │   └── account.py
│   │       │   ├── errors.py
│   │       │   ├── policies
│   │       │   │   ├── account_policy.py
│   │       │   │   └── user_policy.py
│   │       │   ├── services
│   │       │   │   └── user_calculator.py
│   │       │   └── value_objects.py
│   │       ├── interface
│   │       │   ├── __init__.py
│   │       │   ├── auth_urls.py
│   │       │   ├── auth_views.py
│   │       │   ├── errors_handler.py
│   │       │   ├── exceptions
│   │       │   │   ├── __init__.py
│   │       │   │   └── account_exceptions.py
│   │       │   ├── middleware
│   │       │   │   ├── __init__.py
│   │       │   │   └── account_context.py
│   │       │   ├── permissions
│   │       │   │   ├── __init__.py
│   │       │   │   └── account_permissions.py
│   │       │   ├── serializers
│   │       │   │   ├── __init__.py
│   │       │   │   ├── account_serializers.py
│   │       │   │   └── user_serializers.py
│   │       │   └── views
│   │       │       ├── __init__.py
│   │       │       ├── account_views.py
│   │       │       └── user_views.py
│   │       ├── migrations
│   │       │   ├── __init__.py
│   │       │   ├── 0001_initial.py
│   │       │   ├── 0002_remove_user_username_alter_user_email.py
│   │       │   ├── 0003_alter_user_managers_profile.py
│   │       │   ├── 0004_migrate_profile_data.py
│   │       │   ├── 0005_alter_user_options_user_uniq_user_email_ci.py
│   │       │   ├── 0006_professionaluser.py
│   │       │   ├── 0007_professionaluser_allowed_areas.py
│   │       │   ├── 0008_remove_professionaluser_allowed_areas.py
│   │       │   ├── 0009_account.py
│   │       │   ├── 0010_migrate_professional_to_account.py
│   │       │   ├── 0011_cleanup_phase6.py
│   │       │   └── 0012_add_rate_and_service_types_to_account.py
│   │       ├── models
│   │       │   ├── __init__.py
│   │       │   ├── account.py
│   │       │   └── models.py
│   │       ├── services
│   │       │   ├── __init__.py
│   │       │   └── email_change.py
│   │       ├── signals.py
│   │       ├── tests
│   │       │   ├── __init__.py
│   │       │   ├── adapters
│   │       │   │   ├── __init__.py
│   │       │   │   └── persistence
│   │       │   │       ├── __init__.py
│   │       │   │       └── test_django_account_repository.py
│   │       │   ├── application
│   │       │   │   └── usecases
│   │       │   │       ├── __init__.py
│   │       │   │       ├── test_create_account.py
│   │       │   │       ├── test_deactivate_account.py
│   │       │   │       ├── test_get_user_accounts.py
│   │       │   │       ├── test_request_password_reset.py
│   │       │   │       ├── test_reset_password.py
│   │       │   │       └── test_update_account.py
│   │       │   ├── domain
│   │       │   │   ├── __init__.py
│   │       │   │   ├── test_account_entity.py
│   │       │   │   ├── test_account_policy.py
│   │       │   │   └── test_legal_form_value_object.py
│   │       │   ├── interface
│   │       │   │   ├── __init__.py
│   │       │   │   ├── serializers
│   │       │   │   │   └── test_reset_password_serializer.py
│   │       │   │   └── test_account_api.py
│   │       │   ├── test_auth_api.py
│   │       │   ├── test_auth_logout.py
│   │       │   ├── test_refresh_rotation.py
│   │       │   └── test_user_api.py
│   │       └── urls.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── api_errors.py
│   │   ├── asgi.py
│   │   ├── exceptions.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── conftest.py
│   ├── coverage.xml
│   ├── diagrams
│   │   ├── branding_diagram.mermaid
│   │   ├── catalog_diagram.mermaid
│   │   ├── client_diagram.mermaid
│   │   ├── core_diagram.mermaid
│   │   ├── quote_diagram.mermaid
│   │   ├── user_class_diagram.mermaid
│   │   └── user_diagram.mermaid
│   ├── doc
│   │   └── classes
│   │       └── quote
│   │           ├── classes_quote_arch_lr.png
│   │           ├── classes_quote_arch_packages.png
│   │           ├── classes_quote_arch.dot
│   │           ├── packages_quote_arch_packages.png
│   │           ├── packages_quote_arch.dot
│   │           └── packages_quote_arch.png
│   ├── Dockerfile
│   ├── generate_diagrams.py
│   ├── logs
│   │   └── app.log
│   ├── manage.py
│   ├── management
│   │   ├── __init__.py
│   │   └── commands
│   │       ├── __init__.py
│   │       └── generate_mermaid.py
│   ├── media
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── requirements
│   │   ├── dev-requirements.txt
│   │   └── requirements.txt
│   ├── setup.cfg
│   ├── static
│   ├── staticfiles
│   │   ├── admin
│   │   │   ├── css
│   │   │   │   ├── autocomplete.css
│   │   │   │   ├── base.css
│   │   │   │   ├── changelists.css
│   │   │   │   ├── dark_mode.css
│   │   │   │   ├── dashboard.css
│   │   │   │   ├── forms.css
│   │   │   │   ├── login.css
│   │   │   │   ├── nav_sidebar.css
│   │   │   │   ├── responsive_rtl.css
│   │   │   │   ├── responsive.css
│   │   │   │   ├── rtl.css
│   │   │   │   ├── unusable_password_field.css
│   │   │   │   ├── vendor
│   │   │   │   │   └── select2
│   │   │   │   │       ├── LICENSE-SELECT2.md
│   │   │   │   │       ├── select2.css
│   │   │   │   │       └── select2.min.css
│   │   │   │   └── widgets.css
│   │   │   ├── img
│   │   │   │   ├── calendar-icons.svg
│   │   │   │   ├── gis
│   │   │   │   │   ├── move_vertex_off.svg
│   │   │   │   │   └── move_vertex_on.svg
│   │   │   │   ├── icon-addlink.svg
│   │   │   │   ├── icon-alert.svg
│   │   │   │   ├── icon-calendar.svg
│   │   │   │   ├── icon-changelink.svg
│   │   │   │   ├── icon-clock.svg
│   │   │   │   ├── icon-deletelink.svg
│   │   │   │   ├── icon-hidelink.svg
│   │   │   │   ├── icon-no.svg
│   │   │   │   ├── icon-unknown-alt.svg
│   │   │   │   ├── icon-unknown.svg
│   │   │   │   ├── icon-viewlink.svg
│   │   │   │   ├── icon-yes.svg
│   │   │   │   ├── inline-delete.svg
│   │   │   │   ├── LICENSE
│   │   │   │   ├── README.txt
│   │   │   │   ├── search.svg
│   │   │   │   ├── selector-icons.svg
│   │   │   │   ├── sorting-icons.svg
│   │   │   │   ├── tooltag-add.svg
│   │   │   │   └── tooltag-arrowright.svg
│   │   │   └── js
│   │   │       ├── actions.js
│   │   │       ├── admin
│   │   │       │   ├── DateTimeShortcuts.js
│   │   │       │   └── RelatedObjectLookups.js
│   │   │       ├── autocomplete.js
│   │   │       ├── calendar.js
│   │   │       ├── cancel.js
│   │   │       ├── change_form.js
│   │   │       ├── core.js
│   │   │       ├── filters.js
│   │   │       ├── inlines.js
│   │   │       ├── jquery.init.js
│   │   │       ├── nav_sidebar.js
│   │   │       ├── popup_response.js
│   │   │       ├── prepopulate_init.js
│   │   │       ├── prepopulate.js
│   │   │       ├── SelectBox.js
│   │   │       ├── SelectFilter2.js
│   │   │       ├── theme.js
│   │   │       ├── unusable_password_field.js
│   │   │       ├── urlify.js
│   │   │       └── vendor
│   │   │           ├── jquery
│   │   │           │   ├── jquery.js
│   │   │           │   ├── jquery.min.js
│   │   │           │   └── LICENSE.txt
│   │   │           ├── select2
│   │   │           │   ├── i18n
│   │   │           │   │   ├── af.js
│   │   │           │   │   ├── ar.js
│   │   │           │   │   ├── az.js
│   │   │           │   │   ├── bg.js
│   │   │           │   │   ├── bn.js
│   │   │           │   │   ├── bs.js
│   │   │           │   │   ├── ca.js
│   │   │           │   │   ├── cs.js
│   │   │           │   │   ├── da.js
│   │   │           │   │   ├── de.js
│   │   │           │   │   ├── dsb.js
│   │   │           │   │   ├── el.js
│   │   │           │   │   ├── en.js
│   │   │           │   │   ├── es.js
│   │   │           │   │   ├── et.js
│   │   │           │   │   ├── eu.js
│   │   │           │   │   ├── fa.js
│   │   │           │   │   ├── fi.js
│   │   │           │   │   ├── fr.js
│   │   │           │   │   ├── gl.js
│   │   │           │   │   ├── he.js
│   │   │           │   │   ├── hi.js
│   │   │           │   │   ├── hr.js
│   │   │           │   │   ├── hsb.js
│   │   │           │   │   ├── hu.js
│   │   │           │   │   ├── hy.js
│   │   │           │   │   ├── id.js
│   │   │           │   │   ├── is.js
│   │   │           │   │   ├── it.js
│   │   │           │   │   ├── ja.js
│   │   │           │   │   ├── ka.js
│   │   │           │   │   ├── km.js
│   │   │           │   │   ├── ko.js
│   │   │           │   │   ├── lt.js
│   │   │           │   │   ├── lv.js
│   │   │           │   │   ├── mk.js
│   │   │           │   │   ├── ms.js
│   │   │           │   │   ├── nb.js
│   │   │           │   │   ├── ne.js
│   │   │           │   │   ├── nl.js
│   │   │           │   │   ├── pl.js
│   │   │           │   │   ├── ps.js
│   │   │           │   │   ├── pt-BR.js
│   │   │           │   │   ├── pt.js
│   │   │           │   │   ├── ro.js
│   │   │           │   │   ├── ru.js
│   │   │           │   │   ├── sk.js
│   │   │           │   │   ├── sl.js
│   │   │           │   │   ├── sq.js
│   │   │           │   │   ├── sr-Cyrl.js
│   │   │           │   │   ├── sr.js
│   │   │           │   │   ├── sv.js
│   │   │           │   │   ├── th.js
│   │   │           │   │   ├── tk.js
│   │   │           │   │   ├── tr.js
│   │   │           │   │   ├── uk.js
│   │   │           │   │   ├── vi.js
│   │   │           │   │   ├── zh-CN.js
│   │   │           │   │   └── zh-TW.js
│   │   │           │   ├── LICENSE.md
│   │   │           │   ├── select2.full.js
│   │   │           │   └── select2.full.min.js
│   │   │           └── xregexp
│   │   │               ├── LICENSE.txt
│   │   │               ├── xregexp.js
│   │   │               └── xregexp.min.js
│   │   ├── django_extensions
│   │   │   ├── css
│   │   │   │   └── jquery.autocomplete.css
│   │   │   ├── img
│   │   │   │   └── indicator.gif
│   │   │   └── js
│   │   │       ├── jquery.ajaxQueue.js
│   │   │       ├── jquery.autocomplete.js
│   │   │       └── jquery.bgiframe.js
│   │   └── rest_framework
│   │       ├── css
│   │       │   ├── bootstrap-theme.min.css
│   │       │   ├── bootstrap-theme.min.css.map
│   │       │   ├── bootstrap-tweaks.css
│   │       │   ├── bootstrap.min.css
│   │       │   ├── bootstrap.min.css.map
│   │       │   ├── default.css
│   │       │   ├── font-awesome-4.0.3.css
│   │       │   └── prettify.css
│   │       ├── docs
│   │       │   ├── css
│   │       │   │   ├── base.css
│   │       │   │   ├── highlight.css
│   │       │   │   └── jquery.json-view.min.css
│   │       │   ├── img
│   │       │   │   ├── favicon.ico
│   │       │   │   └── grid.png
│   │       │   └── js
│   │       │       ├── api.js
│   │       │       ├── highlight.pack.js
│   │       │       └── jquery.json-view.min.js
│   │       ├── fonts
│   │       │   ├── fontawesome-webfont.eot
│   │       │   ├── fontawesome-webfont.svg
│   │       │   ├── fontawesome-webfont.ttf
│   │       │   ├── fontawesome-webfont.woff
│   │       │   ├── glyphicons-halflings-regular.eot
│   │       │   ├── glyphicons-halflings-regular.svg
│   │       │   ├── glyphicons-halflings-regular.ttf
│   │       │   ├── glyphicons-halflings-regular.woff
│   │       │   └── glyphicons-halflings-regular.woff2
│   │       ├── img
│   │       │   ├── glyphicons-halflings-white.png
│   │       │   ├── glyphicons-halflings.png
│   │       │   └── grid.png
│   │       └── js
│   │           ├── ajax-form.js
│   │           ├── bootstrap.min.js
│   │           ├── coreapi-0.1.1.js
│   │           ├── csrf.js
│   │           ├── default.js
│   │           ├── jquery-3.7.1.min.js
│   │           ├── load-ajax-form.js
│   │           └── prettify-min.js
│   ├── swagger.yaml
│   ├── templates
│   │   └── quote
│   │       └── pdf
│   │           ├── document.html
│   │           └── preview.html
│   └── tools
│       ├── areas.csv
│       ├── generate_csv.py
│       ├── import_catalog.py
│       ├── jsons
│       │   ├── areas.json
│       │   └── prestations.json
│       └── prestations.csv
├── CHANGELOG.md
├── CLAUDE.md
├── coverage.xml
├── database
│   ├── dumps
│   │   └── dump_local_20251120_094504.sql
│   └── init
├── docker-compose.certbot.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── docs
│   ├── architecture
│   │   ├── architecture.md
│   │   ├── bc_branding.md
│   │   ├── bc_catalog.md
│   │   ├── bc_client.md
│   │   ├── bc_core.md
│   │   ├── bc_email.md
│   │   ├── bc_quote.md
│   │   ├── bc_user.md
│   │   ├── decisions
│   │   │   └── ADR-001-cross-context-repository-dependencies.md
│   │   ├── template_bounded_context.md
│   │   └── work
│   │       ├── account_phase1_domain.md
│   │       ├── auth_user_refacto.md
│   │       ├── DEPRECATED_FILES_ACCOUNT.md
│   │       ├── legal_terms_v0.md
│   │       ├── subscription_v0.md
│   │       ├── TODO_FAVORITE_PRESTATIONS.md
│   │       └── user_refacto_analysis.md
│   ├── backup.md
│   ├── database_management.md
│   ├── deployment
│   │   ├── backups.md
│   │   ├── build-and-deploy.md
│   │   ├── DEPLOYMENT_MASTER_GUIDE.md
│   │   ├── disaster-recovery.md
│   │   ├── environment-config.md
│   │   ├── monitoring.md
│   │   ├── production-checklist.md
│   │   └── vps-setup.md
│   ├── good-practices
│   │   ├── claud-good-habits.md
│   │   ├── dev-docs-pattern.md
│   │   ├── development.md
│   │   ├── git-workflow.md
│   │   └── paradigms.md
│   ├── knowledge.md
│   ├── knowledge.sh
│   ├── plans
│   │   ├── legal-term-context.md
│   │   ├── Mentions obligatoires sur un devis d’auto-entrepreneur (France).pdf
│   │   └── production-ready.md
│   ├── release
│   │   ├── RELEASE_PLAN_v0.1.0.md
│   │   └── RELEASE_PLAN_v0.2.0.md
│   └── tmp
│       └── errors.txt
├── FreelanSign.code-workspace
├── frontend
│   ├── .dockerignore
│   ├── .env
│   ├── .env.development.local
│   ├── .eslintrc.cjs
│   ├── .gitignore
│   ├── components.json
│   ├── Dockerfile
│   ├── docs
│   │   └── tests
│   │       ├── account_header.feature.md
│   │       ├── account_store.feature.md
│   │       └── use_require_account.feature.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── nginx.conf
│   ├── package-lock.json
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── prettier.config.cjs
│   ├── public
│   │   ├── img
│   │   │   ├── default-avatar.jpeg
│   │   │   └── logo.png
│   │   └── vite.svg
│   ├── README.md
│   ├── src
│   │   ├── app
│   │   │   ├── providers
│   │   │   │   └── AuthProvider.tsx
│   │   │   └── router.tsx
│   │   ├── App.css
│   │   ├── assets
│   │   │   ├── fonts
│   │   │   │   ├── FiraCode-Bold.ttf
│   │   │   │   ├── FiraCode-Regular.ttf
│   │   │   │   ├── PlayfairDisplay-Bold.ttf
│   │   │   │   ├── PlayfairDisplay-Regular.ttf
│   │   │   │   └── PlayfairDisplay-SemiBold.ttf
│   │   │   ├── icons
│   │   │   │   └── pen-nib-line.svg
│   │   │   └── react.svg
│   │   ├── components
│   │   │   └── ui
│   │   │       ├── button.tsx
│   │   │       ├── dialog.tsx
│   │   │       └── textarea.tsx
│   │   ├── domain
│   │   │   ├── account
│   │   │   │   └── types.ts
│   │   │   ├── auth
│   │   │   │   └── usecases.ts
│   │   │   ├── catalog
│   │   │   │   └── types.ts
│   │   │   ├── client
│   │   │   │   └── types.ts
│   │   │   ├── common
│   │   │   │   └── pagination.ts
│   │   │   ├── quote
│   │   │   │   ├── mappers.ts
│   │   │   │   └── types.ts
│   │   │   ├── types.ts
│   │   │   └── user
│   │   │       └── types.ts
│   │   ├── infrastructure
│   │   │   ├── account
│   │   │   │   ├── accountContext.ts
│   │   │   │   ├── accountRepository.ts
│   │   │   │   └── accountStore.ts
│   │   │   ├── api.ts
│   │   │   ├── auth
│   │   │   │   └── authRepository.ts
│   │   │   ├── branding
│   │   │   │   └── themeRepository.ts
│   │   │   ├── catalog
│   │   │   │   └── catalogRepository.ts
│   │   │   ├── client
│   │   │   │   └── clientRepository.ts
│   │   │   ├── email
│   │   │   │   └── emailRepository.ts
│   │   │   ├── http
│   │   │   │   └── apiClient.ts
│   │   │   ├── quote
│   │   │   │   └── quoteRepository.ts
│   │   │   ├── storage
│   │   │   │   └── tokenStorage.ts
│   │   │   └── user
│   │   │       └── userRepository.ts
│   │   ├── interface
│   │   │   ├── components
│   │   │   │   ├── account
│   │   │   │   │   └── AccountDataForm.tsx
│   │   │   │   ├── AppToBar.tsx
│   │   │   │   ├── auth
│   │   │   │   │   ├── request-password-reset-form.module.css
│   │   │   │   │   ├── RequestPasswordResetForm.tsx
│   │   │   │   │   ├── reset-password-form.module.css
│   │   │   │   │   └── ResetPasswordForm.tsx
│   │   │   │   ├── branding
│   │   │   │   │   └── ThemesForm.tsx
│   │   │   │   ├── client
│   │   │   │   │   ├── client-create-drawer.module.css
│   │   │   │   │   └── ClientCreateDrawer.tsx
│   │   │   │   ├── common
│   │   │   │   │   ├── card.module.css
│   │   │   │   │   ├── Card.tsx
│   │   │   │   │   ├── confirm-modal.module.css
│   │   │   │   │   ├── ConfirmModal.tsx
│   │   │   │   │   ├── Modal.css
│   │   │   │   │   └── Modal.tsx
│   │   │   │   ├── email
│   │   │   │   │   ├── quote-email-preview-dialog.module.css
│   │   │   │   │   └── QuoteEmailPreviewDialog.tsx
│   │   │   │   ├── footer
│   │   │   │   │   ├── footer.module.css
│   │   │   │   │   └── Footer.tsx
│   │   │   │   ├── login
│   │   │   │   │   ├── login-form.module.css
│   │   │   │   │   └── LoginForm.tsx
│   │   │   │   ├── navbar
│   │   │   │   │   ├── Navbar.module.css
│   │   │   │   │   └── Navbar.tsx
│   │   │   │   ├── profile
│   │   │   │   │   ├── PersonalUserDataForm.tsx
│   │   │   │   │   ├── PrestationSelector.tsx
│   │   │   │   │   ├── ProfessionalInfoForm.tsx
│   │   │   │   │   └── ProfessionalUserDataForm.tsx
│   │   │   │   ├── quote
│   │   │   │   │   ├── PdfPreviewPane.tsx
│   │   │   │   │   └── QuotesTable.tsx
│   │   │   │   ├── register
│   │   │   │   │   ├── register-form.module.css
│   │   │   │   │   └── RegisterForm.tsx
│   │   │   │   └── sidebar
│   │   │   │       ├── sidebar.module.css
│   │   │   │       └── Sidebar.tsx
│   │   │   ├── hooks
│   │   │   │   ├── useDebouncedValue.ts
│   │   │   │   ├── usePdfPreview.ts
│   │   │   │   ├── useRequireAccount.ts
│   │   │   │   └── useThemes.ts
│   │   │   ├── layout
│   │   │   │   ├── main-layout.module.css
│   │   │   │   ├── MainLayout.tsx
│   │   │   │   └── RootSeo.tsx
│   │   │   ├── pages
│   │   │   │   ├── Account
│   │   │   │   │   └── AccountOnboardingPage.tsx
│   │   │   │   ├── Auth
│   │   │   │   │   ├── request-password-reset.module.css
│   │   │   │   │   ├── request-password-reset.tsx
│   │   │   │   │   └── reset-password.tsx
│   │   │   │   ├── Branding
│   │   │   │   │   ├── themes.module.css
│   │   │   │   │   ├── ThemesCreatePage.tsx
│   │   │   │   │   ├── ThemesEditPage.tsx
│   │   │   │   │   └── ThemesListPage.tsx
│   │   │   │   ├── dashboard.module.css
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── Login
│   │   │   │   │   ├── LoginPage.module.css
│   │   │   │   │   └── LoginPage.tsx
│   │   │   │   ├── Profile
│   │   │   │   │   ├── profile-edit-page.module.css
│   │   │   │   │   ├── profile-page.module.css
│   │   │   │   │   ├── ProfileEditPage.tsx
│   │   │   │   │   └── ProfilePage.tsx
│   │   │   │   ├── Quote
│   │   │   │   │   ├── quote-detail.module.css
│   │   │   │   │   ├── quote-edit-create.module.css
│   │   │   │   │   ├── QuoteCreatePage.tsx
│   │   │   │   │   ├── QuoteDetailPage.tsx
│   │   │   │   │   ├── QuoteEditPage.tsx
│   │   │   │   │   ├── QuoteListPage.tsx
│   │   │   │   │   └── quotes-list.module.css
│   │   │   │   └── Register
│   │   │   │       ├── RegisterPage.module.css
│   │   │   │       └── RegisterPage.tsx
│   │   │   └── utils
│   │   │       ├── branding.ts
│   │   │       └── saveFile.ts
│   │   ├── lib
│   │   │   ├── api
│   │   │   │   └── auth.ts
│   │   │   ├── constants
│   │   │   │   └── site.config.ts
│   │   │   └── utils.ts
│   │   ├── main.tsx
│   │   ├── shared
│   │   │   ├── apiErrors.ts
│   │   │   ├── endpoints.ts
│   │   │   ├── env.ts
│   │   │   └── utils
│   │   │       └── obj.ts
│   │   ├── styles
│   │   │   └── index.css
│   │   ├── tests
│   │   │   ├── accountStore.test.ts
│   │   │   ├── apiClient.account-header.test.ts
│   │   │   ├── noAccount_ProfileEditPage.test.tsx
│   │   │   ├── noAccount_ProfilePage.test.tsx
│   │   │   └── useRequireAccount.test.tsx
│   │   └── vite-env.d.ts
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── LICENSE
├── logo.png
├── logrotate.conf
├── logs
│   └── app.log
├── Makefile
├── package.json
├── pnpm-lock.yaml
├── postgres.conf
├── release.md
├── scripts
│   ├── backup.sh
│   ├── db-dump.sh
│   ├── db-restore.sh
│   ├── load-env.sh
│   ├── precommit.sh
│   └── restore.sh
├── sonar-project.properties
└── typings
    └── rest_framework
        ├── __init__.pyi
        ├── compat.pyi
        ├── settings.pyi
        ├── test
        └── test.pyi

290 directories, 879 files
```
<!-- END AUTO: PROJECT_STRUCTURE -->

## Frontend package.json
<!-- BEGIN AUTO: FRONTEND_PACKAGE_JSON -->
Path: `/Users/bertrandrenaudin/Desktop/DEV/FreelanSign/frontend/package.json`
**name**: `frontend`  •  **version**: `0.2.0`
**scripts**: 10  •  **dependencies**: 19  •  **devDependencies**: 29

<details><summary>Top dependencies</summary>

- @headlessui/react: ^2.2.9
- @hookform/resolvers: ^5.2.2
- @radix-ui/react-dialog: ^1.1.15
- @radix-ui/react-slot: ^1.2.4
- @tailwindcss/vite: ^4.1.13
- axios: ^1.12.2
- class-variance-authority: ^0.7.1
- clsx: ^2.1.1
- lucide-react: ^0.544.0
- react: ^19.1.0
- react-color: ^2.19.3
- react-dom: ^19.1.0
- react-helmet-async: ^2.0.5
- react-hook-form: ^7.62.0
- react-hot-toast: ^2.6.0
- react-router-dom: ^7.9.1
- tailwind-merge: ^3.3.1
- tailwindcss: ^4.1.13
- zod: ^4.1.9

</details>

<details><summary>Scripts</summary>

- dev: vite
- build: tsc -b && vite build
- preview: vite preview
- lint: eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix
- lint:check: eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts
- format: prettier --write src/
- format:check: prettier --check src/
- type-check: vue-tsc --noEmit
- test:coverage: vitest run --coverage
- test: vitest

</details>
<!-- END AUTO: FRONTEND_PACKAGE_JSON -->

## Backend package.json
<!-- BEGIN AUTO: BACKEND_PACKAGE_JSON -->
Path: `/Users/bertrandrenaudin/Desktop/DEV/FreelanSign/backend/package.json`
_No package.json found at /Users/bertrandrenaudin/Desktop/DEV/FreelanSign/backend/package.json_
<!-- END AUTO: BACKEND_PACKAGE_JSON -->

## Django models (scan)
<!-- BEGIN AUTO: DJANGO_MODELS -->
| Model | File |
|---|---|
| `BrandTheme` | `apps/branding/models.py` |
| `Client` | `apps/client/models.py` |
| `LegalTemplateModel` | `apps/legal_terms/adapters/persistence/models.py` |
| `LegalProfileModel` | `apps/legal_terms/adapters/persistence/models.py` |
| `AttachedTermsModel` | `apps/legal_terms/adapters/persistence/models.py` |
| `PaymentTerms` | `apps/quote/models.py` |
| `Quote` | `apps/quote/models.py` |
| `QuoteLineItem` | `apps/quote/models.py` |
| `QuoteHistory` | `apps/quote/models.py` |
| `Profile` | `apps/user/models/models.py` |
<!-- END AUTO: DJANGO_MODELS -->

---

_Last updated_
<!-- BEGIN AUTO: LAST_UPDATED -->
_Updated_: **2025-12-05 10:10:20 CET**
<!-- END AUTO: LAST_UPDATED -->
