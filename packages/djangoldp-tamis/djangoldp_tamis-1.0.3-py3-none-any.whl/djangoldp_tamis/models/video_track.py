from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseAsset


class VideoTrack(baseAsset):
    # TODO: http://www.ebu.ch/metadata/ontologies/ebucoreplus#VideoTrack
    frame_height = models.PositiveIntegerField(blank=True, null=True, default=0)
    frame_rate = models.PositiveIntegerField(blank=True, null=True, default=0)
    frame_width = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta(Model.Meta):
        verbose_name = _("Video Track")
        verbose_name_plural = _("Video Tracks")
        serializer_fields = [
            "@id",
            "identifier",
            "issuers",
            "frame_height",
            "frame_rate",
            "frame_width",
        ]
        nested_fields = ["issuers"]
        rdf_type = "ec:VideoTrack"
        permission_classes = [ReadOnly]
