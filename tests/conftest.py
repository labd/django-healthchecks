from django.conf import settings


def pytest_configure():
    settings.configure(
        HEALTH_CHECKS={},
        MIDDLEWARE_CLASSES=[],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite',
            },
        }
    )
