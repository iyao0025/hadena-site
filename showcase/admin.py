from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "email", "phone", "service", "created_at", "is_processed")
    list_filter = ("service", "is_processed", "created_at", "consent_gdpr")
    search_fields = ("full_name", "company", "email", "phone", "message")
    readonly_fields = ("created_at", "ip_address", "consent_gdpr")
    list_editable = ("is_processed",)
    date_hierarchy = "created_at"
