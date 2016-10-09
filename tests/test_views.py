import json
from collections import OrderedDict

import pytest
from django.http import Http404

from django_healthchecks import views


def test_index_view(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true',
        'redis': 'django_healthchecks.contrib.check_dummy_false',
    }

    request = rf.get('/')
    view = views.HealthCheckView()
    result = view.dispatch(request)

    data = json.loads(result.content.decode(result.charset))
    assert data == {
        'database': True,
        'redis': False,
    }


def test_service_view(rf, settings):
    settings.HEALTH_CHECKS = OrderedDict([
        ('redis', 'django_healthchecks.contrib.check_dummy_false'),
        ('database', 'django_healthchecks.contrib.check_dummy_true'),
    ])

    request = rf.get('/')
    view = views.HealthCheckServiceView()
    result = view.dispatch(request, service='database')

    assert result.status_code == 200
    assert result.content == b'true'


def test_service_view_err(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_false'
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView()

    result = view.dispatch(request, service='database')
    assert result.status_code == 200
    assert result.content == b'false'


def test_service_view_err_custom_code(rf, settings):
    settings.HEALTH_CHECKS_ERROR_CODE = 500
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_false'
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView()

    result = view.dispatch(request, service='database')
    assert result.status_code == 500
    assert result.content == b'false'


def test_service_view_404(rf):
    request = rf.get('/')
    view = views.HealthCheckServiceView()

    with pytest.raises(Http404):
        view.dispatch(request, service='database')


def test_service_require_auth(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true'
    }
    settings.HEALTH_CHECKS_BASIC_AUTH = {
        '*': [('user', 'password')],
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView()

    result = view.dispatch(request, service='database')
    assert result.status_code == 401
