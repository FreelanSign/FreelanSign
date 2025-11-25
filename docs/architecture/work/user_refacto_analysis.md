# User Context Refactoring - Analysis & Suggestions

## 🎯 Objectif de la refacto

Passer de **User → Profile → ProfessionalUser** (1:1:0..1)
À **User → Profile + User → Account** (1:1 + 1:N)

---

## ✅ Points forts de la refacto proposée

### 1. Séparation claire des responsabilités

**Avant** (confus):
- User = auth
- Profile = identité humaine
- ProfessionalUser = données business **mais lié 1:1 au User**

**Après** (clair):
- User = auth uniquement
- Profile = identité humaine (1:1, always exists)
- Account = workspace professionnel (1:N, freelance peut avoir plusieurs entités juridiques)

**Avantage majeur**: Un freelance avec micro-entreprise + SASU = 2 Accounts, 1 User. C'est la vraie vie.

### 2. Account devient l'Aggregate Root métier

```
Account owns:
- Clients
- Quotes
- Custom Prestations
- Branding
- Subscription (futur)
```

**C'est correct**. L'Account est le "tenant" du système. Toutes les entités métier doivent référencer `account_id`, pas `user_id`.

### 3. Vocabulaire métier cohérent

- `ProfessionalUser` → `Account` : Meilleur nom (workspace/tenant pattern)
- `number_pro` → `legal_id` : Plus générique (SIRET/TVA/autre)
- `status_juridique` → `legal_form` : Naming anglais cohérent
- `name` → `display_name` : Plus explicite

---

## ⚠️ Critiques & Risques

### 1. Migration 1:1 → 1:N = Breaking change majeur

**Impact**:
- Toutes les FK vers `ProfessionalUser` deviennent FK vers `Account`
- Mais surtout: **Client, Quote, Branding doivent pointer vers Account, pas User**

**Risque**: Si Client/Quote pointent actuellement vers `User`, il faut:
1. Créer 1 Account par ProfessionalUser existant
2. Migrer toutes les FK `user_id` → `account_id`
3. Gérer les Users sans ProfessionalUser (admin, comptes incomplets)

**Suggestion**: Migration en 3 étapes:
1. Créer Account, garder ProfessionalUser (dual-write)
2. Migrer données, FK duales (`user_id` + `account_id` nullable)
3. Supprimer ProfessionalUser, rendre `account_id` required

### 2. Account.user = OneToOne alors que 1:N annoncé

**Incohérence dans le doc**:
- Texte dit "Un User peut avoir plusieurs Accounts" (1:N)
- Diagram montre `Account → User: one to one`

**Il faut choisir**:

**Option A (1:N recommandée)**:
```python
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="accounts")
```

**Option B (1:1 si pas besoin multi-account)**:
```python
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, related_name="account")
```

**Ma recommandation**: **1:N** (Option A) même si v1 limite à 1 Account. Raisons:
- Freelance qui crée micro puis SASU = use case réel
- SaaS pricing: "plan Pro = 3 Accounts max" facile à implémenter
- Pas de refacto future 1:1 → 1:N (déjà douloureux)

**Mais**: Si 1:N, il faut un **Account actif/contexte courant**:
```python
class User(models.Model):
    active_account = models.ForeignKey(Account, null=True, related_name="+")
```

### 3. Confusion Account vs Subscription

**Doc actuel**:
> Account est lié à un abonnement (subscription) chez FreelanSign

**Question**: Subscription lié à quoi?
- Account? (chaque Account = 1 abonnement)
- User? (User paye pour tous ses Accounts)

**Use case réel**:
- Freelance avec micro (gratuit) + SASU (plan Pro) → 2 subscriptions? ou 1 User subscription avec multi-account?

**Suggestion**: Clarifier maintenant:
```python
# Option 1: Subscription par Account
class Account:
    subscription = ForeignKey(Subscription)

# Option 2: Subscription par User (plus standard SaaS)
class User:
    subscription = ForeignKey(Subscription)
    # subscription.plan.max_accounts = 3
```

**Je recommande Option 2** (Subscription au niveau User):
- Stripe/SaaS classique: 1 customer = 1 User
- Plus simple facturation
- Account = workspace gratuit dans la limite du plan

---

## 🔧 Suggestions techniques

### 1. Value Objects à introduire

**Au lieu de**:
```python
class Account:
    legal_id = models.CharField(max_length=14)  # SIRET?
    legal_form = models.CharField(choices=...)
```

**Suggéré**:
```python
# domain/value_objects.py
@dataclass(frozen=True)
class LegalEntity:
    form: LegalForm  # MICRO, EURL, SASU...
    id: str  # SIRET, TVA, etc.

    def __post_init__(self):
        if self.form == LegalForm.MICRO and not self._is_valid_siret(self.id):
            raise ValueError("Invalid SIRET")

# models.py
class Account:
    legal_entity = models.JSONField()  # Serialize LegalEntity
```

**Avantage**: Validation métier centralisée (SIRET format, TVA validation, etc.)

### 2. Clarifier Profile.role

**Doc actuel**:
```python
class Profile:
    role = models.CharField(choices=[("freelance", "admin")])
```

**Questions**:
- Role global (User level) ou Account level?
- Admin de quoi? FreelanSign staff ou Account owner?

**Suggestions**:

**Si role = permission globale**:
```python
class User:
    role = models.CharField(choices=[("user", "staff", "superuser")])
    # is_staff/is_superuser deprecated, use role
```

**Si role = Account permission (multi-user Account futur)**:
```python
class AccountMembership:
    account = ForeignKey(Account)
    user = ForeignKey(User)
    role = CharField(choices=[("owner", "editor", "viewer")])
```

