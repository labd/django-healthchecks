from django.conf.urls import url

from django_healthchecks import views

urlpatterns = [
    url(r'^$', views.HealthCheckView.as_view(), name='index'),
    url(r'^(?P<service>.*)$', views.HealthCheckServiceView.as_view(),
        name='service'),
]
