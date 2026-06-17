from django.contrib import admin

from .models import CancellationRequest, SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "request_type", "order", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email", "order__id")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(request_type="cancel_order")


@admin.register(CancellationRequest)
class CancellationRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "order", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email", "order__id")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(request_type="cancel_order")

    def save_model(self, request, obj, form, change):
        obj.request_type = "cancel_order"
        super().save_model(request, obj, form, change)
