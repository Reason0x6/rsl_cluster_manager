import logging
from django import template
from clans.models import SiegePlan

register = template.Library()


@register.simple_tag
def get_recent_siege_plans():
    try:
        recent_plans = SiegePlan.objects.order_by('-created_at')[:4]
        return recent_plans
    except Exception as e:
        return []