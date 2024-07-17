from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import DynamicNestedField, Model
from djangoldp.permissions import ACLPermissions, AnonymousReadOnly, ReadOnly
from djangoldp_account.models import LDPUser

from djangoldp_tamis.models.editorial_work import EditorialWork


class Prestation(Model):
    devis_id = models.CharField(max_length=254, blank=True, null=True, default="")
    admins = models.OneToOneField(
        Group,
        related_name="admin_prestation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    editors = models.OneToOneField(
        Group,
        related_name="editor_prestation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    visitors = models.OneToOneField(
        Group,
        related_name="visitor_prestation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    expected_delivery = models.DateField(
        verbose_name="Date de livraison prévue", blank=True, null=True
    )
    editorial_work = models.ForeignKey(
        EditorialWork,
        on_delete=models.CASCADE,
        related_name="prestations",
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.devis_id:
            return "{} ({})".format(self.devis_id, self.urlid)
        else:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _("Prestation")
        verbose_name_plural = _("Prestations")

        serializer_fields = [
            "@id",
            "devis_id",
            "expected_delivery",
            "editorial_work",
            "assets",
            "steps",
            "admins",
            "editors",
            "visitors",
        ]
        nested_fields = ["assets", "steps", "admins", "editors", "visitors"]
        rdf_type = "sib:Prestation"
        permission_classes = [AnonymousReadOnly & (ReadOnly | ACLPermissions)]
        permission_roles = {
            "admins": {"perms": ["view", "change", "control"]},
            "editors": {"perms": ["view", "change"]},
            "visitors": {"perms": ["view"]},
        }


# add prestations in groups and users
Group._meta.inherit_permissions += [
    "admin_prestation",
    "editor_prestation",
    "visitor_prestation",
]
Group._meta.serializer_fields += [
    "admin_prestation",
    "editor_prestation",
    "visitor_prestation",
]
# TODO: Should take get_user_model instead to handle enventual other OIDC packages?
LDPUser._meta.serializer_fields += ["prestations"]
LDPUser.prestationContainer = lambda self: {"@id": f"{self.urlid}prestations/"}
LDPUser._meta.nested_fields += ["prestations"]
LDPUser.prestations = lambda self: Prestation.objects.filter(
    models.Q(admins__user=self)
    | models.Q(editors__user=self)
    | models.Q(visitors__user=self)
)
LDPUser.prestations.field = DynamicNestedField(Prestation, "prestations")

from .step_to_template import *
