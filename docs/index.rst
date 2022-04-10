===================
django-healthchecks
===================

Simple Django app/framework to publish health check for monitoring purposes

Installation
============

.. code-block:: shell

   pip install django_healthchecks
   
Usage
=====

Add the following to your urls.py:


.. code-block:: python

    path(r'healthchecks/', include('django_healthchecks.urls')),

Add a setting with the available healthchecks:

.. code-block:: python

    HEALTH_CHECKS = {
        'postgresql': 'django_healthchecks.contrib.check_database',
        'cache_default': 'django_healthchecks.contrib.check_cache_default',
        'solr': 'your_project.lib.healthchecks.check_solr',
    }

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
