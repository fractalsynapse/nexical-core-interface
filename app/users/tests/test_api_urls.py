from django.urls import resolve, reverse

from app.users.models import User


def test_user_detail(user: User):
    assert reverse("user-detail", kwargs={"id": user.pk}) == f"/user/{user.pk}/"
    assert resolve(f"/user/{user.pk}/").view_name == "user-detail"


def test_user_list():
    assert reverse("user-list") == "/user/"
    assert resolve("/user/").view_name == "user-list"


def test_user_me():
    assert reverse("user-me") == "/user/me/"
    assert resolve("/user/me/").view_name == "user-me"
