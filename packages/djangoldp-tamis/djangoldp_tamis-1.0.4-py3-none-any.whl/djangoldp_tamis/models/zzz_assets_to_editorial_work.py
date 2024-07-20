from djangoldp.models import DynamicNestedField

from djangoldp_tamis.models.asset import Asset
from djangoldp_tamis.models.editorial_work import EditorialWork

EditorialWork._meta.serializer_fields += ["assets"]

EditorialWork.assetContainer = lambda self: {"@id": f"{self.urlid}assets/"}
EditorialWork._meta.nested_fields += ["assets"]

EditorialWork.assets = lambda self: Asset.objects.filter(
    prestation__in=self.prestations.all()
)
EditorialWork.assets.field = DynamicNestedField(Asset, "assets")
