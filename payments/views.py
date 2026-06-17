import json
from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from events.models import Event
from tickets.models import Order, OrderItem, TicketType


def stripe_value(stripe_object, key, default=None):
    try:
        return stripe_object[key]
    except (KeyError, TypeError):
        return getattr(stripe_object, key, default)


def mark_order_paid(order):
    if order.payment_status == "paid":
        return

    for item in order.items.select_related("ticket_type"):
        ticket = item.ticket_type
        ticket.quantity_available = max(ticket.quantity_available - item.quantity, 0)
        ticket.save()

    order.payment_status = "paid"
    order.save()


def create_order_from_stripe_session(session):
    session_id = stripe_value(session, "id", "")
    existing_order = Order.objects.filter(stripe_checkout_id=session_id).prefetch_related("items__ticket_type").first()

    if existing_order:
        return existing_order

    metadata = stripe_value(session, "metadata", {}) or {}

    order_id = stripe_value(metadata, "order_id")

    if order_id:
        order = Order.objects.filter(id=order_id).prefetch_related("items__ticket_type").first()
        if order:
            order.stripe_checkout_id = session_id
            order.save()
            return order

    user = get_user_model().objects.get(id=stripe_value(metadata, "user_id"))
    event = Event.objects.get(id=stripe_value(metadata, "event_id"))
    ticket_data = json.loads(stripe_value(metadata, "tickets"))
    total_amount = Decimal(stripe_value(session, "amount_total", 0) or 0) / Decimal("100")

    order = Order.objects.create(
        user=user,
        event=event,
        total_amount=total_amount,
        stripe_checkout_id=session_id,
    )

    for ticket_id, quantity in ticket_data:
        ticket = TicketType.objects.get(id=ticket_id)
        OrderItem.objects.create(
            order=order,
            ticket_type=ticket,
            quantity=quantity,
            price_at_purchase=ticket.price,
        )

    return order


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, "Stripe payment session was not found.")
        return redirect("event_list")

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        order = create_order_from_stripe_session(session)
    except (stripe.error.StripeError, KeyError, ValueError, ObjectDoesNotExist):
        messages.error(request, "There was a problem confirming your payment.")
        return redirect("event_list")

    if order.user != request.user:
        return redirect("event_list")

    mark_order_paid(order)

    return render(request, "payments/payment_success.html", {"order": order})


@login_required
def payment_cancel(request):
    return render(request, "payments/payment_cancel.html")


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        try:
            order = create_order_from_stripe_session(session)
        except (KeyError, ValueError, ObjectDoesNotExist):
            return HttpResponse(status=200)

        mark_order_paid(order)

    return HttpResponse(status=200)
