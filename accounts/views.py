from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from tickets.models import Order

from .forms import RegisterForm, SupportRequestForm
from .models import SupportRequest


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def my_tickets(request):
    orders = Order.objects.filter(user=request.user).select_related("event").prefetch_related("items__ticket_type")
    return render(request, "accounts/my_tickets.html", {"orders": orders})


@login_required
def support_requests(request):
    requests = SupportRequest.objects.filter(user=request.user)
    return render(request, "accounts/support_requests.html", {"requests": requests})


@login_required
def create_support_request(request):
    if request.method == "POST":
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            messages.success(request, "Your support request has been sent.")
            return redirect("support_requests")
    else:
        form = SupportRequestForm()

    return render(request, "accounts/support_request_form.html", {"form": form})
