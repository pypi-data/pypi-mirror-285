from django.contrib import admin
from artd_price_list.models import PriceList, PriceListLog
from artd_price_list.forms import PriceListForm
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from django.db import models


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    form = PriceListForm
    list_display = (
        "product",
        "description",
        "id",
        "partner",
        "get_real_price",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "partner__name",
        "product__name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            _("Product Information"),
            {
                "fields": (
                    "partner",
                    "product",
                    "description",
                )
            },
        ),
        (
            _("Price Information"),
            {"fields": ("regular_price",)},
        ),
        (
            _("Special Price Information"),
            {
                "fields": (
                    "special_price_from",
                    "special_price_to",
                    "special_price",
                )
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(PriceListLog)
class PriceListLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "product",
        "description",
        "regular_price",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "partner__name",
        "product__name",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
        "status",
        "partner",
        "product",
        "description",
        "regular_price",
        "special_price_from",
        "special_price_to",
        "special_price",
        "source",
        "external_id",
    ]
    fieldsets = (
        (
            _("Product Information"),
            {
                "fields": (
                    "partner",
                    "product",
                    "description",
                )
            },
        ),
        (
            _("Price Information"),
            {"fields": ("regular_price",)},
        ),
        (
            _("Special Price Information"),
            {
                "fields": (
                    "special_price_from",
                    "special_price_to",
                    "special_price",
                )
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
