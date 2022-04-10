from django.conf import settings


def pytest_configure():
    settings.configure(
        HEALTH_CHECKS={},
        MIDDLEWARE_CLASSES=[],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "django_healthchecks",
        ],
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        },
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite",
            },
        },
        MIDDLEWARE=(
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ),
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {
                    "loaders": ("django.template.loaders.app_directories.Loader",),
                },
            },
        ],
        SECRET_KEY="django-insecure-2%2hup1&(r-6(88=)txivii25r^o%4-&00u5vgs#n93r#t8+y0",
        USE_TZ=True,
        ROOT_URLCONF="test_urls",
    )
