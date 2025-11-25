# Fichiers Obsolètes - Refactorisation Account

Ce document liste les fichiers qui seront obsolètes ou modifiés après la refactorisation complète `ProfessionalUser → Account`.

## ⚠️ Statut: Planification

Ce document reflète les fichiers qui **SERONT** obsolètes après les Phases 3-6. Actuellement (Phase 2), ces fichiers sont **ENCORE UTILISÉS**.

---

## Phase 6: Fichiers à Supprimer

### Models Django

**Fichier**: `backend/apps/user/models/models.py`

**Classe obsolète**: `ProfessionalUser`
- **Raison**: Remplacé par `Account`
- **Migration**: Phase 3 (migration données + drop table)
- **Impact**: Relations avec Quote/Client/BrandTheme/Prestation à migrer

---

### Views/API Endpoints

**Fichier**: `backend/apps/user/interface/views.py`

**Endpoints obsolètes**:
- `ProfessionalUserMeView` (GET `/api/users/professional/me/`)
- `OnboardingProfessionalView` (POST `/api/users/professional/onboarding/`)

**Raison**: Remplacés par `/api/accounts/` endpoints
**Migration**: Phase 4 (nouvelle AccountViewSet)

---

### Serializers

**Fichier**: `backend/apps/user/interface/serializers.py`

**Serializers obsolètes**:
- `ProfessionalOutputSerializer`
- `ProfessionalInputSerializer`
- `OnboardingProfessionalSerializer`

**Raison**: Remplacés par `AccountOutputSerializer` / `AccountInputSerializer`
**Migration**: Phase 4

---

### Permissions

**Fichier**: `backend/apps/branding/interface/permissions.py` (ou équivalent)

**Permission obsolète**: `IsProfessionalUser`

**Raison**: Remplacé par `HasAccountContext` + `IsAccountOwner`
**Migration**: Phase 5.3 (Branding context)

---

### Frontend - API Calls

**Fichiers concernés**:
- `frontend/src/infrastructure/repositories/UserRepository.ts` (ou équivalent)
- `frontend/src/interface/pages/Onboarding*.tsx`

**Appels API obsolètes**:
- `GET /api/users/professional/me/`
- `POST /api/users/professional/onboarding/`

**Raison**: Remplacés par:
- `GET /api/accounts/`
- `POST /api/accounts/`

**Migration**: Phase 7

---

### Frontend - State Management

**Fichiers à modifier/supprimer**:
- Stores gérant `professionalUser` state
- Components affichant `professional.name`, `professional.tjm`, etc.

**Raison**: Remplacé par `accountStore` avec Account entity
**Migration**: Phase 7

---

## Phase 6: Champs de Modèles à Supprimer

### User Model

**Fichier**: `backend/apps/user/models/models.py`

**Champs obsolètes**:
- `full_name` → déplacé dans `Profile`
- `phone` → déplacé dans `Profile`

**Raison**: Duplication entre User et Profile
**Migration**: Phase 6 (drop columns)

---

### Profile Model

**Fichier**: `backend/apps/user/models/models.py`

**Champ obsolète**:
- `birthday: Date`

**Raison**: RGPD + pas d'use case métier
**Migration**: Phase 6 (drop column)

---

## Relations M2M à Renommer

### Catalog - Prestation

**Fichier**: `backend/apps/catalog/models.py`

**Champ obsolète**: `Prestation.professional_user` (FK)

**Nouveau nom**: `Prestation.account`
**Migration**: Phase 5.4

**Table M2M obsolète**: `service_types`

**Nouvelle table**: `favorite_prestations`
**Migration**: Phase 3

---

## Frontend - Components Obsolètes

### Onboarding

**Fichiers**:
- `frontend/src/interface/pages/OnboardingProfessional.tsx` (ou équivalent)
- `frontend/src/interface/components/ProfessionalForm.tsx`

**Raison**: Formulaire change (`ProfessionalUser` → `Account`)
**Migration**: Phase 7 (nouveaux components AccountForm)

---

### Account Switcher (v2 only)

**Note**: En v1 (1:1 User:Account), pas besoin de switcher
En v2 (1:N), il faudra:
- Account switcher UI (dropdown header)
- `activeAccountId` dans state
- Middleware `X-Account-Id` header

---

## Comment Vérifier les Fichiers Obsolètes

Avant de supprimer en Phase 6:

```bash
# Rechercher références ProfessionalUser
grep -r "ProfessionalUser" backend/ --exclude-dir=migrations

# Rechercher appels API obsolètes
grep -r "/api/users/professional" frontend/

# Rechercher service_types M2M
grep -r "service_types" backend/
```

---

## Timeline de Suppression

| Phase | Fichiers/Code à Supprimer |
|-------|---------------------------|
| Phase 3 | Migrations données (ProfessionalUser → Account) |
| Phase 4 | ❌ Rien (ajout Account API, garde professionalUser) |
| Phase 5 | Cross-app migrations (Quote/Client/Branding owns Account) |
| **Phase 6** | **DROP ProfessionalUser model/table** |
| **Phase 6** | **DROP serializers/views/permissions** |
| **Phase 6** | **DROP Profile.birthday, User.phone, User.full_name** |
| Phase 7 | Frontend cleanup (calls, state, components) |

---

## Risques

> [!WARNING]
> **Ne PAS supprimer avant Phase 6** - Risque de casser l'app

> [!CAUTION]
> **Chercher références cachées**:
> - Tests E2E qui appellent `/professional/me/`
> - Scripts admin qui utilisent `ProfessionalUser`
> - Documentation avec anciens endpoints

---

## Feature Flag de Rollback

**Variable**: `ENABLE_ACCOUNT_MODEL` (settings.py)

- `True` → Utilise Account (v2)
- `False` → Rollback vers ProfessionalUser (v1)

**Permet**: Retour arrière sans redéployer si bugs critiques Phase 4-5.
