from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MLMClient, MLMTransaction, get_or_create_mlm_config
from .utils.base import get_system_client

from django.conf import settings

CREATION_DESCRIPTION = getattr(
    settings, "CREATION_DESCRIPTION", "Client account creation."
)


@receiver(post_save, sender=MLMClient)
def execute_subscription_operation(sender, instance, created, *args, **kwargs):
    # Notice that we're checking for 'created' here. We only want to do this
    # the first time the 'User' instance is created. If the save that caused
    # this signal to be run was an update action, we know the user already
    # has a profile.
    if instance and created:

        # We make transactions only if the client has parent and has been created by an admin
        if instance.parent and instance.created_by:

            if instance.created_by.user.is_mlm_staff:
                instance.is_active = True
                instance.save()

                config = get_or_create_mlm_config()
                # We debit the Client from the subscription amount
                tr1 = MLMTransaction.objects.make_debit(
                    instance,
                    instance.subscription_amount,
                    MLMTransaction.FOR_AFFILIATION,
                    CREATION_DESCRIPTION,
                    initiated_by=instance.created_by,
                )

                # We credit the system from the subscription amount
                system_client = get_system_client()
                tr2 = MLMTransaction.objects.make_credit(
                    system_client,
                    instance.subscription_amount,
                    MLMTransaction.FOR_AFFILIATION,
                    CREATION_DESCRIPTION,
                    initiated_by=instance.created_by,
                )

                ### Here Verify if there is a pair, then credit the parent
                # tr3 = MLMTransaction.objects.make_credit(
                #     instance.parent,
                #     config.upline_commissions,
                #     transaction_type=MLMTransaction.FOR_AFFILIATION,
                #     initiated_by=instance.created_by,
                # )
            else:
                instance.is_active = False
                instance.save()
        elif instance.parent and not instance.created_by:
            instance.is_active = False
            instance.save()
        else:
            instance.is_active = True
            instance.save()
