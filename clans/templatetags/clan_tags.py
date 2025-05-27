from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr):
    """
    Gets an attribute of an object dynamically from a string.
    Usage in template: {{ object|get_attribute:"attribute_name" }}
    """
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        try:
            return obj[attr]
        except (KeyError, TypeError):
            return None