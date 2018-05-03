from django.contrib import admin
from django.conf.urls import url, include

import django_healthchecks.urls

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^healthchecks', include(django_healthchecks.urls))
]
