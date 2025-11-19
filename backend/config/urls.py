# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

urlpatterns = [
    path("admin/", admin.site.urls),
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
    # Votre API users
    path("api/user/", include("apps.user.urls", namespace="user")),
    # Auth endpoints
    path("api/auth/", include("apps.user.interface.auth_urls")),
    # Catalog
    path("api/catalog/", include("apps.catalog.interface.urls", namespace="catalog")),
    # Quotes
    path("api/quotes/", include("apps.quote.interface.urls", namespace="quote")),
    # Clients
    path("api/clients/", include("apps.client.interface.urls", namespace="client")),
    # Branding
    path("api/branding/", include("apps.branding.interface.urls", namespace="branding")),
    path("api/", include("apps.email.interface.urls", namespace="email")),
]
