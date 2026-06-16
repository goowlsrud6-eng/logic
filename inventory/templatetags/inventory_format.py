from django import template

register = template.Library()


@register.filter
def comma0(value):
    """Format quantities with thousands separators and no decimals."""
    try:
        return f'{float(value or 0):,.0f}'
    except (TypeError, ValueError):
        return '0'


@register.filter
def weeks1(value):
    """Format stock weeks with exactly one decimal place."""
    try:
        return f'{float(value or 0):,.1f}'
    except (TypeError, ValueError):
        return '0.0'
