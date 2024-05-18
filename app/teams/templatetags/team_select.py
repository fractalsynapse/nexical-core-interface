from django import template

register = template.Library()


@register.simple_tag(name="user_owned_teams")
def user_owned_teams(user):
    teams = []
    for team in user.ownership.all():
        teams.append(team)
    return teams


@register.simple_tag(name="user_member_teams")
def user_member_teams(user):
    teams = []
    for membership in user.membership.all():
        teams.append(membership.team)
    return teams
