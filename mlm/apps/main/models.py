import string

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey

from mlm.apps.core.models import TimestampedModel
from mlm.apps.main import settings as mlm_settings
from mlm.apps.core.utils import generate_random_string


User = get_user_model()


def get_subscription_amount_default():
    try:
        c = MLMConfig.objects.filter().first().get()
        return c.subscription_amount
    except:
        return 0


class MLMConfig(TimestampedModel):
    mlm_name = models.CharField(max_length=100, verbose_name="Nom de l'institution")
    mlm_url = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Lien URL"
    )
    subscription_amount = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Motant pour inscription"
    )
    upline_commissions = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Commissions pour l'upline"
    )


class MLMClient(MPTTModel, TimestampedModel):
    client_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mlm_clients",
        related_query_name="mlm_client",
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    subscription_amount = models.DecimalField(
        max_digits=16, decimal_places=2, default=get_subscription_amount_default
    )

    available_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

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
            return self.affiliations.filter(created_at__year=timezone.now().year)
        except:
            return self.__class__.objects.none()


class MLMTransaction(TimestampedModel):
    DEBIT = "D"
    CREDIT = "C"

    DC_CHOICES = ((DEBIT, "Debit"), (CREDIT, "Credit"))
    client = models.ForeignKey(
        "MLMClient",
        on_delete=models.PROTECT,
        related_name="mlm_transactions",
        related_query_name="mlm_transaction",
    )
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="mlm_initiated_transactions",
        related_query_name="mlm_initiated_transaction",
    )
    debit_credit = models.CharField(max_length=1, choices=DC_CHOICES)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    reference_number = models.PositiveIntegerField()
    reference_line = models.PositiveIntegerField()
    balance_after = models.DecimalField(max_digits=16, decimal_places=2)


################ FUNCTIONS ###############


def generate_client_id():
    """
    Generate a new account code
    :size: Length of code
    :chars: Character set to choose from
    """
    size = mlm_settings.MLM_CLIENT_ID_SIZE
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
