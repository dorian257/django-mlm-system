from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class MLMClient(MPTTModel):
    user = models.OneToOneField("authentication.User", on_delete=models.CASCADE)

    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class MPTTMeta:
        order_insertion_by = ["user__username"]
