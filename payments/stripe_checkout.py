import json

import stripe

from django.conf import settings
from django.urls import reverse


def create_ticket_checkout_session(request, event, selected_tickets):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payment_cancel"))

    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": ticket.name,
                    },
                    "unit_amount": int(ticket.price * 100),
                },
                "quantity": quantity,
            }
            for ticket, quantity in selected_tickets
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": str(request.user.id),
            "event_id": str(event.id),
            "tickets": json.dumps([[ticket.id, quantity] for ticket, quantity in selected_tickets]),
        },
    )
