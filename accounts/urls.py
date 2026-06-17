from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from . import views


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(authentication_form=LoginForm, template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    path("support/", views.support_requests, name="support_requests"),
    path("support/new/", views.create_support_request, name="create_support_request"),
    path("support/<int:request_id>/edit/", views.edit_support_request, name="edit_support_request"),
    path("support/<int:request_id>/delete/", views.delete_support_request, name="delete_support_request"),
]
