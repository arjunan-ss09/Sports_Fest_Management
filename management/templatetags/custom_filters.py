from django import template

register = template.Library()

@register.filter
def before_hyphen(value):
    if isinstance(value, str) and '-' in value:
        return value.split('-')[0].strip()
    return value