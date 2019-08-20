from django.contrib.auth import get_user_model

from mlm.apps.main.models import MLMClient
from mlm.apps.main import settings as mlm_settings

from mlm.apps.main.exceptions import InvalidClientParentError, InvalidAffiliationError

User = get_user_model()


def create_client(user, created_by, parent=None):
    """
    Function to create and validate a client
    """

    if not isinstance(user, User):
        raise RuntimeError("'user' must be instance of User.")

    # client, cr = MLMClient.objects.get_or_create(user=user)
    client = MLMClient(user=user, created_by=created_by)
    client.save()
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

    elif parent:
        try:
            parent = MLMClient.objects.get(client_id=parent)
            client.parent = parent
            save_client = True
        except MLMClient.DoesNotExist:
            raise InvalidClientParentError("The 'Parent Object' given was invalid.")

    if parent is not None:
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
    """
    Change
    """

    def _execute_deactivate(client):
        if client.is_active:
            client.is_active = False
            client.user.is_mlm_staff = False
            client.save()
        return client

    if isinstance(user, User):
        client = user.mlmclient
        for c in client:
            _execute_deactivate(c)
        return user
    elif isinstance(user, MLMClient):
        c = _execute_deactivate(user)
        return c.user


def create_adminclient(user, created_by):
    """
    Function to create and make admin client
    """
    client = create_client(user, created_by)
    client.user.is_mlm_staff = True
    client.user.save()
    return client


def get_system_client():
    system_username = mlm_settings.SYSTEM_USERNAME
    system_email = mlm_settings.SYSTEM_EMAIL

    try:
        u = User.objects.get(username=system_username, email=system_email)
        c = u.mlmclient
    except User.DoesNotExist:
        u = User.objects.create_user(username=system_username, email=system_email)
        c = create_adminclient(u, u)

    return c
