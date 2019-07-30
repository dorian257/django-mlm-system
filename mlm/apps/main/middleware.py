from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings


class CheckClientMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # request.timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        not_checked_url = reverse("main:no-client-redirect")
        dashboard_url = reverse("main:dashboard")
        if request.path == not_checked_url:
            # If User is linked to clients, all goes good
            if request.user.mlm_clients.all().exists():
                return HttpResponseRedirect(dashboard_url)
            response = self.get_response(request)
            return response

        # Checking Client
        print("Checking Client...")
        if (
            request.user.is_authenticated
            and not request.user.mlm_clients.all().exists()
        ) and request.path != settings.LOGOUT_URL:
            return HttpResponseRedirect(not_checked_url)

        # An Active Client
        if request.user.is_authenticated and not request.user.mlmclient.is_active:
            return HttpResponseRedirect(not_checked_url)

        response = self.get_response(request)
        return response
