from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import requests
from django.shortcuts import redirect, render
from django.views.generic.base import View


def error_404_view(request, exception):
    return render(request, "errors/not_found.html")


def account_v2_redirect(request, path=""):
    query = request.META.get("QUERY_STRING", "")
    url = f"/account/{path}"
    if query:
        url = f"{url}?{query}"
    return redirect(url, permanent=True)


def UploadFunc(request):
    """Legacy Google OAuth callback — send users to the current login flow."""
    return HttpResponseRedirect("/account/identify")


def check_ip(request):
    ip = requests.get("https://api.ipify.org").text
    return HttpResponse(ip)


class Campus(View):
    def get(self, request):
        return HttpResponseRedirect("https://chat.whatsapp.com/CRssRaj9zUPCpNJ7FebLWN")


class Sitemap(View):
    def get(self, request):
        return render(request, "site/sitemap.xml", content_type="text/xml")

class Robots(View):
    def get(self, request):
        return render(request, "site/robots.txt", content_type="text/plain")

class LLMFILE(View):
    def get(self, request):
        return render(request, "site/llms.txt", content_type="text/plain")

class Ads(View):
    def get(self, request):
        return render(request, "site/ads.txt", content_type="text/plain")

class ssl(View):
    def get(self, request):
        return render(request, "site/ssl_certificate.txt", content_type="text/plain")


class LoginNext(View):
    def get(self, request, nexturl):
        if nexturl == 'null':
            request.session.pop('login_next_url', None)
        else:
            request.session['login_next_url'] = nexturl
        return JsonResponse({"message" : "Done"})