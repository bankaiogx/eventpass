from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from tickets.models import Order

from .forms import RegisterForm


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
    orders = Order.objects.filter(user=request.user).select_related("event")
    return render(request, "accounts/my_tickets.html", {"orders": orders})
