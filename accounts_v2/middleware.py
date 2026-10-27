from django.http import HttpResponseRedirect


class MiddlewareToVerify:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "/accounts/login" in request.build_absolute_uri():
            if request.user.is_active is False:
                return HttpResponseRedirect("/account/identify")

        response = self.get_response(request)
        return response
