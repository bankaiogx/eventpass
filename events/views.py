import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, redirect, render

from payments.stripe_checkout import create_ticket_checkout_session
from tickets.models import Order

from .models import Category, Event, Venue


def home(request):
    featured_events = (
        Event.objects.filter(is_published=True)
        .select_related("category", "venue")
        .annotate(
            starting_price=Min("ticket_types__price", filter=Q(ticket_types__sale_active=True, ticket_types__quantity_available__gt=0)),
            available_ticket_count=Count("ticket_types", filter=Q(ticket_types__sale_active=True, ticket_types__quantity_available__gt=0)),
        )
        .order_by("start_date", "start_time")[:3]
    )
    categories = Category.objects.all()[:6]

    context = {
        "featured_events": featured_events,
        "categories": categories,
    }
    return render(request, "events/home.html", context)


def event_list(request):
    events = (
        Event.objects.filter(is_published=True)
        .select_related("category", "venue")
        .annotate(
            starting_price=Min("ticket_types__price", filter=Q(ticket_types__sale_active=True, ticket_types__quantity_available__gt=0)),
            available_ticket_count=Count("ticket_types", filter=Q(ticket_types__sale_active=True, ticket_types__quantity_available__gt=0)),
        )
        .order_by("start_date", "start_time")
    )

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()
    price = request.GET.get("price", "").strip()

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category:
        events = events.filter(category__slug=category)

    if city:
        events = events.filter(venue__city__iexact=city)

    if price == "free":
        events = events.filter(ticket_types__price=0)
    elif price == "under-10":
        events = events.filter(ticket_types__price__lt=10)
    elif price == "under-25":
        events = events.filter(ticket_types__price__lt=25)

    context = {
        "events": events.distinct(),
        "categories": Category.objects.all(),
        "cities": Venue.objects.order_by("city").values_list("city", flat=True).distinct(),
        "selected_q": query,
        "selected_category": category,
        "selected_city": city,
        "selected_price": price,
    }
    return render(request, "events/event_list.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related("category", "venue"),
        id=event_id,
        is_published=True,
    )
    ticket_types = event.ticket_types.filter(sale_active=True, quantity_available__gt=0).order_by("price")

    context = {
        "event": event,
        "ticket_types": ticket_types,
    }
    return render(request, "events/event_detail.html", context)


@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_published=True)
    ticket_types = event.ticket_types.filter(sale_active=True, quantity_available__gt=0).order_by("price")

    if request.method == "POST":
        selected_tickets = []

        for ticket in ticket_types:
            try:
                quantity = int(request.POST.get(f"ticket_{ticket.id}", 0))
            except ValueError:
                messages.error(request, "Please choose a valid ticket quantity.")
                return redirect("book_ticket", event_id=event.id)

            if quantity > ticket.quantity_available:
                messages.error(request, "Please choose a valid ticket quantity.")
                return redirect("book_ticket", event_id=event.id)

            if quantity > 0:
                selected_tickets.append((ticket, quantity))

        if not selected_tickets:
            messages.error(request, "Please choose at least one ticket.")
            return redirect("book_ticket", event_id=event.id)

        if not settings.STRIPE_SECRET_KEY:
            messages.error(request, "Payment is not available right now. Please try again later.")
            return redirect("book_ticket", event_id=event.id)

        try:
            checkout_session = create_ticket_checkout_session(request, event, selected_tickets)
        except stripe.error.StripeError:
            messages.error(request, "There was a problem starting payment. Please try again.")
            return redirect("book_ticket", event_id=event.id)

        return redirect(checkout_session.url)

    context = {
        "event": event,
        "ticket_types": ticket_types,
    }
    return render(request, "events/book_ticket.html", context)


@login_required
def booking_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("event").prefetch_related("items__ticket_type"),
        id=order_id,
        user=request.user,
    )
    return render(request, "events/booking_confirmation.html", {"order": order})
