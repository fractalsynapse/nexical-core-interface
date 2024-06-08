from django import template

register = template.Library()


@register.simple_tag(name="is_business_team_member")
def is_business_team_member(user):
    if isinstance(user, str):
        return False
    return user.is_authenticated and user.check_member("business_team_member")


@register.simple_tag(name="is_outreach_member")
def is_outreach_member(user):
    if isinstance(user, str):
        return False
    return user.is_authenticated and user.check_member("outreach")
