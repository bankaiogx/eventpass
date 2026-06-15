from django.contrib import admin

from .models import Order, OrderItem, TicketType


admin.site.register(TicketType)
admin.site.register(Order)
admin.site.register(OrderItem)
