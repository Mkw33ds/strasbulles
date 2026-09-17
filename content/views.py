from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from wagtail.models import Page


def search(request):
    query = request.GET.get("q", "").strip()
    results = Page.objects.none()
    if query:
        results = Page.objects.live().public().search(query)
    return render(request, "search/search.html", {"query": query, "results": results})


def robots(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    return HttpResponse(
        f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n", content_type="text/plain"
    )


def health(request):
    return JsonResponse({"status": "ok"})


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)
