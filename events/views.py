from django.db.models import Min, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Event, Venue


def event_list(request):
    events = (
        Event.objects.filter(is_published=True)
        .select_related("category", "venue")
        .annotate(starting_price=Min("ticket_types__price"))
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
    ticket_types = event.ticket_types.filter(sale_active=True).order_by("price")

    context = {
        "event": event,
        "ticket_types": ticket_types,
    }
    return render(request, "events/event_detail.html", context)
