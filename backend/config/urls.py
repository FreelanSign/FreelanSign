# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI schema & Swagger UI en public
    path(
        'api/schema/',
        SpectacularAPIView.as_view(
            permission_classes=[AllowAny],
            authentication_classes=[]
        ),
        name='schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema',
            permission_classes=[AllowAny],
            authentication_classes=[]
        ),
        name='docs'
    ),

    # Votre API users
    path('api/user/', include('apps.user.urls', namespace='user')),
]
