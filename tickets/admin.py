from django.contrib import admin

from .models import Order, OrderItem, TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "quantity_available", "sale_active")
    list_filter = ("sale_active", "event")
    search_fields = ("event__title", "name")
    list_editable = ("price", "quantity_available", "sale_active")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event", "total_amount", "payment_status", "refund_status", "created_at")
    list_filter = ("payment_status", "refund_status", "created_at", "event")
    search_fields = ("user__username", "user__email", "event__title", "stripe_checkout_id")
    list_editable = ("refund_status",)
    readonly_fields = ("created_at",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.refund_status == "refunded":
            obj.return_ticket_stock()
        elif obj.refund_status == "rejected":
            obj.close_cancellation_requests()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "ticket_type", "quantity", "price_at_purchase")
    search_fields = ("order__user__username", "ticket_type__name", "ticket_type__event__title")
