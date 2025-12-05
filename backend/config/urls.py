# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check endpoint
    path("api/health/", health_check, name="health-check"),
    # OpenAPI schema & Swagger UI en public
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny], authentication_classes=[]),
        name="docs",
    ),
    # API users
    path("api/user/", include("apps.user.urls")),
    # Auth endpoints
    path("api/auth/", include("apps.user.interface.auth_urls")),
    # Catalog
    path("api/catalog/", include("apps.catalog.interface.urls")),
    # Quotes
    path("api/quotes/", include("apps.quote.interface.urls")),
    # Clients
    path("api/clients/", include("apps.client.interface.urls")),
    # Branding
    path("api/branding/", include("apps.branding.interface.urls")),
    # Email
    path("api/", include("apps.email.interface.urls")),
    # Legal Terms
    path("api/legal-terms/", include("apps.legal_terms.interface.urls")),
]
