from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly


class Step(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default="")

    def __str__(self):
        if self.name:
            return "{} ({})".format(self.name, self.urlid)
        else:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Prestation Step")
        verbose_name_plural = _("Prestation Steps")

        serializer_fields = [
            "@id",
            "name",
        ]
        nested_fields = []
        rdf_type = "sib:hasStep"
        permission_classes = [ReadOnly]
