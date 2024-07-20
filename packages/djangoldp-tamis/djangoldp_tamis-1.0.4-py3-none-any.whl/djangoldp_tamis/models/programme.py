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

    def __str__(self):
        try:
            if self.title and not self.season.serie.title:
                return "{} ({})".format(self.title, self.urlid)
            return "{} S{}E{} ({})".format(self.season.serie.title, self.season.number, self.number, self.urlid)
        except Exception:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")

        serializer_fields = [
            "@id",
            "title",
            "alternate_title",
            "editorial_works",
            "number",
            "season",
        ]
        nested_fields = ["editorial_works", "season"]
        rdf_type = "ec:Programme"
        permission_classes = [ReadOnly]
