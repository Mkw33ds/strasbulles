from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.contrib.redirects.models import Redirect
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, Site

from content.models import (
    AuthorIndexPage,
    AuthorPage,
    BlogIndexPage,
    BlogPage,
    Category,
    ContactPage,
    EventIndexPage,
    EventPage,
    FestivalArchiveIndexPage,
    FestivalEditionPage,
    FestivalPage,
    HomePage,
    StandardPage,
    Venue,
)


def ensure_child(parent, model, slug, **fields):
    existing = parent.get_children().filter(slug=slug).first()
    if existing:
        return existing.specific
    page = model(title=fields.pop("title"), slug=slug, **fields)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


def ensure_seed_image(filename, title, description):
    image_model = get_image_model()
    image = image_model.objects.filter(title=title).first()
    if image:
        return image
    source = settings.BASE_DIR / "content" / "seed_assets" / filename
    if not source.exists():
        return None
    with source.open("rb") as source_file:
        image = image_model(
            title=title,
            description=description,
            collection=Collection.get_first_root_node(),
        )
        image.file.save(filename, File(source_file), save=True)
    return image


class Command(BaseCommand):
    help = "Charge un jeu de contenu français initial sans créer de doublons."

    def handle(self, *args, **options):
        root = Page.get_first_root_node()
        home = ensure_child(
            root,
            HomePage,
            "accueil",
            title="Accueil",
            hero_title="Strasbulles, la bande dessinée en grand",
            hero_text="Festival, rencontres et lectures : le neuvième art se vit toute l’année à Strasbourg.",
            association_intro=(
                "<p>Depuis sa création en 2007, l’association Alsace Bande Dessinée "
                "promeut les actions et manifestations autour de la bande dessinée, en Alsace et ailleurs.</p>"
            ),
            membership_text="Rejoignez les bénévoles et soutenez des rendez-vous culturels ouverts à toutes et tous.",
        )
        poster = ensure_seed_image(
            "strasbulles-automne.png",
            "Affiche Strasbulles d’Automne",
            "Affiche illustrée de Strasbulles d’Automne, les 31 octobre et 1er novembre à Strasbourg.",
        )
        if poster and home.hero_image_id != poster.pk:
            home.hero_image = poster
            home.save_revision().publish()
        site, _ = Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": "localhost",
                "port": 8000,
                "root_page": home,
                "site_name": "Strasbulles",
            },
        )

        ensure_child(
            home,
            FestivalPage,
            "strasbulles",
            title="Le festival Strasbulles",
            introduction="Le festival européen de la bande dessinée de Strasbourg.",
            dates="Prochaine édition : dates à confirmer",
            admission="Tarifs à confirmer avant publication",
        )
        authors = ensure_child(
            home,
            AuthorIndexPage,
            "auteurs-et-autrices",
            title="Auteurs et autrices",
            introduction="Rencontrez les artistes invités par Alsace Bande Dessinée.",
        )
        archive = ensure_child(
            home,
            FestivalArchiveIndexPage,
            "archives",
            title="Archives",
            introduction="Retrouvez les éditions qui ont façonné l’histoire de Strasbulles.",
        )
        association = ensure_child(
            home,
            StandardPage,
            "association",
            title="L’association",
            introduction="Une association au service de la bande dessinée depuis 2007.",
            body=[
                ("heading", "Promouvoir le neuvième art"),
                (
                    "rich_text",
                    "<p>Alsace Bande Dessinée met en relation maisons d’édition, libraires, "
                    "artistes, lecteurs, lectrices et collectionneurs.</p>",
                ),
            ],
        )
        ensure_child(
            association,
            StandardPage,
            "classes-de-bande-dessinee",
            title="Classes de bande dessinée",
            introduction="Des journées d’animation scolaire pour découvrir les étapes de création d’une BD.",
            body=[
                (
                    "rich_text",
                    "<p>Ces rencontres permettent aux élèves du CE1 à la 3e d’échanger avec des "
                    "artistes confirmés et de réaliser leur propre planche.</p>",
                )
            ],
        )
        ensure_child(
            association,
            StandardPage,
            "partenariats-solidaires",
            title="Partenariats solidaires",
            introduction="Des actions partagées avec les acteurs associatifs et culturels du territoire.",
        )
        membership = ensure_child(
            association,
            StandardPage,
            "adherer-soutenir",
            title="Adhérer / Soutenir",
            introduction="Les modalités d’adhésion et de soutien sont à confirmer avant la mise en ligne.",
        )
        home.membership_page = membership
        home.save_revision().publish()

        event_index = ensure_child(
            home,
            EventIndexPage,
            "evenements",
            title="Événements",
            introduction="Les prochains rendez-vous et les archives de l’association.",
        )
        venue, _ = Venue.objects.get_or_create(
            name="Lieu à confirmer", defaults={"address": "Adresse à confirmer avant publication"}
        )
        next_year = timezone.localdate().year + 1
        tz = timezone.get_current_timezone()
        ensure_child(
            event_index,
            EventPage,
            "prochain-rendez-vous",
            title="Prochain rendez-vous Strasbulles",
            introduction="Événement de démonstration : date, lieu, programme et tarif à confirmer avant publication.",
            start=timezone.make_aware(datetime(next_year, 10, 31, 10), tz),
            end=timezone.make_aware(datetime(next_year, 11, 1, 18), tz),
            venue=venue,
            admission="À confirmer",
            organiser="Alsace Bande Dessinée",
            featured=True,
        )
        ensure_child(
            event_index,
            EventPage,
            "strasbulles-automne-archive",
            title="Strasbulles d’Automne — archive",
            introduction="Une rencontre avec des auteurs et autrices de bande dessinée et d’illustration.",
            start=timezone.make_aware(datetime(2020, 10, 31, 10), tz),
            end=timezone.make_aware(datetime(2020, 11, 1, 18), tz),
            venue=venue,
            admission="Archive : tarif historique à vérifier",
            organiser="Alsace Bande Dessinée",
        )
        ensure_child(
            home,
            StandardPage,
            "rencontres",
            title="Les rencontres",
            introduction="Les Rencontres d’Alsace Bande Dessinée réunissent amateurs, professionnels et artistes.",
            body=[
                (
                    "rich_text",
                    "<p>Ces deux journées donnent aux passionnés la possibilité de vendre des livres, "
                    "de rencontrer des artistes de la région et de découvrir une exposition consacrée au neuvième art.</p>",
                )
            ],
        )
        blog = ensure_child(
            home,
            BlogIndexPage,
            "chroniques",
            title="Chroniques",
            introduction="Nos lectures, coups de cœur et actualités du neuvième art.",
        )
        reviews, _ = Category.objects.get_or_create(name="Coups de cœur", slug="coups-de-coeur")
        articles = [
            (
                "moi-ce-que-jaime-cest-les-monstres",
                "Moi, ce que j’aime, c’est les monstres — Livre premier",
                "Un roman graphique singulier d’Emil Ferris, publié par Monsieur Toussaint Louverture.",
            ),
            (
                "joe-shuster",
                "Joe Shuster",
                "Un roman graphique passionnant consacré au dessinateur et cocréateur de Superman.",
            ),
            (
                "baker-street-all-you-need-is-holmes",
                "Baker Street — All you need is Holmes",
                "Une intégrale pleine d’humour librement inspirée de Sherlock Holmes et du docteur Watson.",
            ),
        ]
        for slug, title, intro in articles:
            ensure_child(
                blog,
                BlogPage,
                slug,
                title=title,
                introduction=intro,
                publication_date=datetime(2026, 8, 10).date(),
                category=reviews,
                publisher="À vérifier dans le contenu source",
            )
        for year in range(2008, 2022):
            ensure_child(
                archive,
                FestivalEditionPage,
                str(year),
                title=f"Strasbulles {year}",
                year=year,
                introduction="Affiche et documents d’archive à confirmer avant import.",
            )
        for slug, name, role in [
            ("christian-peultier", "Christian Peultier", "Auteur et dessinateur"),
            ("christophe-carmona", "Christophe Carmona", "Auteur et illustrateur"),
            ("jean-francois-cellier", "Jean-François Cellier", "Auteur et dessinateur"),
        ]:
            ensure_child(
                authors,
                AuthorPage,
                slug,
                title=name,
                discipline=role,
                biography="<p>Biographie et présence aux éditions à confirmer avant publication.</p>",
                featured=True,
            )
        ensure_child(
            home,
            ContactPage,
            "contact",
            title="Contact",
            introduction="Contactez l’équipe d’Alsace Bande Dessinée.",
        )
        ensure_child(
            home,
            StandardPage,
            "mentions-legales",
            title="Mentions légales",
            introduction="Les informations d’identification doivent être complétées dans le CMS avant la mise en ligne.",
        )
        ensure_child(
            home,
            StandardPage,
            "politique-de-confidentialite",
            title="Politique de confidentialité",
            introduction="Le formulaire traite les coordonnées uniquement pour répondre à la demande et ne les conserve pas en base.",
        )

        redirect_map = {
            "/lassociation/": association,
            "/adherer-soutenir/": membership,
            "/evenements-a-venir/": event_index,
            "/annonces/": home.get_children().get(slug="rencontres").specific,
            "/mentions-legles/": home.get_children().get(slug="mentions-legales").specific,
            "/politique-de-confidentialites/": home.get_children()
            .get(slug="politique-de-confidentialite")
            .specific,
        }
        for old_path, target in redirect_map.items():
            Redirect.objects.update_or_create(
                old_path=old_path,
                site=site,
                defaults={"redirect_page": target, "is_permanent": True},
            )
        self.stdout.write(self.style.SUCCESS("Contenu initial chargé ou mis à jour sans doublons."))
