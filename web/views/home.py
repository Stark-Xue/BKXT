from django.shortcuts import render, HttpResponse, redirect
from django import forms
from django.forms import widgets
from django.forms import fields
from django.urls import reverse
from io import BytesIO
import json, datetime, re
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from utils.check_code import create_validate_code
from repository import models
from utils.pagination import Page

from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin, xframe_options_deny
'''
xframe_options_exempt: 页面地址允许frame加载
xframe_options_sameorigin: 页面地址只能被同源域名页面嵌入到frame中
xframe_options_deny: 页面地址不能被嵌入到任何frame中
'''

# Create your views here.


def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    :param request:
    :return:
    """

    # models.ArticleDetail.objects.create(content="乒乒乓乓乒乒乓乓乒乒乓乓乒乒乓乓乒乒乓乓乒乒乓乓乒乒乓乓乒乒乓乓品牌", article_id="1")

    # models.Article.objects.create(title="test5", summary="testtesttesttesttesttesttesttesttesttesttesttes", blog_id=2, category_id=1, article_type=2)

    if kwargs:
        article_type = int(kwargs["article_type"])
        base_url = reverse("index", kwargs=kwargs)
    else:
        article_type = None
        base_url = "/"

    data_count = models.Article.objects.filter(**kwargs).count()
    page_obj = Page(request.GET.get("p"), data_count)

    article_type_list = models.Article.type_choices
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    comment_max = models.Article.objects.filter(**kwargs).order_by('-comment_count')[0:5]
    new_article = models.Article.objects.filter(**kwargs).order_by('-create_time')[0:5]
    page_str = page_obj.page_str(base_url)
    return render(
        request,
        "index.html",
        {
            "article_type_list": article_type_list,
            "article_list": article_list,
            "article_type_id": article_type,
            "page_str": page_str,
            "comment_max": comment_max,
            'new_article': new_article
        }
    )




def article_detail(request, *args, **kwargs):
    """
    文章细节，展示博文内容
    :param request:
    :return:
    """

    if request.method == "GET":
        comment_count = 0
        article_type_list = models.Article.type_choices
        print("hahaha", request.session.get('username'))
        user_obj = models.UserInfo.objects.filter(username=request.session.get('username')).first()
        blog = models.Blog.objects.filter(site=kwargs["site"]).first()
        fans_rel = models.UserFans.objects.filter(user=blog.user, follower=user_obj).first()
        if fans_rel or user_obj == blog.user:
            focus = True
        else:
            focus = False
        print(focus)
        obj = models.ArticleDetail.objects.filter(article_id=kwargs["article_id"]).first()
        article_obj = obj.article
        read_count = article_obj.read_count
        read_count += 1
        models.Article.objects.filter(nid=article_obj.nid).update(read_count=read_count)
        # print(type(obj.article.blog.nid), obj.article.blog.nid)
        new_article = models.Article.objects.filter(blog=obj.article.blog).order_by('-create_time')[0:5]
        article_count = models.Article.objects.filter(blog=obj.article.blog).count()
        fans_count = models.UserFans.objects.filter(user=obj.article.blog.user).count()
        up_count = 0
        for row in models.Article.objects.filter(blog=obj.article.blog):
            comment_count += models.Comment.objects.filter(article=row).count()
            up_count += row.up_count
        comment_max = models.Article.objects.filter(blog=obj.article.blog).order_by('-comment_count')[0:5]
        comment = models.Comment.objects.filter(article=obj.article).order_by("-create_time")
        category_obj = models.Category.objects.filter(blog=obj.article.blog).all()
        tags = models.Tag.objects.filter(blog=obj.article.blog).all()
        tags_count_dic = {}
        category_count_dic = {}
        for tag in tags:
            tags_count_dic[tag.nid] = [tag.title, models.Article2Tag.objects.filter(tag=tag).count()]
        for category in category_obj:
            category_count_dic[category.nid] = [category.title, models.Article.objects.filter(category=category).count()]
        return render(
            request,
            "article_detail.html",
            {
                "article_type_list": article_type_list,
                "obj": obj,
                "article_obj": article_obj,
                "article_count": article_count,
                "fans_count": fans_count,
                "up_count": up_count,
                "comment_count": comment_count,
                "new_article": new_article,
                "comment_max": comment_max,
                "user_obj": user_obj,
                "comment": comment,
                "category_obj": category_obj,
                "category_count_dic": category_count_dic,
                "tags_count_dic": tags_count_dic,
                "blog": blog,
                "focus": focus,
                "read_count": read_count,
            }
        )


@csrf_exempt
def talk(request):
    """
    博文讨论内容
    :param request:
    :return:
    """

    if request.method == "POST":
        print("sasa", request.POST.get("user_id"), request.POST.get("article_id"), request.POST.get("words"))
        ret = {"status": True, "error": None}
        words = request.POST.get("words")
        if len(words) and request.session.get("username"):
            with transaction.atomic():
                if words.startswith("@"):
                    print("@@@@", request.POST.get("words_id"))
                    str = re.search("^@\w+:", words).group()
                    print(str, type(str), words, type(words))
                    words = words[len(str):]
                    to_user = str[1:len(str)-1]
                    print("to_user", to_user)
                    print(words)
                    models.Comment.objects.create(
                        content=words,
                        article_id=request.POST.get("article_id"),
                        user_id=request.POST.get("user_id"),
                        reply_id=request.POST.get("words_id"),
                        to_user=to_user,
                    )
                else:
                    models.Comment.objects.create(
                        content=request.POST.get("words"),
                        article_id=request.POST.get("article_id"),
                        user_id=request.POST.get("user_id")
                    )
                article_obj = models.Article.objects.filter(nid=request.POST.get("article_id")).first()
                comment_count = article_obj.comment_count
                comment_count += 1
                models.Article.objects.filter(nid=request.POST.get("article_id")).update(comment_count=comment_count)

        else:
            if not request.session.get("username"):
                ret["error"] = 1
                ret["status"] = False
                print("please login")
                print(ret["error"], type(ret["error"]))
            elif len(words) == 0:
                ret["error"] = 0
                ret["status"] = False
                print("input words")
                print(ret["error"], type(ret["error"]))

        return HttpResponse(json.dumps(ret))


@csrf_exempt
def up(request):
    """
    点赞
    :param request:
    :return:
    """

    if request.method == "POST":
        ret = {"status": False, "data": None}
        if request.session.get('username'):
            #ret = {"status": False, "data": None}
            user = models.UserInfo.objects.filter(username=request.session.get('username')).first()
            with transaction.atomic():
                obj = models.UpDown.objects.filter(article_id=request.POST.get("article_id"), user=user).first()
                article_obj = models.Article.objects.filter(nid=request.POST.get("article_id")).first()
                down_count = article_obj.down_count
                up_count = article_obj.up_count
                if obj:
                    if obj.up == False:
                        up_count += 1
                        down_count -= 1
                        models.UpDown.objects.filter(article_id=request.POST.get("article_id"), user=user).update(up=True)
                else:
                    up_count += 1
                    models.UpDown.objects.create(article_id=request.POST.get("article_id"), user=user, up=True)

                models.Article.objects.filter(nid=request.POST.get("article_id")).update(up_count=up_count, down_count=down_count)
                ret["status"] = True
                ret["data"] = [up_count, down_count]
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse(json.dumps(ret))


@csrf_exempt
def down(request):
    """
    踩你
    :param request:
    :return:
    """

    if request.method == "POST":
        ret = {"status": False, "data": None}
        if request.session.get('username'):

            user = models.UserInfo.objects.filter(username=request.session.get('username')).first()
            with transaction.atomic():
                obj = models.UpDown.objects.filter(article_id=request.POST.get("article_id"), user=user).first()
                article_obj = models.Article.objects.filter(nid=request.POST.get("article_id")).first()
                down_count = article_obj.down_count
                up_count = article_obj.up_count
                if obj:
                    if obj.up == True:
                        up_count -= 1
                        down_count += 1
                        models.UpDown.objects.filter(article_id=request.POST.get("article_id"), user=user).update(up=False)
                else:
                    down_count += 1
                    models.UpDown.objects.create(article_id=request.POST.get("article_id"), user=user, up=False)

                models.Article.objects.filter(nid=request.POST.get("article_id")).update(up_count=up_count, down_count=down_count)
                ret["status"] = True
                ret["data"] = [up_count, down_count]
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse(json.dumps(ret))


def filter(request, site, condition, val):
    """
    分类显示
    :param request:
    :param site:
    :param condition:
    :param val:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related("user").first()
    if not blog:
        return redirect("/")
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    user_obj = models.UserInfo.objects.filter(username=request.session.get('username')).first()
    fans_rel = models.UserFans.objects.filter(user=blog.user, follower=user_obj).first()
    if fans_rel or user_obj == blog.user:
        focus = True
    else:
        focus = False
    template_name = "home_tag_list.html"
    if condition == "tag":
        article_list = models.Article.objects.filter(blog=blog, tags=val).all()
    elif condition == "category":
        template_name = "home_category_list.html"
        article_list = models.Article.objects.filter(blog=blog, category_id=val).all()
    article_count = models.Article.objects.filter(blog=blog).count()
    fans_count = models.UserFans.objects.filter(user=blog.user).count()
    #up_count = models.UpDown.objects.filter(article=obj.article, user=obj.article.blog.user, up=True).count()
    article_type_list = models.Article.type_choices
    up_count = 0
    comment_count = 0
    for row in models.Article.objects.filter(blog=blog):
        comment_count += models.Comment.objects.filter(article=row).count()
        up_count += row.up_count
    new_article = models.Article.objects.filter(blog=blog).order_by('-create_time')[0:5]
    comment_max = models.Article.objects.filter(blog=blog).order_by('-comment_count')[0:5]
    category_obj = models.Category.objects.filter(blog=blog).all()
    tags = models.Tag.objects.filter(blog=blog).all()
    tags_count_dic = {}
    category_count_dic = {}
    for tag in tags:
        tags_count_dic[tag.nid] = [tag.title, models.Article2Tag.objects.filter(tag=tag).count()]
    for category in category_obj:
        category_count_dic[category.nid] = [category.title, models.Article.objects.filter(category=category).count()]

    return render(
        request,
        template_name,
        {
            "blog": blog,
            "tag_list": tag_list,
            "category_list": category_list,
            "article_list": article_list,
            "article_count": article_count,
            "fans_count": fans_count,
            "article_type_list": article_type_list,
            "comment_count": comment_count,
            "up_count": up_count,
            "new_article": new_article,
            "comment_max": comment_max,
            "category_count_dic": category_count_dic,
            "tags_count_dic": tags_count_dic,
            "focus": focus,
        }
    )

@csrf_exempt
def focus(request):
    if request.method == "POST":
        print("dayin", request.POST.get("path_info"))
        path_info = request.POST.get("path_info")
        user_id = request.POST.get("user_id")
        print(user_id)
        follower = models.UserInfo.objects.filter(username=request.session["username"]).first()
        models.UserFans.objects.create(user_id=user_id, follower=follower)
        return redirect(path_info)