from django.contrib import admin

from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "request_type", "order", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email", "order__id")
    readonly_fields = ("created_at", "updated_at")
