import pytest
from django.core.management import call_command
from wagtail.models import Site


@pytest.fixture
def seeded(db):
    call_command("seed_content", verbosity=0)
    return Site.objects.get(is_default_site=True).root_page.specific
