import six
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.views.decorators.cache import cache_control
from django.views.generic import View

from django_healthchecks.checker import (
    PermissionDenied,
    create_report,
    create_service_result,
)


class NoCacheMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(NoCacheMixin, cls).as_view(**kwargs)
        return cache_control(private=True, no_cache=True, no_store=True, max_age=0)(
            view
        )


class GetErrorStatusCodeMixin(object):
    def get_error_stats_code(self, request):
        """override status code based on header but only allow int and within
        100-599 range.

        """
        status_header = getattr(
            settings, "HEALTH_CHECKS_ERROR_CODE_HEADER", "X-HEALTHCHECK-ERROR-CODE"
        )

        requested_status_code = request.headers.get(status_header)
        if requested_status_code:
            try:
                # validate status code can be used
                status_code = int(requested_status_code)
                if 100 <= status_code <= 599:
                    return status_code

            except (TypeError, ValueError):
                pass

        # current default behaviour
        return getattr(settings, "HEALTH_CHECKS_ERROR_CODE", 200)


class HealthCheckView(NoCacheMixin, GetErrorStatusCodeMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            report, is_healthy = create_report(request=request)
        except PermissionDenied:
            response = HttpResponse(status=401)
            response["WWW-Authenticate"] = 'Basic realm="Healthchecks"'
            return response
        status_code = 200 if is_healthy else self.get_error_stats_code(request)
        return JsonResponse(report, status=status_code)


class HealthCheckServiceView(NoCacheMixin, GetErrorStatusCodeMixin, View):
    def get(self, request, service, *args, **kwargs):
        service_path = list(filter(lambda s: s, service.split("/")))
        service = service_path.pop(0)

        try:
            result = create_service_result(service=service, request=request)
        except PermissionDenied:
            response = HttpResponse(status=401)
            response["WWW-Authenticate"] = 'Basic realm="Healthchecks"'
            return response

        return self.create_result_response(request, service, result, service_path)

    def create_result_response(self, request, service, result, service_path):
        for nested in service_path:
            result = result.get(nested, None)
            if result is None:
                break

        if result is None:
            raise Http404()

        if result in (True, False):
            status_code = 200 if result else self.get_error_stats_code(request)
            return HttpResponse(str(result).lower(), status=status_code)
        elif isinstance(result, six.string_types) or isinstance(result, bytes):
            return HttpResponse(result)
        else:
            # Django requires safe=False for non-dict values.
            return JsonResponse(result, safe=False)
