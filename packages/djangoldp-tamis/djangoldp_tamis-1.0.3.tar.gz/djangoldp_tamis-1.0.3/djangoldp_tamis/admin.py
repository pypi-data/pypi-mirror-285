from django.contrib import admin
from django.contrib.auth.models import Group
from djangoldp.admin import DjangoLDPAdmin

from djangoldp_tamis.forms import GroupAdminForm
from djangoldp_tamis.models import *


@admin.register(
    AudioTrack,
    VideoTrack,
    Asset,
    Track,
    StepToTemplate,
)
class EmptyAdmin(admin.ModelAdmin):
    readonly_fields = ("urlid",)
    exclude = ("is_backlink", "allow_create_backlink")

    def get_model_perms(self, request):
        return {}


@admin.register(
    Agent,
    Format,
    Serie,
    Season,
    Programme,
    EditorialWork,
    EditorialWorkTag,
    Step,
)
class TamisModelAdmin(DjangoLDPAdmin):
    readonly_fields = ("urlid",)
    exclude = ("is_backlink", "allow_create_backlink")
    extra = 0


class PrestationStepInline(admin.TabularInline):
    model = StepToTemplate
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


@admin.register(PrestationStep)
class PrestationStepAdmin(TamisModelAdmin):
    inlines = [PrestationStepInline]


class AssetInline(admin.TabularInline):
    model = Asset
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


@admin.register(Prestation)
class PrestationAdmin(TamisModelAdmin):
    inlines = [AssetInline]


class TrackInline(admin.TabularInline):
    model = Track
    exclude = ("urlid", "is_backlink", "allow_create_backlink")
    extra = 0


@admin.register(MediaResource)
class MediaResourceAdmin(TamisModelAdmin):
    inlines = [TrackInline]


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    readonly_fields = ("name",)

    def get_model_perms(self, request):
        return {}
