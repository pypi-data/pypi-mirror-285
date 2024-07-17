from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.editorial_work_tag import EditorialWorkTag
from djangoldp_tamis.models.programme import Programme


class EditorialWork(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default="")
    tags = models.ManyToManyField(
        EditorialWorkTag,
        related_name="tags",
        blank=True,
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name="editorial_works",
        blank=True,
        null=True,
    )

    @property
    def assets(self):
        return [prestation.assets for prestation in self.prestations.all()]

    class Meta(Model.Meta):
        verbose_name = _("Editorial Work")
        verbose_name_plural = _("Editorial Works")

        serializer_fields = ["@id", "tags", "programme", "assets"]
        nested_fields = ["tags"]
        rdf_type = "ec:EditorialWork"
        permission_classes = [ReadOnly]
