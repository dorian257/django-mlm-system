from django.contrib.auth import get_user_model

from mlm.apps.main.models import MLMClient
from mlm.apps.main import settings as mlm_settings

from mlm.apps.main.exceptions import InvalidClientParentError

User = get_user_model()


def create_client(user, parent=None):
    """
    Function to create and validate a client
    """
    client, cr = MLMClient.objects.get_or_create(user=user)
    save_client = False

    if not isinstance(user, User):
        raise RuntimeError("'user' must be instance of User.")

    if not client.is_valid:
        client.is_valid = True
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

    if save_client:
        client.save()
        return client
    else:
        return None


def deactivate_client(user):
    client, cr = MLMClient.objects.get_or_create(user=user)
    if client.is_valid:
        client.is_valid = False
        client.is_admin = False
        client.save()
    return client


def create_adminclient(user):
    """
    Function to create and make admin client
    """
    client = create_client(user)
    client.is_admin = True
    client.save()
    return client
