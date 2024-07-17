from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import InheritPermissions

from djangoldp_tamis.models.prestation import Prestation


class PrestationStep(Model):
    is_template = models.BooleanField(default=False)
    prestation = models.ForeignKey(
        Prestation,
        on_delete=models.CASCADE,
        related_name="steps",
        blank=True,
        null=True,
    )

    class Meta(Model.Meta):
        verbose_name = _("Prestation Related Step")
        verbose_name_plural = _("Prestation Related Steps")

        serializer_fields = ["@id", "is_template", "steps"]
        nested_fields = ["steps"]
        rdf_type = "sib:PrestationTemplate"
        permission_classes = [InheritPermissions]
        inherit_permissions = ["prestation"]
