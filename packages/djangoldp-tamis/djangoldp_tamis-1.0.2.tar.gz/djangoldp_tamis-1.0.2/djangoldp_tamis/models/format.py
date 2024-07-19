from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.__base import baseAsset


class Format(baseAsset):
    class Meta(Model.Meta):
        verbose_name = _("File Format")
        verbose_name_plural = _("File Formats")
        serializer_fields = ["@id", "identifier", "issuers"]
        nested_fields = ["issuers"]
        rdf_type = "ec:FileFormat"
        permission_classes = [ReadOnly]
