# from django.contrib import messages
# from django.urls import reverse


class UserMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # No display on AJAX or debugging pages (and only when logged in)
        if (
            "~" not in request.path
            and "__debug__" not in request.path
            and request.user.is_authenticated
            and not request.user.is_staff
        ):
            pass

        return self.get_response(request)
