import pytest
from django.core import cache

from django_healthchecks import contrib


@pytest.mark.django_db
def test_check_database():
    assert contrib.check_database()


def test_check_cache_default():
    cache.caches = cache.CacheHandler()
    assert contrib.check_cache_default()


def test_check_cache_default_down(settings):
    """Check if the application can connect to the default cached and
    read/write some dummy data.

    """
    cache.caches = cache.CacheHandler()
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
    assert not contrib.check_cache_default()


@pytest.mark.django_db
def test_check_heartbeats():
    assert not contrib.MIGRATION_CACHE
    assert contrib.check_open_migrations()
    assert contrib.MIGRATION_CACHE
