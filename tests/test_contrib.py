import pytest

from django_healthchecks import contrib


@pytest.mark.django_db
def test_check_database():
    assert contrib.check_database()
