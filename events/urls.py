from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/book/", views.book_ticket, name="book_ticket"),
]
