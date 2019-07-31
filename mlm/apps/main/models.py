import string

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from mlm.apps.core.models import TimestampedModel
from mlm.apps.main import settings as mlm_settings
from mlm.apps.core.utils import generate_random_string

from .managers import MLMClientManager, MLMTransactionManager


User = get_user_model()


def get_or_create_mlm_config():
    try:
        if MLMConfig.objects.filter().exists():
            c = MLMConfig.objects.filter().first()
            return c
        else:
            raise MLMConfig.DoesNotExist()
    except MLMConfig.DoesNotExist:
        return MLMConfig.objects.create(
            mlm_name=mlm_settings.MLM_GROUP_NAME,
            mlm_url=mlm_settings.MLM_GROUP_URL,
            subscription_amount=mlm_settings.DEFAULT_SUBSCRIPTION_AMOUNT,
            upline_commissions=mlm_settings.DEFAULT_UPLINE_CIOS_AMOUNT,
        )


def get_subscription_amount_default():
    try:
        c = get_or_create_mlm_config()
        return c.subscription_amount
    except:
        return mlm_settings.DEFAULT_SUBSCRIPTION_AMOUNT


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
    # is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # is_main = models.BooleanField(default=False)

    subscription_amount = models.DecimalField(
        max_digits=16, decimal_places=2, default=get_subscription_amount_default
    )

    available_amount = models.DecimalField(
        max_digits=16, decimal_places=2, default=get_subscription_amount_default
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mlm_clients_created",
        related_query_name="mlm_client_created",
    )
    # Managers
    objects = MLMClientManager()
    tree = TreeManager()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.client_id = generate_client_id()
        super(MLMClient, self).save(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ["client_id"]

    def __str__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.client_id)

    @property
    def balance(self):
        return self.available_amount

    def get_bonus(self, **kwargs):
        debits = (
            self.mlm_transactions.filter(
                debit_credit=MLMTransaction.DEBIT, **kwargs
            ).aggregate(models.Max("amount"))["amount__max"]
            or 0
        )
        credits = (
            self.mlm_transactions.filter(
                debit_credit=MLMTransaction.CREDIT, **kwargs
            ).aggregate(models.Max("amount"))["amount__max"]
            or 0
        )

        diff = credits - debits
        if diff > 0:
            return diff
        else:
            return 0

    @property
    def bonus(self, **kwargs):
        return self.get_bonus()

    @property
    def this_year_bonus(self, **kwargs):
        return self.get_bonus(created_at__year=timezone.now().year)

    @property
    def last_year_bonus(self, **kwargs):
        return self.get_bonus(created_at__year=timezone.now().year - 1)

    @property
    def affiliation_bonus(self, **kwargs):
        return self.get_bonus(transaction_type=MLMTransaction.FOR_AFFILIATION)

    @property
    def product_bonus(self, **kwargs):
        return self.get_bonus(transaction_type=MLMTransaction.FOR_PRODUCT)

    @property
    def affiliations(self):
        return self.get_descendants(include_self=False)

    def get_absolute_url(self):
        return self.user.get_profile_url()

    def get_list_url(self):
        return reverse("main:admin-clients-list")

    def get_activation_url(self):
        return reverse(
            "main:admin-client-activation", kwargs={"type_": 1, "pk": self.pk}
        )

    def get_deactivation_url(self):
        return reverse(
            "main:admin-client-activation", kwargs={"type_": 0, "pk": self.pk}
        )

    def get_set_admin_url(self):
        return reverse(
            "main:admin-client-activation", kwargs={"type_": 2, "pk": self.pk}
        )

    def get_delete_admin_url(self):
        return reverse(
            "main:admin-client-activation", kwargs={"type_": 3, "pk": self.pk}
        )

    @property
    def year_affiliations(self):
        try:
            return self.affiliations.filter(created_at__year=timezone.now().year)
        except:
            return self.__class__.objects.none()

    @property
    def last_year_affiliations(self):
        try:
            return self.affiliations.filter(created_at__year=timezone.now().year - 1)
        except:
            return self.__class__.objects.none()


class MLMTransaction(TimestampedModel):
    DEBIT = "D"
    CREDIT = "C"

    DC_CHOICES = ((DEBIT, "Debit"), (CREDIT, "Credit"))

    SIMPLE = "S"
    FOR_AFFILIATION = "A"
    FOR_PRODUCT = "P"

    TR_TYPE_CHOICES = (
        (SIMPLE, "Simple"),
        (FOR_AFFILIATION, "Affiliation"),
        (FOR_PRODUCT, "Produits"),
    )
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
    transaction_type = models.CharField(
        max_length=1, choices=TR_TYPE_CHOICES, default=SIMPLE
    )
    description = models.TextField(null=True)

    # Managers
    objects = MLMTransactionManager()

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return "%s:%s:%s" % (
            self.created_at.year,
            self.reference_number,
            self.reference_line,
        )

    @classmethod
    def get_next_ref_no(cls):
        current_year = timezone.now().year
        current_reference = (
            cls.objects.filter(created_at__year=current_year).aggregate(
                models.Max("reference_number")
            )["reference_number__max"]
            or 0
        )

        return current_reference + 1


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
