from django.conf import settings


MAX_AFFILIATION_NUMBER = getattr(settings, "MAX_AFFILIATION_NUMBER", 2)
MLM_CLIENT_ID_SIZE = getattr(settings, "MLM_CLIENT_ID_SIZE", 6)
