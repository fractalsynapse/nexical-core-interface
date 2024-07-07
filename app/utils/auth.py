from django.contrib.auth.mixins import AccessMixin


class PublicOnlyAccessMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TeamAccessMixin(AccessMixin):
    """Verify that the current user is a current team user."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.check_member("team_member"):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
