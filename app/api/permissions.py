from rest_framework.permissions import BasePermission, DjangoModelPermissions


class BaseModelPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user

        if not user or (not user.is_authenticated and self.authenticated_users_only):
            return False

        if getattr(view, "_ignore_model_permissions", False):
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        change_perm = self.get_required_permissions("PUT", queryset.model)

        if request.method == "GET":
            return user.has_perms(perms) or user.has_perms(change_perm)

        return user.has_perms(perms)


class TeamPermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.check_member("team_member"):
            return False
        return True


class EnginePermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.check_member("engine"):
            return False
        return True


class SiteModelPermissions(BaseModelPermissions):
    pass


class TeamModelPermissions(BaseModelPermissions):
    pass


class UserModelPermissions(BaseModelPermissions):
    pass
