from .models import ContactSettings, MenuLink, SocialLink


def site_context(request):
    site = getattr(request, "site", None)
    settings = ContactSettings.for_site(site) if site else None
    return {
        "contact_settings": settings,
        "social_links": SocialLink.objects.all(),
        "footer_links": MenuLink.objects.filter(location="footer").select_related("page"),
    }
