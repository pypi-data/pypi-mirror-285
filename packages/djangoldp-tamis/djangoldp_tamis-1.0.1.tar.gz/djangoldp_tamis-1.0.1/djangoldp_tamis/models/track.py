from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseAsset
from djangoldp_tamis.models.audio_track import AudioTrack
from djangoldp_tamis.models.media_resource import MediaResource
from djangoldp_tamis.models.video_track import VideoTrack


class Track(baseAsset):
    media_resource = models.ForeignKey(
        MediaResource,
        on_delete=models.CASCADE,
        related_name="tracks",
        blank=True,
        null=True,
    )
    audio_track = models.ForeignKey(
        AudioTrack,
        on_delete=models.CASCADE,
        related_name="tracks",
        blank=True,
        null=True,
    )
    video_track = models.ForeignKey(
        VideoTrack,
        on_delete=models.CASCADE,
        related_name="tracks",
        blank=True,
        null=True,
    )

    class Meta(Model.Meta):
        verbose_name = _("Track")
        verbose_name_plural = _("Tracks")
        serializer_fields = [
            "@id",
            "identifier",
            "issuers",
            "audio_track",
            "video_track",
        ]
        nested_fields = ["issuers", "audio_track", "video_track"]
        rdf_type = "ec:Track"
        permission_classes = [ReadOnly]
