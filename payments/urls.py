from django.urls import path

from . import views


urlpatterns = [
    path("orders/<int:order_id>/checkout/", views.create_checkout_session, name="create_checkout_session"),
    path("orders/<int:order_id>/success/", views.payment_success, name="payment_success"),
]
