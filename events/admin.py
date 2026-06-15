from django.contrib import admin

from .models import Category, Event, Venue


admin.site.register(Category)
admin.site.register(Venue)
admin.site.register(Event)
