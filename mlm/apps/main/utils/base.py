from django.contrib.auth import get_user_model

from mlm.apps.main.models import MLMClient
from mlm.apps.main import settings as mlm_settings

from mlm.apps.main.exceptions import InvalidClientParentError, InvalidAffiliationError

User = get_user_model()


def create_client(user, parent=None):
    """
    Function to create and validate a client
    """

    if not isinstance(user, User):
        raise RuntimeError("'user' must be instance of User.")

    # client, cr = MLMClient.objects.get_or_create(user=user)
    client = MLMClient(user=user)
    save_client = False

    if not client.is_active:
        client.is_active = True
        save_client = True

    if isinstance(parent, MLMClient):
        client.parent = parent
        save_client = True

    elif isinstance(parent, User):
        if hasattr(parent, "mlmclient"):
            client.parent = parent.mlmclient
            save_client = True

    elif parent is not None:
        raise InvalidClientParentError("The 'Parent Object' given was invalid.")

    if parent.get_children().count() >= mlm_settings.MAX_AFFILIATION_NUMBER:
        raise InvalidAffiliationError(
            "L'upline a atteint le nombre maximal de parrainages."
        )

    if save_client:
        client.save()
        return client
    else:
        return None


def deactivate_client(user):
    def _execute_deactivate(client):
        if client.is_active:
            client.is_active = False
            client.is_admin = False
            client.save()
        return client

    if isinstance(user, User):
        client = MLMClient.objects.filter(user=user)
        for c in client:
            _execute_deactivate(c)
        return user
    elif isinstance(user, MLMClient):
        c = _execute_deactivate(user)
        return c.user


def create_adminclient(user):
    """
    Function to create and make admin client
    """
    client = create_client(user)
    client.is_admin = True
    client.save()
    return client
