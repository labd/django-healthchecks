===================
django-healthchecks
===================

Simple Django app/framework to publish health check for monitoring purposes

Features:

* Custom checks via Python functions
* Remote healthchecks
* Heartbeat monitoring


Status
======
.. image:: https://github.com/mvantellingen/django-healthchecks/workflows/Python%20Tests/badge.svg
    :target: https://github.com/mvantellingen/django-healthchecks/actions?query=workflow%3A%22Python+Tests%22

.. image:: http://codecov.io/github/mvantellingen/django-healthchecks/coverage.svg?branch=master
    :target: http://codecov.io/github/mvantellingen/django-healthchecks?branch=master

.. image:: https://img.shields.io/pypi/v/django-healthchecks.svg
    :target: https://pypi.python.org/pypi/django-healthchecks/

Installation
============

.. code-block:: shell

   pip install django_healthchecks


Usage
=====

Add the following to your urls.py:


.. code-block:: python

    url(r'^healthchecks/', include('django_healthchecks.urls')),


Add a setting with the available healthchecks:

.. code-block:: python

    HEALTH_CHECKS = {
        'postgresql': 'django_healthchecks.contrib.check_database',
        'cache_default': 'django_healthchecks.contrib.check_cache_default',
        'solr': 'your_project.lib.healthchecks.check_solr',
    }


You can also include healthchecks over http. This is useful when you want to
monitor if depending services are up:

.. code-block:: python

    HEALTH_CHECKS = {
        ...
        'my_microservice': 'https://my-service.services.internal/healthchecks/',
        ...
    }


By default, http health checks will time out after 500ms. You can override this
as follows:

.. code-block:: python

    HEALTH_CHECKS_HTTP_TIMEOUT = 0.5


By default the status code is always 200, you can change this to something
else by using the `HEALTH_CHECKS_ERROR_CODE` setting:

.. code-block:: python

    HEALTH_CHECKS_ERROR_CODE = 503


You can also add some simple protection to your healthchecks via basic auth.
This can be specified per check or a wildcard can be used `*`.

.. code-block:: python

    HEALTH_CHECKS_BASIC_AUTH = {
        '*': [('admin', 'pass')],
        'solr': [],
    }


Using heartbeats
================

Heartbeats give a periodic update, to see whether an service was recently active.
When the service doesn't report back within timeout, a healthcheck can be triggered.
To use heartbeats, add the application to the ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "django_healthchecks",
    ]

Include one of these checks:

.. code-block:: python

    HEALTH_CHECKS = {
        ...
        'heartbeats': 'django_healthchecks.contrib.check_heartbeats'
        ...
        'expired_heartbeats': 'django_healthchecks.contrib.check_expired_heartbeats',
        ...
    }

Optionally, define an initial timeout:

.. code-block:: python

    HEALTHCHECKS_DEFAULT_HEARTBEAT_TIMEOUT = timedelta(days=1)

Let your code track the beats:

.. code-block:: python

    from datetime import timedelta
    from django_healthchecks.heartbeats import update_heartbeat

    update_heartbeat("myservice.name", default_timeout=timedelta(days=2))

Or use the decorator:

.. code-block:: python

    from django_healthchecks.heartbeats import update_heartbeat_on_success

    @update_heartbeat_on_success("myservice.name", default_timeout=...)
    def long_running_task():
        ....

Each time ``update_heartbeat()`` is called, the heartbeat is reset.
When a heartbeat didn't receive an update before it's ``timeout``,
the service name be mentioned in the ``check_expired_heartbeats`` check.

Updating timeouts
~~~~~~~~~~~~~~~~~

The ``default_timeout`` parameter is only assigned upon creation. Any updates
happen through the Django admin. To update the timeout automatically on
code deployment, use the ``timeout`` parameter instead. This will replace the
stored timeout value each time the ``update_heartbeat()`` function
is called, erasing any changes made in the Django admin.

