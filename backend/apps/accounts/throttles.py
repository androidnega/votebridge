from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class OTPRateThrottle(AnonRateThrottle):
    scope = "otp"


class TokenRefreshRateThrottle(SimpleRateThrottle):
    scope = "token_refresh"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return self.cache_format % {
                "scope": self.scope,
                "ident": request.user.pk,
            }
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
