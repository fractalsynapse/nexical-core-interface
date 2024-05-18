from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name="ui_url")
def ui_url(*args):
    path = "/".join([str(arg) for arg in args]) if len(args) else ""
    return f"{settings.BASE_UI_URL}/{path}"


@register.simple_tag(name="api_url")
def api_url(*args):
    path = "/".join([str(arg) for arg in args]) if len(args) else ""
    return f"{settings.BASE_API_URL}/{path}"
