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

#### Version Control & Release Strategy
- Use tags in Git to mark releases: v1.0.0, v1.1.0, etc.
- Automate changelog generation if possible (tools like conventional-changelog).
- Review the commit history for the release branch to determine version bump (PATCH/MINOR/MAJOR).
- Post-release, merge back hotfix or release branch into develop (if branching model uses it).
- Ensure that after a release, main always reflects the production version and develop (if any) includes ongoing work.
- Protect main (and develop) branches: require pull request, code review, passing CI, and correct commit messages before merging.

---

In summary: Adopting the Conventional Commit standard promotes clarity, quality and traceability. For a collaborative project like Freelansign, following these rules will make your commit history meaningful, your releases predictable, and your codebase easier to maintain.
