from django.conf import settings


MAX_AFFILIATION_NUMBER = getattr(settings, "MLM_MAX_AFFILIATION_NUMBER", 2)
MLM_CLIENT_ID_SIZE = getattr(settings, "MLM_CLIENT_ID_SIZE", 6)
# Amount in Default Currency (Here USD,but will change)
DEFAULT_SUBSCRIPTION_AMOUNT = getattr(settings, "MLM_DEFAULT_SUBSCRIPTION_AMOUNT", 10)
