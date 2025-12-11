# Core Services – @core/services/

This directory contains cross-cutting service helpers used across bounded contexts.
Keep these modules small, focused, and framework-aware (they can depend on Django/DRF).

## Audit Service (`audit.py`)

Central helper for GDPR-oriented audit logging.
Do **not** call `AuditLog.objects.create(...)` directly outside this module.

### Canonical helper

```python
from apps.core.services.audit import log_audit
from apps.core.models.audit import AuditLog

log_audit(
    action=AuditLog.Action.ACCOUNT_CREATED,  # always use enum, not raw strings
    actor=request.user,                      # can be None for async jobs
    target_model="Account",                  # stable logical label ("Account", "Client", "Quote", ...)
    target_id=account.pk,                    # any PK, will be cast to str
    request=request,                         # optional, used to derive IP
    metadata={"display_name": account.display_name},  # minimal contextual fields
)
