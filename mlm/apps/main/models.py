import string

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey

from mlm.apps.core.models import TimestampedModel
from mlm.apps.main import settings as mlm_settings
from mlm.apps.core.utils import generate_random_string


User = get_user_model()


class MLMClient(MPTTModel, TimestampedModel):
    client_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_admin = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.client_id = generate_client_id()
        super(MLMClient, self).save(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ["user"]

    @property
    def affiliations(self):
        return self.get_descendants(include_self=False)

    @property
    def year_affiliations(self):
        try:
            return self.affilations.filter(created_at__year=timezone.now().year)
        except:
            return self.__class__.objects.none()


################ FUNCTIONS ###############


def generate_client_id():
    """
    Generate a new account code
    :size: Length of code
    :chars: Character set to choose from
    """
    size = mlm_settings.MLM_CLIENT_ID
    # chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    chars = string.digits
    code = generate_random_string(chars=chars, size=size)
    # Ensure code does not aleady exist

    exists = False

    try:
        MLMClient.objects.get(client_id=code)
    except MLMClient.DoesNotExist:
        return code

    return generate_account_code(size=size, chars=chars)
