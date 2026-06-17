import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from tickets.models import Order


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__ticket_type"),
        id=order_id,
        user=request.user,
    )

    if order.payment_status == "paid":
        messages.info(request, "This order has already been paid.")
        return redirect("booking_confirmation", order_id=order.id)

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Stripe test keys need to be added before payment can work.")
        return redirect("booking_confirmation", order_id=order.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    order_url = request.build_absolute_uri(reverse("booking_confirmation", args=[order.id]))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": item.ticket_type.name,
                    },
                    "unit_amount": int(item.price_at_purchase * 100),
                },
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ],
        success_url=order_url,
        cancel_url=order_url,
    )

    order.stripe_checkout_id = checkout_session.id
    order.save()

    return redirect(checkout_session.url)
