from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def addclass(value, arg):
    """Add a CSS class to a form field or HTML string"""
    if hasattr(value, 'field'):
        # Handle form fields
        css_classes = value.field.widget.attrs.get('class', '').split()
        if arg not in css_classes:
            css_classes.append(arg)
        value.field.widget.attrs['class'] = ' '.join(css_classes)
        return value
    elif hasattr(value, 'tag'):
        # Handle BoundField subwidgets (like individual checkboxes)
        original_tag = value.tag
        if 'class="' in original_tag:
            original_tag = original_tag.replace('class="', f'class="{arg} ')
        else:
            original_tag = original_tag.replace('>', f' class="{arg}">')
        return mark_safe(original_tag)
    return value
