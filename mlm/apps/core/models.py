from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # updated_by = models.ForeignKey("human_resources.Operator", null=True, blank=True)
    # created_by = models.ForeignKey("human_resources.Operator", null=True, blank=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ["-created_at", "-updated_at"]