**Ma recommandation**: Si v1 = 1 User = 1 Account owner, garder simple:
```python
class Account:
    owner = ForeignKey(User, related_name="owned_accounts")
    # Pas de role, owner a tous les droits sur son Account
```

Ajouter AccountMembership plus tard si besoin multi-user.

### 3. Prestations: Account.services_types confusion

**Doc montre**:
```
Account → Prestation (M2M) "services_types"
Account → Prestation (1:N) "custom_prestations"
Prestation → Account (N:1) "owner_account"
```

**Incohérence**:
- `Account.services_types` = Prestations du catalogue global choisies?
- `custom_prestations` = Prestations custom créées par Account?
- `Prestation.owner_account` = Account qui a créé cette Prestation custom?

**Suggestion de clarification**:

```python
class Prestation:
    area = ForeignKey(Area)
    name = models.CharField()
    is_custom = models.BooleanField(default=False)
    created_by_account = ForeignKey(Account, null=True)  # null si global catalog

class Account:
    # Pas de M2M services_types
    # Les prestations disponibles = Prestation.filter(
    #   Q(is_custom=False) | Q(created_by_account=self)
    # )
```

**Ou** si vraiment besoin M2M (Account choisit ses prestations favorites du catalogue):
```python
class Account:
    favorite_prestations = M2M(Prestation, limit_choices_to={"is_custom": False})
    # custom_prestations = reverse FK via Prestation.created_by_account
```

---

## 🎯 Règles métier à ajouter

### BR-ACCOUNT-001
**Un User doit avoir au moins 1 Account actif pour créer Client/Quote**

**Validation**: Middleware/permission check Account exists avant accès aux features.

### BR-ACCOUNT-002
**TJM est défini au niveau Account, pas User**

**Impact**: Quote doit utiliser `account.tjm_cents` comme default, pas `user.professional.tjm_cents`.

### BR-ACCOUNT-003
**Account.display_name est unique par User** (éviter "Micro-Entreprise" x10)

**Validation**:
```python
class Account:
    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "display_name"], name="unique_account_name_per_user")
        ]
```

### BR-ACCOUNT-004
**Seul l'owner d'un Account peut le modifier/supprimer**

**Permission**: `IsAccountOwner` custom permission.

---

## 📋 Migration checklist (si refacto validée)

### Phase 1: Création Account (non-breaking)
- [ ] Créer modèle Account (avec `user` ForeignKey)
- [ ] Signal: `post_save(ProfessionalUser)` → créer Account dual
- [ ] Migration données: 1 ProfessionalUser → 1 Account
- [ ] Tests: vérifier Account.tjm_cents = ProfessionalUser.tjm_cents

### Phase 2: Migration FK (breaking)
- [ ] Ajouter `account_id` nullable sur Client, Quote, Branding
- [ ] Migration: remplir `account_id` via `user.professional.account`
- [ ] Dual write: créer Client avec `account_id` ET garder `user_id`
- [ ] Tests E2E avec nouveau flow

### Phase 3: Cleanup (breaking)
- [ ] Rendre `account_id` required sur Client/Quote/Branding
- [ ] Supprimer `user_id` de ces modèles (breaking!)
- [ ] Supprimer ProfessionalUser modèle
- [ ] Mettre à jour serializers/views/repos
- [ ] Migration frontend (API change)

### Phase 4: Multi-account (optionnel v2)
- [ ] Ajouter `User.active_account_id`
- [ ] UI: switcher d'Account
- [ ] Permissions: check Account ownership

---

## 🤔 Questions non résolues

1. **User sans Account**: Autorisé? (compte incomplet, admin staff)
   → Si oui, toutes les features métier doivent gracefully handle `user.accounts.count() == 0`

2. **Suppression Account**: Cascade ou soft delete? Impact sur Clients/Quotes liés?
   → Recommandation: soft delete avec `is_active=False`, bloquer suppression si quotes exists

3. **Area optionnel sur Account**: Pourquoi optionnel?
   → Si Account sans domaine, impact sur catalog filtering? Clarifier use case

4. **Profile.birthday**: Utilisé où? RGPD risk si pas nécessaire métier
   → Envisager suppression si pas d'use case clair

5. **Avatar storage**: URLField vs FileField/S3?
   → URLField OK si avatars = Gravatar/externe, sinon migrer vers FileField

---

## 🎬 Verdict

**Refacto nécessaire**: ✅ Oui, ProfessionalUser 1:1 est une impasse métier

**Priorité**: 🔴 Haute (avant d'accumuler plus de données legacy)

**Complexité**: 🟡 Moyenne (migration data OK, mais breaking changes API/frontend)

**Risque**: 🟢 Faible si migration 3 phases + tests (downtime minimal)

**Recommandations finales**:
1. Valider dès maintenant User 1:N Account (pas 1:1)
2. Clarifier Subscription au niveau User, pas Account
3. Simplifier Prestations relations (supprimer M2M services_types si pas d'use case clair)
4. Ajouter `User.active_account` pour contexte courant
5. Migrer en 3 phases avec feature flags (éviter big bang)

**Timeline suggérée**:
- Phase 1 (Account creation): 2-3j dev + tests
- Phase 2 (FK migration): 3-5j dev + migration script robuste
- Phase 3 (Cleanup): 2j dev + coordination frontend
- Total: ~10j avec tests, docs, review

**Bloquant avant de commencer**:
- Décision User 1:1 ou 1:N Account
- Décision Subscription level (User ou Account)
- Validation impact frontend (toutes les API calls changent)
