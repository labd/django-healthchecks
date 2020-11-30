from django.urls import include, path
from django.contrib import admin

import django_healthchecks.urls

urlpatterns = [
    path("^admin/", admin.site.urls),
    path("^healthchecks", include(django_healthchecks.urls)),
]
