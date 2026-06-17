from django.conf import settings
from django.db import models

from events.models import Event


class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    sale_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["event", "price"]

    def __str__(self):
        return f"{self.event.title} - {self.name}"


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    REFUND_STATUS_CHOICES = [
        ("not_requested", "Not requested"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="orders")
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    stripe_checkout_id = models.CharField(max_length=255, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default="not_requested",
    )
    stock_returned = models.BooleanField(default=False)
    email_confirmation_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} - {self.user}"

    def close_cancellation_requests(self):
        self.support_requests.filter(request_type="cancel_order").update(status="closed")

    def return_ticket_stock(self):
        if self.stock_returned:
            return

        for item in self.items.select_related("ticket_type"):
            item.ticket_type.quantity_available += item.quantity
            item.ticket_type.save(update_fields=["quantity_available"])

        self.stock_returned = True
        self.payment_status = "cancelled"
        self.save(update_fields=["stock_returned", "payment_status"])
        self.close_cancellation_requests()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name}"
