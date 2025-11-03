# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.user.interface.auth_views import AuthLoginView, AuthLogoutView, SecureAuthRefreshView

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
    path("api/auth/login/", AuthLoginView.as_view(), name="auth_login"),
    path("api/auth/refresh/", SecureAuthRefreshView.as_view(), name="auth_refresh"),
    path("api/auth/logout/", AuthLogoutView.as_view(), name="auth_logout"),
    # Catalog
    path("api/catalog/", include("apps.catalog.interface.urls", namespace="catalog")),
    # Quotes
    path("api/quotes/", include("apps.quote.interface.urls", namespace="quote")),
    # Clients
    path("api/clients/", include("apps.client.interface.urls", namespace="client")),
    # Branding
    path("api/branding/", include("apps.branding.interface.urls", namespace="branding")),
]
