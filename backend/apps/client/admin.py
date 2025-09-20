# apps/client/admin.py
from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "email")
    search_fields = ("name", "email", "vat_number")
