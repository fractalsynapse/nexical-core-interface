from django import template

register = template.Library()


@register.simple_tag(name="is_team_member")
def is_team_member(user):
    if isinstance(user, str):
        return False
    return user.is_authenticated and user.check_member("team_member")
