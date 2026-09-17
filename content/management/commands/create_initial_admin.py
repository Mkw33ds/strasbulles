import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crée le premier compte administrateur depuis les variables d’environnement."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not all([username, email, password]):
            raise CommandError(
                "Définissez DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL "
                "et DJANGO_SUPERUSER_PASSWORD."
            )
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Administrateur {username} créé."))
        else:
            self.stdout.write(f"Le compte {username} existe déjà ; aucune modification.")
