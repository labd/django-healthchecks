from django.urls import path

from django_healthchecks import views

urlpatterns = [
    path(r"", views.HealthCheckView.as_view(), name="index"),
    path(r"<str:service>/", views.HealthCheckServiceView.as_view(), name="service"),
]
