from django.http import HttpResponse


def robots_txt(request):
    content = """User-agent: *
Disallow: /admin/
Disallow: /accounts/
Disallow: /dashboard/
Disallow: /profile/
Disallow: /contests/
"""
    return HttpResponse(content, content_type="text/plain")