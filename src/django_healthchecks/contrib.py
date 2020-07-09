import uuid

from django.core.cache import cache
from django.db import connection

MIGRATION_CACHE = False


def check_database():
    """Check if the application can perform a dummy sql query"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1; -- Healthcheck")
        row = cursor.fetchone()
    return row[0] == 1


def check_cache_default():
    """Check if the application can connect to the default cached and
    read/write some dummy data.

    """
    dummy = str(uuid.uuid4())
    key = "healthcheck:%s" % dummy
    cache.set(key, dummy, timeout=5)
    cached_value = cache.get(key)
    return cached_value == dummy


def check_dummy_true():
    return True


def check_dummy_false(request):
    return False


def check_remote_addr(request):
    return request.META["REMOTE_ADDR"]


def check_expired_heartbeats():
    """Check which heartbeats have expired."""
    from django_healthchecks.heartbeats import get_expired_heartbeats

    return get_expired_heartbeats() or None


def check_heartbeats():
    """Give a dict of each check and it's status."""
    from django_healthchecks.heartbeats import get_heartbeat_statuses

    return get_heartbeat_statuses() or None


def check_open_migrations():
    """
    Check if all migrations have run.

    Cache this check on succesfull run as to reduce disk io.
    """
    global MIGRATION_CACHE
    if MIGRATION_CACHE:
        return True

    from django.conf import ImproperlyConfigured
    from django.db.migrations.executor import MigrationExecutor

    try:
        executor = MigrationExecutor(connection)
    except ImproperlyConfigured:
        # No databases are configured (or the dummy one)
        return None

    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    if plan:
        return False

    if not MIGRATION_CACHE:
        MIGRATION_CACHE = True
    return MIGRATION_CACHE
