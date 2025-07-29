# apps/users/urls.py
from django.urls import path, include

app_name = 'user'

urlpatterns = [
    # on inclut simplement les routes de interface/urls.py
    path('', include('apps.user.interface.urls')),
]
