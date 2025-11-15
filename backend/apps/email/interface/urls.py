# apps/email/interface/urls.py
from django.urls import path

from .views import prepared_email_view

app_name = "email"

urlpatterns = [
    path("quote/<uuid:quote_id>/prepared-email", prepared_email_view, name="prepared-email"),
]
