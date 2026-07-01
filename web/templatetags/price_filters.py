from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value

    return f"{int(value):,}".replace(",", ".")
