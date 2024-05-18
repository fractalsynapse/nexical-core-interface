import pytest
from rest_framework.test import APIRequestFactory

from app.api.views import UserViewSet
from app.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user not in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore
        result_fields = [
            "id",
            "email",
            "last_login",
            "date_joined",
            "first_name",
            "last_name",
            "timezone",
        ]
        assert all(field in response.data for field in result_fields)
