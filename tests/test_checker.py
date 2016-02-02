from django_healthchecks import checker


def test_create_report(settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true'
    }
    result, is_healthy = checker.create_report()
    expected = {
        'database': True
    }

    assert result == expected
    assert is_healthy is True


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
