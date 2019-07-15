from django.conf import settings
from mlm import settings as app_settings


def mlm_defaults(request):
    return {
        "MLM_GROUP_NAME": settings.MLM_GROUP_NAME,
        "MLM_GROUP_URL": settings.MLM_GROUP_URL,  # Communication WebSite
        "MLM_VERSION": app_settings.__version__,
    }
