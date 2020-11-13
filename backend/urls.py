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
from backend import views

urlpatterns = [
    # path('admin/', admin.site.urls),

    path("index/", views.index),

    re_path("tags/", views.tags),
    path("tag_add/", views.tag_add),
    path("tag_del/", views.tag_del),
    path("tag_edit/", views.tag_edit),

    path("categories/", views.categories),
    path("category_add/", views.category_add),
    path("category_del/", views.category_del),
    path("category_edit/", views.category_edit),

    path("baseinfo/", views.baseinfo),
    path("upload_avatar/", views.upload_avatar),
    path("baseinfo_update/", views.baseinfo_update),

    re_path("articles-(?P<article_type>\d+)-(?P<category_id>\d+)/", views.articles),
    re_path("article_(?P<nid>\d+)_edit/", views.edit_article),
    re_path("article_(?P<nid>\d+)_del/", views.del_article),
    path("article_add/", views.article_add),
]
