from django.db import models

from core.models.generics import StampedUUIDModel


class SharepointFile(StampedUUIDModel):
    file = models.FileField(upload_to="sharepoint/")
    # objects: models.Manager["SharepointFile"]


class CoaterProductionPlanner(StampedUUIDModel):
    plan = models.JSONField()
    sha256 = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("-lastmodified_at",)


class FloaterProductionPlanner(StampedUUIDModel):
    plan = models.JSONField()
    sha256 = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("-lastmodified_at",)
