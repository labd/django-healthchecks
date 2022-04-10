import pytest


@pytest.fixture
def contrib():
    # The django_healthchecks contrib module imports `django.core.cache`. The cache will be configured using the settings
    # at import time which makes it difficult to override the cache backend in individual tests.
    # As a workaround, we import the contrib module here and use it as a fixture so the cache will only be configured
    # when we use the contrib module in our tests.
    from django_healthchecks import contrib

    return contrib


@pytest.mark.django_db
def test_check_database(contrib):
    assert contrib.check_database()


def test_check_cache_default(contrib):
    assert contrib.check_cache_default()


def test_check_cache_default_down(settings, contrib):
    """Check if the application can connect to the default cached and
    read/write some dummy data.

    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
    assert not contrib.check_cache_default()


@pytest.mark.django_db
def test_check_heartbeats(contrib):
    assert not contrib.MIGRATION_CACHE
    assert contrib.check_open_migrations()
    assert contrib.MIGRATION_CACHE
