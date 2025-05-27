from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr):
    """Gets an attribute of an object dynamically from a string name."""
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return None

