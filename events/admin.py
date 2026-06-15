from django.contrib import admin

from .models import Category, Event, Venue


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "postcode")
    search_fields = ("name", "city", "postcode")
    list_filter = ("city",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "venue", "start_date", "start_time", "is_published")
    list_filter = ("category", "venue", "is_published", "start_date")
    search_fields = ("title", "description", "venue__name", "venue__city")
    list_editable = ("is_published",)
    ordering = ("start_date", "start_time")
