from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseAsset
from djangoldp_tamis.models.asset import Asset
from djangoldp_tamis.models.format import Format


class MediaResource(baseAsset):
    # TODO: http://www.ebu.ch/metadata/ontologies/ebucoreplus#MediaResource
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="media_resources",
        blank=True,
        null=True,
    )
    file_name = models.CharField(max_length=254, blank=True, null=True, default="")
    file_size = models.PositiveIntegerField(blank=True, null=True, default=0)
    format = models.ForeignKey(
        Format,
        on_delete=models.CASCADE,
        related_name="media_resources",
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.file_name:
            return "{} ({})".format(self.file_name, self.urlid)
        else:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Media Resource")
        verbose_name_plural = _("Media Resources")

        serializer_fields = [
            "@id",
            "identifier",
            "issuers",
            "file_name",
            "file_size",
            "format",
            "tracks",
        ]
        nested_fields = ["issuers", "tracks", "format"]
        rdf_type = "ec:MediaResource"
        permission_classes = [ReadOnly]
