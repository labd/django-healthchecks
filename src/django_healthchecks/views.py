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
        report = create_report()
        return JsonResponse(report)


class HealthCheckServiceView(NoCacheMixin, View):
    def get(self, request, service, *args, **kwargs):
        result = create_service_result(service)
        if result is None:
            raise Http404()

        if result in (True, False):
            return HttpResponse(str(result).lower())

        return HttpResponse(result)
