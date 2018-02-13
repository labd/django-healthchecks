import base64

from django_healthchecks import checker

import requests
import requests_mock


def test_create_report(settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true',
        'remote_service': 'https://test.com/api/healthchecks/',
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            'https://test.com/api/healthchecks/',
            text='{"cache_default": true}')
        result, is_healthy = checker.create_report()

    expected = {
        'database': True,
        'remote_service': {'cache_default': True},
    }

    assert result == expected
    assert is_healthy is True


def test_service_timeout(settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true',
        'timeout_service': 'http://timeout.com/api/healthchecks/',
    }

    with requests_mock.Mocker() as mock:
        mock.register_uri(
            'GET', 'http://timeout.com/api/healthchecks/',
            exc=requests.exceptions.Timeout)
        result, is_healthy = checker.create_report()

    expected = {
        'database': True,
        'timeout_service': False
    }

    assert result == expected
    assert is_healthy is False


def test_create_report_err(settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true',
        'i_fail': 'django_healthchecks.contrib.check_dummy_false',
    }
    result, is_healthy = checker.create_report()
    expected = {
        'database': True,
        'i_fail': False,
    }

    assert result == expected
    assert is_healthy is False


def test_create_service_result(settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true'
    }
    result = checker.create_service_result('database')
    assert result is True


def test_create_service_result_unknown(settings):
    result = checker.create_service_result('database')
    assert result is None


def test_create_with_request(rf, settings):
    settings.HEALTH_CHECKS = {
        'remote_addr': 'django_healthchecks.contrib.check_remote_addr'
    }
    request = rf.get('/')
    result = checker.create_service_result('remote_addr', request)
    assert result == '127.0.0.1'


def test_filter_checks_on_permission(rf, settings):
    checks = {
        'public': 'django_healthchecks.contrib.check_dummy_true',
        'private': 'django_healthchecks.contrib.check_dummy_true'
    }

    settings.HEALTH_CHECKS_BASIC_AUTH = {
        '*': [('user', 'password')],
        'public': [],
    }

    request = rf.get('/')
    result = checker._filter_checks_on_permission(request, checks)
    assert result == {
        'public': 'django_healthchecks.contrib.check_dummy_true',
    }

    request = rf.get(
        '/', HTTP_AUTHORIZATION=b'Basic ' + base64.b64encode(b'user:password'))

    result = checker._filter_checks_on_permission(request, checks)
    assert result == {
        'public': 'django_healthchecks.contrib.check_dummy_true',
        'private': 'django_healthchecks.contrib.check_dummy_true'
    }
