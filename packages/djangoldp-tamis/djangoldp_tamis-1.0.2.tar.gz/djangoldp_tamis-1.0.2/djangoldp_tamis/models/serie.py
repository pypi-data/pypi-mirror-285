from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseEditorialObject


class Serie(baseEditorialObject):

    def __str__(self):
        try:
            if self.title:
                return "{} ({})".format(self.title, self.urlid)
            return "{} ({})".format(self.seasons.first().programmes.first().title, self.urlid)
        except Exception:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Serie")
        verbose_name_plural = _("Series")

        serializer_fields = [
            "@id",
            "title",
            "alternate_title",
            "seasons",
        ]
        nested_fields = ["seasons"]
        rdf_type = "ec:Series"
        permission_classes = [ReadOnly]
