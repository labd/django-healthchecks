django-healthchecks
-------------------

Simple Django app/framework to publish health check for monitoring purposes

Status
======
.. image:: https://travis-ci.org/mvantellingen/django-healthchecks.svg?branch=master
    :target: https://travis-ci.org/mvantellingen/django-healthchecks

.. image:: http://codecov.io/github/mvantellingen/django-healthchecks/coverage.svg?branch=master 
    :target: http://codecov.io/github/mvantellingen/django-healthchecks?branch=master
    
.. image:: https://pypip.in/version/django_healthchecks/badge.svg
    :target: https://pypi.python.org/pypi/django_healthchecks/

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
