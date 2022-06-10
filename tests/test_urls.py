from django.contrib import admin
from django.urls import include, path

import django_healthchecks.urls

urlpatterns = [
    path("^admin/", admin.site.urls),
    path("^healthchecks", include(django_healthchecks.urls)),
]
