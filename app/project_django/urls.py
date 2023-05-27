"""hello_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from upload.views import image_upload


urlpatterns = [
    re_path(r'^knowledge/static/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
    path("upload/", image_upload, name="upload"),
    path("auth/", include('authentication.urls')),
    path("data/", include('data.urls')),
    path("knowledge/", include('knowledge.urls')),
]

print(bool(settings.DEBUG))
if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)