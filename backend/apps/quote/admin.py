# apps/quote/admin.py
from django.contrib import admin
from .models import Quote, QuoteLineItem, QuoteHistory, PaymentTerms

class QuoteLineItemInline(admin.TabularInline):
    model = QuoteLineItem
    extra = 0

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("reference", "owner", "client", "status", "issue_date", "total", "currency")
    list_filter = ("status", "currency")
    search_fields = ("reference", "title", "client__name")
    inlines = [QuoteLineItemInline]

@admin.register(PaymentTerms)
class PaymentTermsAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "days", "updated_at")
    search_fields = ("name",)

@admin.register(QuoteHistory)
class QuoteHistoryAdmin(admin.ModelAdmin):
    list_display = ("quote", "action", "actor", "timestamp")
    list_filter = ("action",)
