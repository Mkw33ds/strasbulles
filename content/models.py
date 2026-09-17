from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from .blocks import BaseStreamBlock, GalleryImageBlock, LinkBlock, ProgrammeBlock
from .forms import ContactForm


@register_snippet
class Category(models.Model):
    name = models.CharField("Nom", max_length=100, unique=True)
    slug = models.SlugField("Identifiant URL", max_length=100, unique=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Contributor(models.Model):
    name = models.CharField("Nom", max_length=150)
    biography = models.TextField("Présentation", blank=True)

    class Meta:
        verbose_name = "contributeur ou contributrice"
        verbose_name_plural = "contributeurs et contributrices"
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Venue(models.Model):
    name = models.CharField("Nom", max_length=200)
    address = models.TextField("Adresse postale", blank=True)
    accessibility = models.TextField("Informations d’accessibilité", blank=True)
    map_url = models.URLField("Lien vers le plan", blank=True)

    class Meta:
        verbose_name = "lieu"
        verbose_name_plural = "lieux"
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Partner(models.Model):
    name = models.CharField("Nom", max_length=200)
    logo = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Logo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    website = models.URLField("Site web", blank=True)
    is_featured = models.BooleanField("Afficher sur l’accueil", default=True)
    sort_order = models.PositiveIntegerField("Ordre", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("logo"),
        FieldPanel("website"),
        FieldPanel("is_featured"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        verbose_name = "partenaire"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


@register_snippet
class SocialLink(models.Model):
    label = models.CharField("Réseau", max_length=50)
    url = models.URLField("Adresse")

    class Meta:
        verbose_name = "lien social"
        verbose_name_plural = "liens sociaux"

    def __str__(self):
        return self.label


@register_snippet
class MenuLink(models.Model):
    label = models.CharField("Libellé", max_length=80)
    page = models.ForeignKey(
        Page,
        verbose_name="Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    external_url = models.URLField("Lien externe", blank=True)
    location = models.CharField(
        "Emplacement",
        max_length=10,
        choices=[("header", "En-tête"), ("footer", "Pied de page")],
        default="footer",
    )
    sort_order = models.PositiveIntegerField("Ordre", default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("page"),
        FieldPanel("external_url"),
        FieldPanel("location"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        verbose_name = "lien de navigation"
        ordering = ["sort_order", "label"]

    def __str__(self):
        return self.label

    @property
    def url(self):
        return self.page.url if self.page else self.external_url


@register_setting
class ContactSettings(BaseSiteSetting):
    organisation_name = models.CharField(
        "Nom de l’association", max_length=200, default="Alsace Bande Dessinée"
    )
    postal_address = models.TextField("Adresse postale", blank=True)
    phone = models.CharField("Téléphone", max_length=30, blank=True)
    public_email = models.EmailField("Adresse e-mail publique", blank=True)
    legal_identifier = models.CharField("Numéro RNA ou SIRET", max_length=100, blank=True)
    publication_director = models.CharField(
        "Direction de la publication", max_length=150, blank=True
    )

    panels = [
        FieldPanel("organisation_name"),
        FieldPanel("postal_address"),
        FieldPanel("phone"),
        FieldPanel("public_email"),
        FieldPanel("legal_identifier"),
        FieldPanel("publication_director"),
    ]


@register_setting
class FestivalSettings(BaseSiteSetting):
    festival_name = models.CharField("Nom du festival", max_length=200, default="Strasbulles")
    dates = models.CharField("Dates", max_length=200, blank=True)
    location = models.CharField("Lieu", max_length=200, blank=True)
    notice = models.CharField(
        "Mention de vérification",
        max_length=250,
        default="Dates et lieu à confirmer avant publication.",
        blank=True,
    )
    newsletter_enabled = models.BooleanField("Afficher l’inscription à l’infolettre", default=False)
    newsletter_url = models.URLField("Lien d’inscription", blank=True)


class SeoPage(Page):
    social_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image de partage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    promote_panels = Page.promote_panels + [FieldPanel("social_image")]

    class Meta:
        abstract = True


class HomePage(SeoPage):
    hero_eyebrow = models.CharField(
        "Surtitre", max_length=100, default="Festival européen de la BD"
    )
    hero_title = models.CharField("Titre de campagne", max_length=200, default="Strasbulles")
    hero_text = models.TextField("Introduction", blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Affiche ou image principale",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    primary_cta = StreamField(
        [("link", LinkBlock())], blank=True, max_num=1, verbose_name="Action principale"
    )
    association_intro = RichTextField("Présentation de l’association", blank=True)
    membership_title = models.CharField(
        "Titre de l’appel à adhésion",
        max_length=150,
        default="Faire vivre la bande dessinée en Alsace",
    )
    membership_text = models.TextField("Texte de l’appel à adhésion", blank=True)
    membership_page = models.ForeignKey(
        Page,
        verbose_name="Page Adhérer / Soutenir",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow"),
                FieldPanel("hero_title"),
                FieldPanel("hero_text"),
                FieldPanel("hero_image"),
                FieldPanel("primary_cta"),
            ],
            heading="En-tête",
        ),
        FieldPanel("association_intro"),
        MultiFieldPanel(
            [
                FieldPanel("membership_title"),
                FieldPanel("membership_text"),
                FieldPanel("membership_page"),
            ],
            heading="Adhésion",
        ),
    ]
    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)
        context.update(
            {
                "featured_event": EventPage.objects.live()
                .filter(end__gte=timezone.now(), featured=True)
                .order_by("start")
                .first(),
                "latest_posts": BlogPage.objects.live().order_by("-publication_date")[:3],
                "featured_authors": AuthorPage.objects.live().filter(featured=True)[:4],
                "editions": FestivalEditionPage.objects.live().order_by("-year")[:5],
                "partners": Partner.objects.filter(is_featured=True),
            }
        )
        return context


class StandardPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    body = StreamField(BaseStreamBlock(), blank=True, verbose_name="Contenu")

    content_panels = Page.content_panels + [FieldPanel("introduction"), FieldPanel("body")]
    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]


class FestivalPage(StandardPage):
    dates = models.CharField("Dates et horaires", max_length=250, blank=True)
    venue = models.ForeignKey(
        Venue,
        verbose_name="Lieu",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="festival_pages",
    )
    admission = models.CharField("Tarif ou entrée libre", max_length=150, blank=True)
    poster = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Affiche",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    programme = StreamField([("item", ProgrammeBlock())], blank=True, verbose_name="Programme")
    documents = StreamField(
        [("document", BaseStreamBlock.base_blocks["document"])],
        blank=True,
        verbose_name="Documents",
    )

    content_panels = StandardPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("dates"),
                FieldPanel("venue"),
                FieldPanel("admission"),
                FieldPanel("poster"),
            ],
            heading="Informations pratiques",
        ),
        FieldPanel("programme"),
        FieldPanel("documents"),
    ]


class AuthorIndexPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["content.AuthorPage"]

    def get_context(self, request):
        context = super().get_context(request)
        authors = AuthorPage.objects.child_of(self).live().order_by("title")
        query = request.GET.get("q", "").strip()
        edition = request.GET.get("edition", "").strip()
        if query:
            authors = authors.filter(title__icontains=query)
        if edition.isdigit():
            authors = authors.filter(editions__year=int(edition)).distinct()
        context.update(
            {
                "authors": authors,
                "query": query,
                "selected_edition": edition,
                "edition_years": FestivalEditionPage.objects.live()
                .order_by("-year")
                .values_list("year", flat=True),
            }
        )
        return context


class AuthorPage(SeoPage):
    portrait = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Portrait",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    portrait_alt = models.CharField("Texte alternatif du portrait", max_length=250, blank=True)
    biography = RichTextField("Biographie", blank=True)
    discipline = models.CharField("Discipline ou rôle", max_length=150, blank=True)
    country = models.CharField("Pays ou région", max_length=150, blank=True)
    website = models.URLField("Site web", blank=True)
    social_url = models.URLField("Réseau social", blank=True)
    bibliography = RichTextField("Bibliographie ou œuvres choisies", blank=True)
    featured = models.BooleanField("Mettre en avant", default=False)
    editions = ParentalManyToManyField(
        "content.FestivalEditionPage", verbose_name="Éditions", blank=True, related_name="guests"
    )

    parent_page_types = ["content.AuthorIndexPage"]
    content_panels = Page.content_panels + [
        FieldPanel("portrait"),
        FieldPanel("portrait_alt"),
        FieldPanel("biography"),
        MultiFieldPanel(
            [
                FieldPanel("discipline"),
                FieldPanel("country"),
                FieldPanel("website"),
                FieldPanel("social_url"),
            ],
            heading="Profil",
        ),
        FieldPanel("bibliography"),
        FieldPanel("editions"),
        FieldPanel("featured"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("biography"),
        index.FilterField("featured"),
    ]


class EventIndexPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["content.EventPage"]

    def get_context(self, request):
        context = super().get_context(request)
        events = EventPage.objects.child_of(self).live().select_related("venue")
        now = timezone.now()
        context["upcoming_events"] = events.filter(end__gte=now).order_by("start")
        context["past_events"] = events.filter(end__lt=now).order_by("-start")
        return context


class EventPage(SeoPage):
    introduction = models.TextField("Introduction courte", blank=True)
    body = StreamField(BaseStreamBlock(), blank=True, verbose_name="Description")
    start = models.DateTimeField("Début")
    end = models.DateTimeField("Fin")
    venue = models.ForeignKey(
        Venue,
        verbose_name="Lieu",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    address_override = models.TextField("Adresse spécifique", blank=True)
    map_url = models.URLField("Lien vers le plan", blank=True)
    admission = models.CharField("Tarif ou entrée libre", max_length=150, blank=True)
    booking_url = models.URLField("Réservation ou billetterie", blank=True)
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image principale",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField("Texte alternatif", max_length=250, blank=True)
    gallery = StreamField([("image", GalleryImageBlock())], blank=True, verbose_name="Galerie")
    programme = models.ForeignKey(
        "wagtaildocs.Document",
        verbose_name="Programme à télécharger",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    organiser = models.CharField("Organisation", max_length=200, blank=True)
    related_authors = ParentalManyToManyField(
        AuthorPage, verbose_name="Artistes associés", blank=True, related_name="events"
    )
    edition = models.ForeignKey(
        "content.FestivalEditionPage",
        verbose_name="Édition associée",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Catégorie",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    featured = models.BooleanField("Mettre en avant", default=False)

    parent_page_types = ["content.EventIndexPage"]
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("start"),
                FieldPanel("end"),
                FieldPanel("venue"),
                FieldPanel("address_override"),
                FieldPanel("map_url"),
            ],
            heading="Date et lieu",
        ),
        MultiFieldPanel(
            [
                FieldPanel("admission"),
                FieldPanel("booking_url"),
                FieldPanel("organiser"),
                FieldPanel("programme"),
            ],
            heading="Informations pratiques",
        ),
        FieldPanel("featured_image"),
        FieldPanel("image_alt"),
        FieldPanel("gallery"),
        FieldPanel("related_authors"),
        FieldPanel("edition"),
        FieldPanel("category"),
        FieldPanel("featured"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.FilterField("start"),
    ]

    def clean(self):
        super().clean()
        if self.start and self.end and self.end < self.start:
            from django.core.exceptions import ValidationError

            raise ValidationError({"end": _("La fin doit être postérieure au début.")})


class BlogIndexPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["content.BlogPage"]

    def get_context(self, request):
        from django.core.paginator import Paginator

        context = super().get_context(request)
        posts = BlogPage.objects.child_of(self).live().order_by("-publication_date")
        category = request.GET.get("categorie", "")
        if category:
            posts = posts.filter(category__slug=category)
        context["posts"] = Paginator(posts, 9).get_page(request.GET.get("page"))
        context["categories"] = Category.objects.filter(blog_posts__isnull=False).distinct()
        context["selected_category"] = category
        return context


class BlogPage(SeoPage):
    publication_date = models.DateField("Date de publication", default=timezone.localdate)
    contributor = models.ForeignKey(
        Contributor,
        verbose_name="Auteur ou autrice de la chronique",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Catégorie",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )
    introduction = models.TextField("Introduction")
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image principale",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt = models.CharField("Texte alternatif de l’image", max_length=250, blank=True)
    body = StreamField(BaseStreamBlock(), blank=True, verbose_name="Contenu")
    gallery = StreamField([("image", GalleryImageBlock())], blank=True, verbose_name="Galerie")
    writer = models.CharField("Scénariste", max_length=150, blank=True)
    artist = models.CharField("Dessinateur ou dessinatrice", max_length=150, blank=True)
    colorist = models.CharField("Coloriste", max_length=150, blank=True)
    publisher = models.CharField("Maison d’édition", max_length=150, blank=True)
    related_articles = ParentalManyToManyField(
        "self", verbose_name="Chroniques associées", blank=True, symmetrical=False
    )
    featured = models.BooleanField("Mettre en avant", default=False)

    parent_page_types = ["content.BlogIndexPage"]
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("publication_date"),
                FieldPanel("contributor"),
                FieldPanel("category"),
                FieldPanel("featured"),
            ],
            heading="Publication",
        ),
        FieldPanel("introduction"),
        FieldPanel("featured_image"),
        FieldPanel("image_alt"),
        FieldPanel("body"),
        FieldPanel("gallery"),
        MultiFieldPanel(
            [
                FieldPanel("writer"),
                FieldPanel("artist"),
                FieldPanel("colorist"),
                FieldPanel("publisher"),
            ],
            heading="Informations sur l’ouvrage",
        ),
        FieldPanel("related_articles"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.FilterField("publication_date"),
    ]


class FestivalArchiveIndexPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["content.FestivalEditionPage"]

    def get_context(self, request):
        context = super().get_context(request)
        editions = FestivalEditionPage.objects.child_of(self).live().order_by("-year")
        year = request.GET.get("annee", "")
        if year.isdigit():
            editions = editions.filter(year=int(year))
        context.update({"editions": editions, "selected_year": year})
        return context


class FestivalEditionPage(SeoPage):
    year = models.PositiveIntegerField("Année")
    poster = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Affiche",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    dates = models.CharField("Dates", max_length=200, blank=True)
    introduction = models.TextField("Introduction", blank=True)
    retrospective = StreamField(BaseStreamBlock(), blank=True, verbose_name="Rétrospective")
    programme = StreamField([("item", ProgrammeBlock())], blank=True, verbose_name="Programme")
    gallery = StreamField([("image", GalleryImageBlock())], blank=True, verbose_name="Galerie")
    documents = StreamField(
        [("document", BaseStreamBlock.base_blocks["document"])],
        blank=True,
        verbose_name="Documents",
    )

    parent_page_types = ["content.FestivalArchiveIndexPage"]
    content_panels = Page.content_panels + [
        FieldPanel("year"),
        FieldPanel("poster"),
        FieldPanel("dates"),
        FieldPanel("introduction"),
        FieldPanel("retrospective"),
        FieldPanel("programme"),
        FieldPanel("gallery"),
        FieldPanel("documents"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("retrospective"),
        index.FilterField("year"),
    ]


class ContactPage(SeoPage):
    introduction = models.TextField("Introduction", blank=True)
    success_message = models.CharField(
        "Message de confirmation",
        max_length=250,
        default="Merci, votre message a bien été envoyé.",
    )
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("success_message"),
    ]
    max_count = 1

    def serve(self, request):
        from django.shortcuts import render

        form = ContactForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip = forwarded.split(",", 1)[0].strip() or request.META.get("REMOTE_ADDR", "unknown")
            key = f"contact:{ip}"
            if cache.get(key):
                form.add_error(None, "Veuillez patienter avant d’envoyer un autre message.")
            elif form.cleaned_data.get("website"):
                return HttpResponseRedirect(f"{self.url}?envoye=1")
            elif not settings.CONTACT_RECIPIENT:
                form.add_error(None, "L’adresse de réception n’est pas encore configurée.")
            else:
                EmailMessage(
                    f"[Strasbulles] {form.cleaned_data['subject']}",
                    f"Nom : {form.cleaned_data['name']}\n"
                    f"E-mail : {form.cleaned_data['email']}\n\n{form.cleaned_data['message']}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_RECIPIENT],
                    reply_to=[form.cleaned_data["email"]],
                ).send()
                cache.set(key, True, 60)
                return HttpResponseRedirect(f"{self.url}?envoye=1")
        return render(request, self.get_template(request), {"page": self, "form": form})
