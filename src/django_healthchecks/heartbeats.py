"""API functions to update heartbeats.

This module exists to keep external code decoupled from our model-based
implementation. This allows extending the functionality later to support
different mechanisms for tracking heartbeats (e.g. external services).
"""
from functools import wraps

from django.utils.timezone import now

from django_healthchecks.models import HeartbeatMonitor


def get_expired_heartbeats():
    """Provide a list of all heartbeats that expired.

    :rtype: list
    """
    return HeartbeatMonitor.objects.enabled().expired_names()


def get_heartbeat_statuses():
    """Provide a dict of ``name: status`` for every heartbeat.

    :rtype: dict
    """
    data = HeartbeatMonitor.objects.enabled().status_by_name()
    data["__all__"] = all(data.values())
    return data


def update_heartbeat(name, default_timeout=None, timeout=None):
    """Update a heartbeat monitor.
    This tracks a new pulse, so the timer is reset.

    Upon the first call, the ``default_timeout`` can be assigned.
    To tune the timeout later, use the Django admin interface,
    or make a call that provides the ``timeout`` value.

    :param name: Name of the check.
    :type name: str
    :param default_timeout: The timeout to use by default on registration.
    :type default_timeout: datetime.timedelta
    :param timeout: The timeout to be forcefully updated.
    :type timeout: datetime.timedelta
    """
    HeartbeatMonitor._update(
        name=name, default_timeout=default_timeout, timeout=timeout
    )


def update_heartbeat_on_success(name, default_timeout=None, timeout=None):
    """Decorator to update a heartbeat when a function was successful.

    Usage:

    .. code-block::

        @update_heartbeat_on_success("some.check.name")
        def your_function():
            pass
    """

    def _inner(func):
        @wraps(func)
        def _update_heartbeat_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            update_heartbeat(name, default_timeout=default_timeout, timeout=timeout)
            return value

        return _update_heartbeat_decorator

    return _inner
