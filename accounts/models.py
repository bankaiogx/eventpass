from django.conf import settings
from django.db import models

from tickets.models import Order


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} profile"


class SupportRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ("general", "General help"),
        ("cancel_order", "Cancel order"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="support_requests", blank=True, null=True)
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES, default="general")
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.user}"


class CancellationRequest(SupportRequest):
    class Meta:
        proxy = True
        verbose_name = "Cancellation request"
        verbose_name_plural = "Cancellation requests"
