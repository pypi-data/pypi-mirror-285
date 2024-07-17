from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseEditorialObject
from djangoldp_tamis.models.season import Season


class Programme(baseEditorialObject):
    # http://www.ebu.ch/metadata/ontologies/ebucoreplus#Programme
    number = models.PositiveIntegerField(blank=True, null=True, default=0)
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="programmes",
        blank=True,
        null=True,
    )

    class Meta(Model.Meta):
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")

        serializer_fields = [
            "@id",
            "title",
            "alternate_title",
            "editorial_works",
            "season",
        ]
        nested_fields = ["editorial_works", "season"]
        rdf_type = "ec:Programme"
        permission_classes = [ReadOnly]
