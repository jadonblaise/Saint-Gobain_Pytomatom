from django.db import models

from core.models.users import CoreAbstractUser


class User(CoreAbstractUser):
    class Roles(models.TextChoices):
        # roles derived from CoreAbstractUser.Roles:
        INCOMPLETE = "inc", "Incomplete Profile"  # !default
        ADMIN = "adm", "Admin"  # dev only
        API = "api", "Api User"
        # additional roles
        SG_DIGITAL = "sgd", "Saint-Gobain Digital"
        SG_GLAS = "gla", "Saint-Gobain Glas"
        SG_API = "dat", "Internal Api User"  # e.g. datalake

    class Meta(CoreAbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    # ! All changes to the user model that add non-nullable fields break backwards compatibility with AUTH_USER_MODEL.
    plants = models.ManyToManyField("datalake.Plant", related_name="users")
    jobtitle = models.CharField(blank=True, max_length=255, null=True)
