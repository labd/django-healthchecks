from django.db import connection


def check_database():
    """Check if the application can perform a dummy sql query"""
    cursor = connection.cursor()
    cursor.execute('SELECT 1; -- Healthcheck')
    row = cursor.fetchone()
    return row[0] == 1


def check_dummy_true():
    return True


def check_dummy_false():
    return False
