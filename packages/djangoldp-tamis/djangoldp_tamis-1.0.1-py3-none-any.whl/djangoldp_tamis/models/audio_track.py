from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp.models import Model
from djangoldp.permissions import ReadOnly
from djangoldp_tamis.models.__base import baseAsset


class AudioTrack(baseAsset):
    # TODO: http://www.ebu.ch/metadata/ontologies/ebucoreplus#AudioTrack
    audio_channel_number = models.CharField(
        max_length=254, blank=True, null=True, default=""
    )
    bit_depth = models.CharField(max_length=254, blank=True, null=True, default="")
    sample_rate = models.CharField(max_length=254, blank=True, null=True, default="")

    class Meta(Model.Meta):
        verbose_name = _("Audio Track")
        verbose_name_plural = _("Audio Tracks")
        serializer_fields = [
            "@id",
            "identifier",
            "issuers",
            "audio_channel_number",
            "bit_depth",
            "sample_rate",
        ]
        nested_fields = ["issuers"]
        rdf_type = "ec:AudioTrack"
        permission_classes = [ReadOnly]
