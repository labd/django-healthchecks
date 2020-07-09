from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import ExpressionWrapper, F
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

EXPIRES_COLUMN_TYPE = models.DateTimeField()
IS_EXPIRED_COLUMN_TYPE = models.BooleanField()


def _get_default_timeout():
    return getattr(
        settings, "HEALTHCHECKS_DEFAULT_HEARTBEAT_TIMEOUT", timedelta(days=1)
    )


class HeartbeatMonitorQuerySet(models.QuerySet):
    def enabled(self):
        """Filter on enabled checks only."""
        return self.filter(enabled=True)

    def annotate_expires_at(self):
        """Add an ``expires_at`` field to the queryset results."""
        return self.annotate(
            expires_at=ExpressionWrapper(
                (F("last_beat") + F("timeout")), output_field=EXPIRES_COLUMN_TYPE
            )
        )

    def expired(self):
        """Tell which services no longer appear to send heartbeats."""
        return self.annotate_expires_at().filter(expires_at__lt=now())

    def expired_names(self):
        """Return a list of all heartbeats names that are expired."""
        return list(self.expired().values_list("name", flat=True))

    def status_by_name(self):
        """Return the expired status for every heartbeat."""
        # Sadly, tests like (F('last_beat') + F('timeout')) < now() aren't supported in Django.
        # Even this fails: .annotate(is_expired=RawSQL("(last_beat + timeout) < %s", [now()]))
        # Thus, have to make the comparison in Python instead.
        t = now()
        monitors = self.annotate_expires_at().values_list("name", "expires_at")
        return {name: (expires_at < t) for name, expires_at in monitors}


class HeartbeatMonitor(models.Model):
    """Monitoring the heartbeat of a task

    When a service is no longer sending out heartbeats, the
    ``check_expired_heartbeats`` check will be triggered.
    """

    name = models.CharField(_("Name"), max_length=200, db_index=True, unique=True)
    enabled = models.BooleanField(_("Enabled"), db_index=True, default=True)
    timeout = models.DurationField(_("Timeout"))
    last_beat = models.DateTimeField(_("Last Beat"), null=True)

    objects = HeartbeatMonitorQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = _("Heartbeat Monitor")
        verbose_name_plural = _("Heartbeat Monitors")

    @property
    def expires_at(self):
        """Tell when the object will expire"""
        return self.last_beat + self.timeout

    @property
    def is_expired(self):
        """Tell whether the last beat expired."""
        return self.expires_at < now()

    @property
    def remaining_time(self):
        return self.expires_at - now()

    @classmethod
    def _update(cls, name, default_timeout=None, timeout=None):
        """Internal function to update a heartbeat.
        Use :func:`django_healthchecks.heartbeats.update_heartbeat` instead.
        """
        extra_updates = {}
        if timeout is not None:
            extra_updates["timeout"] = timeout

        rows = cls.objects.filter(name=name).update(last_beat=now(), **extra_updates)
        if not rows:
            return cls.objects.create(
                name=name,
                enabled=True,
                timeout=timeout or default_timeout or _get_default_timeout(),
                last_beat=now(),
            )
