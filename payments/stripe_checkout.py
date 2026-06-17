import stripe

from django.conf import settings
from django.urls import reverse


def create_order_checkout_session(request, order):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(reverse("payment_success", args=[order.id]))
    cancel_url = request.build_absolute_uri(reverse("payment_cancel", args=[order.id]))

    return stripe.checkout.Session.create(
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
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": order.id},
    )
