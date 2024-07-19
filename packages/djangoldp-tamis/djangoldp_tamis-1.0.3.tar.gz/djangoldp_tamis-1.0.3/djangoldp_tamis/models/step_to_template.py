from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import InheritPermissions

from djangoldp_tamis.models.prestation_step import PrestationStep
from djangoldp_tamis.models.step import Step


class StepToTemplate(Model):
    template = models.ForeignKey(
        PrestationStep,
        on_delete=models.CASCADE,
        related_name="steps",
        blank=True,
        null=True,
    )
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name="templates",
        blank=True,
        null=True,
    )
    order = models.IntegerField(blank=True, null=True)
    validated = models.BooleanField(default=False)

    class Meta(Model.Meta):
        verbose_name = _("Prestation Template Step")
        verbose_name_plural = _("Prestation Template Steps")

        serializer_fields = ["@id", "step", "order", "validated"]
        nested_fields = ["step"]
        rdf_type = "sib:PrestationStep"
        permission_classes = [InheritPermissions]
        inherit_permissions = ["template"]
        depth = 1
