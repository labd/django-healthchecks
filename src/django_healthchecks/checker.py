import base64
import functools
import inspect
from importlib import import_module

import requests
from django.conf import settings
from django.utils.encoding import force_text


try:
    from django.utils.module_loading import import_string
except ImportError:
    def import_string(value):
        module_name, func_name = value.rsplit('.', 1)
        module = import_module(module_name)
        return getattr(module, func_name)


class PermissionDenied(Exception):
    pass


def create_report(request=None):
    """Run all checks and return a tuple containing results and boolean to
    indicate to indicate if all things are healthy.

    """
    report = {}
    has_error = False

    for service, check_func in _get_check_functions(request=request):
        report[service] = check_func() or False

        if not report[service]:
            has_error = True
    return report, not has_error


def create_service_result(service, request=None):
    functions = list(_get_check_functions(name=service, request=request))
    if not functions:
        return

    check_func = functions[0][1]
    result = check_func() or False
    return result


def _get_check_functions(name=None, request=None):
    checks = _get_registered_health_checks()
    if not checks or (name and name not in checks):
        raise StopIteration()

    checks = _filter_checks_on_permission(request, checks)
    if not checks or (name and name not in checks):
        raise PermissionDenied()

    for service, func_string in checks.items():
        if name and name != service:
            continue

        if callable(func_string):
            check_func = func_string
        elif func_string.startswith(('https://', 'http://')):
            check_func = _http_healthcheck_func(func_string)
        else:
            check_func = import_string(func_string)

        spec = inspect.getargspec(check_func)
        if spec.args == ['request']:
            check_func = functools.partial(check_func, request)

        yield service, check_func


def _get_registered_health_checks():
    return getattr(settings, 'HEALTH_CHECKS', {})


def _http_healthcheck_func(url):
    def handle_remote_request():
        try:
            response = requests.get(url, timeout=_get_http_healthcheck_timeout())
        except requests.exceptions.RequestException:
            return False

        if response.ok:
            return response.json()
        return False

    return handle_remote_request


def _get_http_healthcheck_timeout():
    return getattr(settings, 'HEALTH_CHECKS_HTTP_TIMEOUT', 0.5)


def _filter_checks_on_permission(request, checks):
    permissions = getattr(settings, 'HEALTH_CHECKS_BASIC_AUTH', {})
    if not permissions:
        return checks

    allowed = {}
    for name in checks.keys():
        required_credentials = permissions.get(name, permissions.get('*'))

        if required_credentials:
            credentials = _get_basic_auth(request)
            if not credentials or credentials not in required_credentials:
                continue

        allowed[name] = checks[name]
    return allowed


def _get_basic_auth(request):
    auth = request.META.get('HTTP_AUTHORIZATION')
    if not auth:
        return

    auth = auth.split()
    if len(auth) == 2 and force_text(auth[0]).lower() == u'basic':
        credentials = base64.b64decode(auth[1]).decode('latin-1')
        return tuple(credentials.split(':'))
