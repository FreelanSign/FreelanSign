# TODO: M2M favorite_prestations

## Contexte

La relation Many-to-Many `Account ↔ Prestation` (favorite_prestations) a été **reportée** des Phases 2-3.

## À implémenter plus tard

### Django Model
```python
class Account(models.Model):
    # ... autres champs
    favorite_prestations = models.ManyToManyField(
        'catalog.Prestation',
        related_name='favorited_by_accounts',
        blank=True
    )
```

### Migration de données
- Copier `ProfessionalUser.service_types` → `Account.favorite_prestations`
- Drop table M2M `user_professionaluser_service_types` après migration

### Repository
- Ajouter méthodes:
  - `add_favorite_prestation(account_id, prestation_id)`
  - `remove_favorite_prestation(account_id, prestation_id)`
  - `get_favorite_prestations(account_id) -> list[Prestation]`

### Use Cases
- `AddFavoritePrestations`
- `RemoveFavoritePrestations`
- `GetFavoritePrestations`

### DTOs
- Ajouter `favorite_prestation_ids: list[int]` dans ViewModels si nécessaire

## Priorité

**Phase future** (v0.3.x ou v0.4.0) - Pas bloquant pour le CRUD Account basique.

## Référence

Issue #54 - Phase 3 mentionnée mais reportée par décision architecture.
