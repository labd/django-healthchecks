from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.views.decorators.cache import cache_control
from django.views.generic import View

from django_healthchecks.checker import create_report, create_service_result


class NoCacheMixin(object):

    @classmethod
    def as_view(cls, **kwargs):
        view = super(NoCacheMixin, cls).as_view(**kwargs)
        return cache_control(
            private=True, no_cache=True, no_store=True, max_age=0)(view)


class HealthCheckView(NoCacheMixin, View):

    def get(self, request, *args, **kwargs):
        report, is_healthy = create_report(request=request)
        status_code = 200 if is_healthy else _get_err_status_code()
        return JsonResponse(report, status=status_code)


class HealthCheckServiceView(NoCacheMixin, View):
    def get(self, request, service, *args, **kwargs):
        result = create_service_result(service=service, request=request)
        if result is None:
            raise Http404()

        if result in (True, False):
            status_code = 200 if result else _get_err_status_code()
            return HttpResponse(str(result).lower(), status=status_code)

        return HttpResponse(result)


def _get_err_status_code():
    return getattr(settings, 'HEALTH_CHECKS_ERROR_CODE', 200)
