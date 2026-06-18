from django import template

register = template.Library()


EVENT_IMAGE_MAP = {
    "manchester startup meetup": "images/event_images/manchester.png",
    "blackburn charity food night": "images/event_images/food.png",
    "preston fitness bootcamp": "images/event_images/fitness.png",
    "live acoustic evening": "images/event_images/acoustic.png",
    "django workshop for beginners": "images/event_images/workshop.png",
    "community networking brunch": "images/event_images/brunch.png",
}

CATEGORY_IMAGE_MAP = {
    "business": "images/event_images/manchester.png",
    "charity": "images/event_images/food.png",
    "food": "images/event_images/food.png",
    "fitness": "images/event_images/fitness.png",
    "music": "images/event_images/acoustic.png",
    "workshop": "images/event_images/workshop.png",
}


@register.filter
def event_static_image(event):
    title = event.title.lower()
    category_slug = event.category.slug if event.category else ""
    return EVENT_IMAGE_MAP.get(title) or CATEGORY_IMAGE_MAP.get(category_slug) or "images/event_placeholder.png"
