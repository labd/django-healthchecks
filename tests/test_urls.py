from django.conf.urls import include, url
from django.contrib import admin

import django_healthchecks.urls

urlpatterns = [
    url("^admin/", admin.site.urls),
    url("^healthchecks", include(django_healthchecks.urls)),
]
