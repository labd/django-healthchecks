Simple Django app/framework to publish health check for monitoring purposes

Usage
=====

Add the following to your urls.py:

    url(r'^healthchecks/', include('django_healthchecks.urls')),

Add a setting with the available healthchecks:

    HEALTH_CHECKS = {
        'postgresql': 'django_healthchecks.contrib.check_database',
        'solr': 'your_project.lib.healthchecks.check_solr',
    }

