"""BKXT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path

from web.views import home, account

from web import urls

urlpatterns = [
    # path('admin/', admin.site.urls),

    re_path('register/$',  account.register),
    #path('register_sub',  account.register_sub),
    path('check_code.html', account.check_code),
    #path('register_blog', account.register_blog),
    re_path("login/$", account.login),
    re_path("logout/$", account.logout),
    path('img_upload', account.img_upload),

    path('', home.index),
    re_path("all/(?P<article_type>\d+)", home.index, name="index"),
    re_path("(?P<site>\w+)/article-(?P<article_id>\d+)", home.article_detail),
    path("talk/", home.talk),
    re_path('(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+)', home.filter),

    path("up/", home.up),
    path("down/", home.down),

    path("focus/", home.focus),
]
