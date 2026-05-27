from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.contrib.auth import logout
from account.models import Registers, Upload


# Create your views here
def UploadFunc(request):
    if Registers.objects.filter(email=request.user.email).exists() or Upload.objects.filter(email=request.user.email).exists():
        redirect_url = request.session.pop('login_next_url', '')
        if redirect_url:
            return HttpResponseRedirect(f'/{redirect_url}/')
        else:
            return HttpResponseRedirect('/')
    else:
        user = User.objects.get(pk=request.user.id)
        logout(request)
        request.session['google_sign_up'] = True
        request.session['username'] = user.username
        request.session['fname'] = user.first_name
        request.session['lname'] = user.last_name
        request.session['gender'] = ""
        request.session['email'] = user.email
        return HttpResponseRedirect('/account/upload/')


class Campus(View):
    def get(self, request):
        return HttpResponseRedirect("https://chat.whatsapp.com/CRssRaj9zUPCpNJ7FebLWN")


class Sitemap(View):
    def get(self, request):
        return render(request, 'sitemap.xml', content_type='text/xml')

class Robots(View):
    def get(self, request):
        return render(request, 'robots.txt', content_type='text/plain')

class LLMFILE(View):
    def get(self, request):
        return render(request, 'llms.txt', content_type='text/plain')

class Ads(View):
    def get(self, request):
        return render(request, 'ads.txt', content_type='text/plain')

class ssl(View):
    def get(self, request):
        return render(request, '3E4612F07E9BF0ED441A9D77F76CCF06.txt', content_type='text/plain')


class LoginNext(View):
    def get(self, request, nexturl):
        if nexturl == 'null':
            request.session.pop('login_next_url', None)
        else:
            request.session['login_next_url'] = nexturl
        return JsonResponse({"message" : "Done"})