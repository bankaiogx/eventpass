import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from tickets.models import Order


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

    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(reverse("payment_success", args=[order.id]))
    cancel_url = request.build_absolute_uri(reverse("booking_confirmation", args=[order.id]))

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
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": order.id},
    )

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
    order.payment_status = "paid"
    order.save()

    return render(request, "payments/payment_success.html", {"order": order})


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
            Order.objects.filter(id=order_id).update(
                payment_status="paid",
                stripe_checkout_id=session.get("id", ""),
            )

    return HttpResponse(status=200)
