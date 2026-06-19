from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from tickets.models import Order

from .forms import ProfileForm, RegisterForm, SupportRequestForm
from .models import Profile, SupportRequest


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    profile_form = ProfileForm(instance=request.user, profile=user_profile)
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        if "save_profile" in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user, profile=user_profile)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated.")
                return redirect("profile")

        if "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated.")
                return redirect("profile")

    for field in password_form.fields.values():
        field.widget.attrs.update({"class": "form-control"})

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )


@login_required
def my_tickets(request):
    orders = Order.objects.filter(user=request.user).select_related("event").prefetch_related("items__ticket_type")
    return render(request, "accounts/my_tickets.html", {"orders": orders})


@login_required
def support_requests(request):
    requests = SupportRequest.objects.filter(user=request.user).select_related("order", "order__event")
    return render(request, "accounts/support_requests.html", {"requests": requests})


@login_required
def create_support_request(request):
    order = None
    request_type = request.GET.get("type", "general")
    order_id = request.GET.get("order")

    if order_id:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.order = order
            support_request.request_type = request_type
            support_request.save()
            if order and request_type == "cancel_order":
                order.refund_status = "requested"
                order.save()
            messages.success(request, "Your support request has been sent.")
            return redirect("support_requests")
    else:
        initial = {}

        if order and request_type == "cancel_order":
            initial = {
                "subject": f"Cancel order #{order.id}",
                "message": f"I would like to request cancellation for order #{order.id}.",
            }

        form = SupportRequestForm(initial=initial)

    return render(
        request,
        "accounts/support_request_form.html",
        {"form": form, "order": order, "request_type": request_type},
    )


@login_required
def edit_support_request(request, request_id):
    support_request = get_object_or_404(SupportRequest, id=request_id, user=request.user, status="open")

    if request.method == "POST":
        form = SupportRequestForm(request.POST, instance=support_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Your support request has been updated.")
            return redirect("support_requests")
    else:
        form = SupportRequestForm(instance=support_request)

    return render(request, "accounts/support_request_form.html", {"form": form, "support_request": support_request})


@login_required
def delete_support_request(request, request_id):
    support_request = get_object_or_404(SupportRequest, id=request_id, user=request.user, status="open")

    if request.method == "POST":
        support_request.delete()
        messages.success(request, "Your support request has been deleted.")
        return redirect("support_requests")

    return render(request, "accounts/support_request_confirm_delete.html", {"support_request": support_request})
