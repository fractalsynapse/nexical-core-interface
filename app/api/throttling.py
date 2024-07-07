from rest_framework.throttling import SimpleRateThrottle


class BaseRoleRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated and request.user.check_member(self.scope):
            return self.cache_format % {"scope": self.scope, "ident": request.user.pk}
        return None


class EngineUserRoleRateThrottle(BaseRoleRateThrottle):
    scope = "engine"


class TeamUserRoleRateThrottle(BaseRoleRateThrottle):
    scope = "team_member"
