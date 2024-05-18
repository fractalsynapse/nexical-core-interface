from django import template

register = template.Library()


@register.filter(name="unique_values")
def unique_values(values):
    index = {}
    if values:
        for item in values:
            index[str(item)] = item
    return list(index.values())
