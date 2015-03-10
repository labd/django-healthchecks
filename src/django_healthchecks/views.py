from django.http import JsonResponse, HttpResponse
from django.http.response import Http404
from django.views.generic import View

from django_healthchecks.checker import create_report, create_service_result


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        report = create_report()
        return JsonResponse(report)


class HealthCheckServiceView(View):
    def get(self, request, service, *args, **kwargs):
        result = create_service_result(service)
        if result is None:
            raise Http404()

        if result:
            return HttpResponse('true')
        return HttpResponse('false', status=500)
