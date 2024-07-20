from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseEditorialObject
from djangoldp_tamis.models.serie import Serie


class Season(baseEditorialObject):
    number = models.PositiveIntegerField(blank=True, null=True, default=0)
    serie = models.ForeignKey(
        Serie,
        on_delete=models.CASCADE,
        related_name="seasons",
        blank=True,
        null=True,
    )

    def __str__(self):
        try:
            if self.title and not self.serie.title:
                return "{} ({})".format(self.title, self.urlid)
            if not self.title and not self.serie.title:
                return "{} ({})".format(self.programmes.first().title, self.urlid)
            return "{} S{} ({})".format(self.serie.title, self.number, self.urlid)
        except Exception:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Season")
        verbose_name_plural = _("Seasons")

        serializer_fields = [
            "@id",
            "title",
            "alternate_title",
            "number",
            "serie",
            "programmes",
        ]
        nested_fields = ["serie", "programmes"]
        rdf_type = "ec:Seasons"
        permission_classes = [ReadOnly]
