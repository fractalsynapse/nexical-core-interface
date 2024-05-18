from django.urls import resolve, reverse

from app.users.models import User


def test_detail(user: User):
    assert reverse("users:me") == "/users/me/"
    assert resolve("/users/me/").view_name == "users:me"


def test_update():
    assert reverse("users:update") == "/users/update/"
    assert resolve("/users/update/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
