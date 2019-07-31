from django.conf import settings


MAX_AFFILIATION_NUMBER = getattr(settings, "MLM_MAX_AFFILIATION_NUMBER", 2)
MLM_CLIENT_ID_SIZE = getattr(settings, "MLM_CLIENT_ID_SIZE", 6)
# Amount in Default Currency (Here USD,but will change)
DEFAULT_SUBSCRIPTION_AMOUNT = getattr(settings, "MLM_DEFAULT_SUBSCRIPTION_AMOUNT", 10)
DEFAULT_UPLINE_CIOS_AMOUNT = getattr(settings, "MLM_DEFAULT_UPLINE_CIOS_AMOUNT", 1)

SYSTEM_USERNAME = getattr(settings, "SYSTEM_USERNAME", "sys_user_super")
SYSTEM_EMAIL = getattr(settings, "SYSTEM_EMAIL", "sys@email.email")


MLM_GROUP_NAME = getattr(settings, "MLM_GROUP_NAME", "Djando MLM")
MLM_GROUP_URL = getattr(settings, "MLM_GROUP_URL", "dj-mlm")
