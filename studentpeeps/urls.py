"""studentpeeps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path 
from django.conf.urls.static import static
from django.views.static import serve
from . import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('event/', views.Campus.as_view(), name="Event"),
    path("", include("main.urls")),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('google-upload/', views.UploadFunc, name="google-upload"),
    path('sitemap.xml/', views.Sitemap.as_view(), name="Sitemap"),
    path('loginnext/<str:nexturl>/', views.LoginNext.as_view(), name="LoginNext"),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root' : settings.MEDIA_ROOT})
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'main.views.error_404_view'
handler404 = 'account.views.error_404_view'
