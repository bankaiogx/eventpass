from django import template
from django.templatetags.static import static

register = template.Library()


EVENT_IMAGE_MAP = {
    "manchester startup meetup": "images/event_images/manchester.jpg",
    "blackburn charity food night": "images/event_images/food.jpg",
    "preston fitness bootcamp": "images/event_images/fitness.jpg",
    "live acoustic evening": "images/event_images/acoustic.jpg",
    "django workshop for beginners": "images/event_images/workshop.jpg",
    "community networking brunch": "images/event_images/brunch.jpg",
}

CATEGORY_IMAGE_MAP = {
    "business": "images/event_images/manchester.jpg",
    "charity": "images/event_images/food.jpg",
    "food": "images/event_images/food.jpg",
    "fitness": "images/event_images/fitness.jpg",
    "music": "images/event_images/acoustic.jpg",
    "workshop": "images/event_images/workshop.jpg",
}


@register.filter
def event_static_image(event):
    title = event.title.lower()
    category_slug = event.category.slug if event.category else ""
    return EVENT_IMAGE_MAP.get(title) or CATEGORY_IMAGE_MAP.get(category_slug) or "images/event_placeholder.jpg"


@register.filter
def event_image_url(event):
    if event.image:
        return event.image.url

    return static(event_static_image(event))
