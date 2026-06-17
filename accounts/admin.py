from django.contrib import admin

from .models import CancellationRequest, Profile, SupportRequest


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")


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
    list_display = ("subject", "user", "order", "order_payment_status", "order_refund_status", "status", "created_at")
    list_filter = ("status", "created_at", "order__payment_status", "order__refund_status")
    search_fields = ("subject", "message", "user__username", "user__email", "order__id")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(request_type="cancel_order")

    def save_model(self, request, obj, form, change):
        obj.request_type = "cancel_order"
        super().save_model(request, obj, form, change)

    @admin.display(description="Payment status")
    def order_payment_status(self, obj):
        if obj.order:
            return obj.order.get_payment_status_display()
        return "-"

    @admin.display(description="Refund status")
    def order_refund_status(self, obj):
        if obj.order:
            return obj.order.get_refund_status_display()
        return "-"
