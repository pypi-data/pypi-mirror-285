from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly

from djangoldp_tamis.models.editorial_work_tag import EditorialWorkTag
from djangoldp_tamis.models.programme import Programme


class EditorialWork(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default="")
    tags = models.ManyToManyField(
        EditorialWorkTag,
        related_name="tags",
        blank=True,
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name="editorial_works",
        blank=True,
        null=True,
    )

    def __str__(self):
        try:
            if self.programme.title:
                return "{} - {} ({})".format(self.programme.title, self.name, self.urlid)
            if self.programme.season.serie.title:
                return "{} S{}E{} - {} ({})".format(self.programme.season.serie.title, self.programme.season.number, self.programme.number, self.name, self.urlid)
            return self.urlid
        except Exception:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Editorial Work")
        verbose_name_plural = _("Editorial Works")

        serializer_fields = ["@id", "name", "tags", "programme"]
        nested_fields = ["tags"]
        rdf_type = "ec:EditorialWork"
        permission_classes = [ReadOnly]
