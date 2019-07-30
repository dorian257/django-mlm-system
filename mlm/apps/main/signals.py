from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MLMClient, MLMTransaction
from .utils.base import get_system_client


@receiver(post_save, sender=MLMClient)
def execute_subscription_operation(sender, instance, created, *args, **kwargs):
    # Notice that we're checking for 'created' here. We only want to do this
    # the first time the 'User' instance is created. If the save that caused
    # this signal to be run was an update action, we know the user already
    # has a profile.
    if instance and created:
        instance.is_active = True
        instance.save()
        # We debit the Client from the subscription amount
        tr1 = MLMTransaction.objects.make_debit(
            instance, instance.subscription_amount, initiated_by=instance.created_by
        )
        # We credit the system from the subscription amount
        system_client = get_system_client()
        tr2 = MLMTransaction.objects.make_credit(
            system_client,
            instance.subscription_amount,
            initiated_by=instance.created_by,
        )
