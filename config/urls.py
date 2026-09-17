from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from content import views

handler404 = "content.views.error_404"
handler500 = "content.views.error_500"

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("recherche/", views.search, name="search"),
    path("sitemap.xml", sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("health/", views.health, name="health"),
    path("lassociation/", RedirectView.as_view(url="/association/", permanent=True)),
    path(
        "adherer-soutenir/",
        RedirectView.as_view(url="/association/adherer-soutenir/", permanent=True),
    ),
    path(
        "evenements-a-venir/",
        RedirectView.as_view(url="/evenements/", permanent=True),
    ),
    path("annonces/", RedirectView.as_view(url="/rencontres/", permanent=True)),
    path(
        "mentions-legles/",
        RedirectView.as_view(url="/mentions-legales/", permanent=True),
    ),
    path(
        "politique-de-confidentialites/",
        RedirectView.as_view(url="/politique-de-confidentialite/", permanent=True),
    ),
    path("", include("wagtail.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
