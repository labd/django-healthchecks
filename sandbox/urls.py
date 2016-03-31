from django.conf.urls import url, include

urlpatterns = [
    url(r'^healthchecks/', include('django_healthchecks.urls')),
]
