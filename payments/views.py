import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .stripe_checkout import create_order_checkout_session
from tickets.models import Order


def mark_order_paid(order):
    if order.payment_status == "paid":
        return

    for item in order.items.select_related("ticket_type"):
        ticket = item.ticket_type
        ticket.quantity_available = max(ticket.quantity_available - item.quantity, 0)
        ticket.save()

    order.payment_status = "paid"
    order.save()


@login_required
@require_POST
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

    try:
        checkout_session = create_order_checkout_session(request, order)
    except stripe.error.StripeError:
        messages.error(request, "There was a problem starting Stripe checkout. Please try again.")
        return redirect("booking_confirmation", order_id=order.id)

    order.stripe_checkout_id = checkout_session.id
    order.save()

    return redirect(checkout_session.url)


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("event").prefetch_related("items__ticket_type"),
        id=order_id,
        user=request.user,
    )
    mark_order_paid(order)

    return render(request, "payments/payment_success.html", {"order": order})


@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("event"),
        id=order_id,
        user=request.user,
    )
    return render(request, "payments/payment_cancel.html", {"order": order})


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
        order_id = session.get("metadata", {}).get("order_id")

        if order_id:
            order = Order.objects.filter(id=order_id).prefetch_related("items__ticket_type").first()

            if order:
                order.stripe_checkout_id = session.get("id", "")
                mark_order_paid(order)

    return HttpResponse(status=200)
