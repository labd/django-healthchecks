import uuid

from django.core.cache import cache
from django.db import connection


def check_database():
    """Check if the application can perform a dummy sql query"""
    cursor = connection.cursor()
    cursor.execute('SELECT 1; -- Healthcheck')
    row = cursor.fetchone()
    return row[0] == 1


def check_cache_default():
    """Check if the application can connect to the default cached and
    read/write some dummy data.

    """
    dummy = str(uuid.uuid4())
    key = 'healthcheck:%s' % dummy
    cache.set(key, dummy, timeout=5)
    cached_value = cache.get(key)
    return cached_value == dummy


def check_dummy_true():
    return True


def check_dummy_false():
    return False


def check_remote_addr(request):
    return request.META['REMOTE_ADDR']
