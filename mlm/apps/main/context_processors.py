from django.conf import settings


def mlm_defaults(request):
    return {
        "MLM_GROUP_NAME": settings.MLM_GROUP_NAME,
        "MLM_GROUP_URL": settings.MLM_GROUP_URL,  # Communication WebSite
    }
