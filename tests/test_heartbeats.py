from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import utc
from freezegun import freeze_time

from django_healthchecks.contrib import check_expired_heartbeats, check_heartbeats
from django_healthchecks.heartbeats import update_heartbeat, update_heartbeat_on_success
from django_healthchecks.models import HeartbeatMonitor

NOON = datetime(2018, 5, 3, 12, 0, 0, tzinfo=utc)
ONE_HOUR_LATER = datetime(2018, 5, 3, 13, 1, 0, tzinfo=utc)


@pytest.fixture
@freeze_time(NOON)
def beat1():
    # Should be expired one hour later
    return HeartbeatMonitor.objects.create(
        name="testing.beat1", enabled=True, timeout=timedelta(hours=1), last_beat=NOON
    )


@pytest.fixture
@freeze_time(NOON)
def beat2():
    # Should not be expired one hour later
    return HeartbeatMonitor.objects.create(
        name="testing.beat2",
        enabled=True,
        timeout=timedelta(hours=1, minutes=8),
        last_beat=NOON,
    )


@pytest.fixture
@freeze_time(NOON)
def beat3():
    # Should be ignored in all tests
    return HeartbeatMonitor.objects.create(
        name="testing.beat3",
        enabled=False,
        timeout=timedelta(minutes=1),
        last_beat=NOON,
    )


@pytest.mark.django_db
def test_check_empty_db():
    """See that an empty database doesn't crash."""
    assert check_expired_heartbeats() is None
    assert check_heartbeats() == {"__all__": True}


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_check_expired(beat1, beat2, beat3):
    """See that the checks themselves return proper data."""
    assert check_expired_heartbeats() == ["testing.beat1"]
    assert check_heartbeats() == {
        "__all__": False,
        "testing.beat1": True,
        "testing.beat2": False,
    }


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_expired_names(beat1, beat2, beat3):
    assert HeartbeatMonitor.objects.expired_names() == [
        "testing.beat1",
        "testing.beat3",
    ]
    assert HeartbeatMonitor.objects.enabled().expired_names() == ["testing.beat1"]


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_update_heartbeat(beat1):
    """See that ``last_beat`` is properly updated."""
    assert beat1.is_expired
    update_heartbeat(beat1.name)

    # Should not have created new objects, but update existing.
    assert HeartbeatMonitor.objects.count() == 1

    beat1.refresh_from_db()
    assert not beat1.is_expired


@pytest.mark.django_db
def test_update_heartbeat_auto_creates():
    """See that the first call to update_heartbeat() auto-creates."""
    assert HeartbeatMonitor.objects.count() == 0

    update_heartbeat("testing.autocreate1", default_timeout=timedelta(days=1))
    update_heartbeat("testing.autocreate1", default_timeout=timedelta(days=2))

    # Should not have created new objects, but update existing.
    assert HeartbeatMonitor.objects.count() == 1

    # Should only assign default_timeout in the first call.
    beat = HeartbeatMonitor.objects.get(name="testing.autocreate1")
    assert beat.timeout == timedelta(days=1)


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_update_heartbeat_timeout(beat1):
    assert beat1.is_expired
    update_heartbeat(beat1.name, timeout=timedelta(days=3))

    # Should not have created new objects, but update existing.
    assert HeartbeatMonitor.objects.count() == 1

    beat1.refresh_from_db()
    assert not beat1.is_expired
    assert beat1.timeout == timedelta(days=3)


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_update_heartbeat_on_success(beat1):
    assert beat1.is_expired

    @update_heartbeat_on_success(beat1.name)
    def foo(x=1):
        return x

    assert foo(x=2) == 2
    beat1.refresh_from_db()
    assert not beat1.is_expired


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_update_heartbeat_on_success_exception(beat1):
    assert beat1.is_expired

    @update_heartbeat_on_success(beat1.name)
    def foo():
        raise ValueError()

    with pytest.raises(ValueError):
        foo()

    beat1.refresh_from_db()
    assert beat1.is_expired


@pytest.mark.django_db
@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_is_expired(beat1, beat2, beat3):
    assert beat1.is_expired
    assert not beat2.is_expired
    assert beat3.is_expired


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_remaining_time(beat1, beat2):
    assert beat1.remaining_time == timedelta(minutes=-1)
    assert beat2.remaining_time == timedelta(minutes=7)


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_admin_list_view(admin_client, beat1, beat2, beat3):
    """See that the admin list renders and displays the status.

    By adding ?o=1.2.3.4 the ordering of all columns is tested too.
    This makes sure the 'admin_order_field' also works.
    """
    url = (
        reverse("admin:django_healthchecks_heartbeatmonitor_changelist") + "?o=1.2.3.4"
    )
    response = admin_client.get(url)
    assert response.status_code == 200
    content = response.render().content  # make sure template rendering works
    assert b"icon-alert.svg" in content


@pytest.mark.django_db
@freeze_time(ONE_HOUR_LATER)
def test_admin_change_view(admin_client, beat1):
    """See that the admin page renders without fieldset issues."""
    url = reverse("admin:django_healthchecks_heartbeatmonitor_change", args=(beat1.pk,))
    response = admin_client.get(url)
    assert response.status_code == 200
    content = response.render().content  # make sure template rendering works
    assert b"icon-alert.svg" in content
