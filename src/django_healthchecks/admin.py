from django.contrib import admin
from django.templatetags.static import static
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.timesince import timeuntil
from django.utils.timezone import is_aware, localtime
from django.utils.translation import gettext_lazy as _

from django_healthchecks.models import HeartbeatMonitor


@admin.register(HeartbeatMonitor)
class HeartbeatMonitorAdmin(admin.ModelAdmin):
    """Give an overview of heartbeats."""

    list_display = ("name", "enabled", "timeout", "last_beat_column")
    list_filter = ("enabled",)
    readonly_fields = ("last_beat_column", "remaining_time")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "timeout",
                    "enabled",
                    ("last_beat_column", "remaining_time"),
                )
            },
        ),
    )

    def has_add_permission(self, request):
        # Only code calling HeartbeatMonitor.update() can add objects
        return False

    def last_beat_column(self, object):
        last_beat = object.last_beat
        if is_aware(last_beat):
            # Only for USE_TZ=True
            last_beat = localtime(last_beat)

        last_beat_str = localize(last_beat)
        if object.is_expired:
            # Make clearly visible
            alert_icon = static("admin/img/icon-alert.svg")
            return format_html(
                '<div style="vertical-align: middle; display: inline-block;">'
                '  <img src="{}" style="vertical-align: middle;"> '
                '  <span style="color: #efb80b; vertical-align: middle;">{}</span>'
                "</div>",
                alert_icon,
                last_beat_str,
            )
        else:
            return last_beat_str

    last_beat_column.admin_order_field = "last_beat"
    last_beat_column.short_description = _("Last beat")

    def remaining_time(self, object):
        return timeuntil(object.expires_at)

    remaining_time.short_description = _("Time remaining")
