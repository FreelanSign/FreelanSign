# apps/quote/__init__.py
"""
Quote bounded context.

DESIGN: Simplified Architecture
================================
Quote uses a SIMPLER architecture than Account:
- NO domain layer (no entities) - works directly with Django models
- Has application layer (use cases, DTOs)
- Has adapters layer (repositories)
- Has interface layer (serializers, views)

Rationale:
- Quote was implemented before full Clean Architecture adoption
- Django model is simple enough (no complex business rules in entity)
- Domain logic lives in:
  * domain/policies/ (TaxPolicy, StatusPolicy)
  * domain/services/ (TotalsService)
- Entity-level validation not needed (handled by model + serializers)

vs Account which follows full Clean Architecture:
  domain/ → entities + value objects
  application/ → use cases + DTOs + ports
  adapters/ → persistence
  interface/ → API

TODO (v0.3+): Consider adding Quote entity if business logic grows complex.

@since: 2025-11-29
@author: @Bertrand2808
"""

default_app_config = "apps.quote.apps.QuoteConfig"
