from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from wagtail.models import Page

from content.models import BlogPage, EventIndexPage, EventPage, Venue

pytestmark = pytest.mark.django_db


def test_homepage_contains_expected_french_content(client, seeded):
    response = client.get("/")
    assert response.status_code == 200
    assert "Strasbulles, la bande dessinée en grand" in response.content.decode()
    assert "Dernières chroniques" in response.content.decode()


def test_event_index_separates_future_and_past(client, seeded):
    response = client.get("/evenements/")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Prochain rendez-vous Strasbulles" in content
    assert "Strasbulles d’Automne — archive" in content
    assert content.index("À venir") < content.index("Événements passés")


def test_event_detail(client, seeded):
    event = EventPage.objects.live().filter(slug="prochain-rendez-vous").first()
    response = client.get(event.url)
    assert response.status_code == 200
    assert event.title in response.content.decode()
    assert "application/ld+json" in response.content.decode()


def test_article_detail_and_publication(client, seeded):
    article = BlogPage.objects.live().first()
    response = client.get(article.url)
    assert response.status_code == 200
    assert article.title in response.content.decode()
    assert "Article" in response.content.decode()


def test_draft_event_is_not_public(client, seeded):
    index_page = EventIndexPage.objects.first()
    venue = Venue.objects.first()
    draft = EventPage(
        title="Événement brouillon",
        slug="evenement-brouillon",
        introduction="Invisible",
        start=timezone.now() + timedelta(days=5),
        end=timezone.now() + timedelta(days=5, hours=2),
        venue=venue,
        live=False,
    )
    index_page.add_child(instance=draft)
    draft.save_revision()
    assert client.get(draft.url).status_code == 404
    assert "Événement brouillon" not in client.get(index_page.url).content.decode()


def test_contact_validation(client, seeded):
    response = client.post("/contact/", {"name": "", "email": "invalide"})
    assert response.status_code == 200
    assert "Ce champ est obligatoire" in response.content.decode()
    assert len(mail.outbox) == 0


@override_settings(CONTACT_RECIPIENT="contact@example.org")
def test_contact_email_delivery(client, seeded):
    response = client.post(
        "/contact/",
        {
            "name": "Camille Test",
            "email": "camille@example.org",
            "subject": "Question festival",
            "message": "Bonjour, je souhaite une information.",
            "consent": "on",
            "website": "",
        },
    )
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["contact@example.org"]


def test_legacy_redirect_is_permanent(client, seeded):
    response = client.get("/annonces/")
    assert response.status_code == 301
    assert response["Location"].endswith("/rencontres/")


def test_sitemap_and_error_page(client, seeded, settings):
    assert client.get("/sitemap.xml").status_code == 200
    settings.DEBUG = False
    response = client.get("/cette-page-nexiste-pas/")
    assert response.status_code == 404
    assert "Cette page a quitté la case" in response.content.decode()


def test_seed_command_is_idempotent(seeded):
    pages_before = Page.objects.count()
    articles_before = BlogPage.objects.count()
    call_command("seed_content", verbosity=0)
    assert Page.objects.count() == pages_before
    assert BlogPage.objects.count() == articles_before


def test_staff_groups_command(seeded):
    call_command("setup_staff_groups", verbosity=0)
    assert set(Group.objects.values_list("name", flat=True)) >= {
        "Administrateurs",
        "Rédacteurs",
        "Éditeurs",
    }
