from django.shortcuts import render, redirect, HttpResponse
from repository import models
from django import forms
from django.forms import widgets
from django.forms import fields
from utils.pagination import Page
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
import json
from .forms.article import ArticleForm
from django.db import transaction
from utils.xss import XSSFilter
from .auth.auth import check_login

# Create your views here.


class Tag(forms.Form):
    tag_name = fields.CharField(
        error_messages={"required": "标签名不能为空"},
        )

class Category(forms.Form):
    category_name = fields.CharField(
        error_messages={"required": "分类名不能为空"},
        )


@check_login
def index(request):
    """
    博主个人首页
    :param request:
    :return:
    """

    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    return render(request, "backend_index.html", {"user_obj": user_obj})


@check_login
def tags(request, **kwargs):
    """
    标签管理
    :param request:
    :return:
    """

    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog = models.Blog.objects.filter(user_id=user_obj.nid).first()
    tag2article_dic = {}
    base_url = '/backend/tags/'
    data_count = models.Tag.objects.filter(blog=blog).count()
    page_obj = Page(request.GET.get("p"), data_count, 5, 5)
    page_str = page_obj.page_str(base_url)
    tags = models.Tag.objects.filter(blog=blog).order_by('-nid')[page_obj.start:page_obj.end]
    print(tags)
    #print(tags)
    for row in tags:
        #print(row.nid, row.title, row.blog_id)
        article_count = models.Article2Tag.objects.filter(tag=row).count()
        tag2article_dic[row.title] = [row.nid, article_count]
        print(tag2article_dic[row.title][0])

    return render(request, "backend_tag.html", {"tag2article_dic": tag2article_dic, "user_obj": user_obj, 'page_str': page_str})


@check_login
def tag_add(request, **kwargs):
    """
    增加标签
    :param request:
    :return:
    """

    if request.method == "POST":
        user = models.UserInfo.objects.filter(username=request.session["username"]).first()
        blog=models.Blog.objects.filter(user_id=user.nid).first()

        tag2article_dic = {}
        base_url = '/backend/tags/'
        data_count = models.Tag.objects.filter(blog=blog).count()
        page_obj = Page(request.GET.get("p"), data_count, 5, 5)
        page_str = page_obj.page_str(base_url)
        tags = models.Tag.objects.filter(blog=blog).order_by('-nid')[page_obj.start:page_obj.end]
        # print(tags[0])
        # print(tags)
        for row in tags:
            # print(row.nid, row.title, row.blog_id)
            article_count = models.Article2Tag.objects.filter(tag=row).count()
            tag2article_dic[row.title] = article_count
        # print(tag2article_dic)

        user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()

        obj = Tag(request.POST)
        r1 = obj.is_valid()
        if r1:
            print("tag bug info: ", obj.cleaned_data['tag_name'], blog.nid)
            models.Tag.objects.create(title=obj.cleaned_data["tag_name"], blog=blog)
            return redirect("/backend/tags/")
        else:
            return render(request, "backend_tag.html", {"obj": obj,  "tag2article_dic": tag2article_dic, "user_obj": user_obj, 'page_str': page_str})



@csrf_exempt
@check_login
def tag_del(request):
    if request.method == "POST":
        nid = request.POST.get("nid")
        print(nid)
        models.Tag.objects.filter(nid=nid).delete()
        return HttpResponse("ok")



@csrf_exempt
@check_login
def tag_edit(request):
    if request.method == "POST":
        nid = request.POST.get("nid")
        tag_title = request.POST.get("val")
        print("hahaha", nid, tag_title)
        models.Tag.objects.filter(nid=nid).update(title=tag_title)
        return HttpResponse("ok")


@check_login
def categories(request):
    """
    分类管理
    :param request:
    :return:
    """

    category2article_dic = {}

    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog = models.Blog.objects.filter(user=user_obj).first()
    print(blog)
    base_url = '/backend/categories/'
    data_count = models.Category.objects.filter(blog=blog).count()
    page_obj = Page(request.GET.get("p"), data_count, 5, 5)
    page_str = page_obj.page_str(base_url)
    categories_obj = models.Category.objects.filter(blog=blog).order_by('-nid')[page_obj.start: page_obj.end]
    print(categories_obj)
    for row in categories_obj:
        article_count = models.Article.objects.filter(category=row).count()
        category2article_dic[row.title] = [row.nid, article_count]

    return render(
        request,
        "backend_category.html",
        {
            "user_obj": user_obj,
            "category2article_dic": category2article_dic,
            "page_str": page_str,
        }
    )


@check_login
def category_add(request):
    """
    增加分类
    :param request:
    :return:
    """
    
    if request.method == "POST":
        category2article_dic = {}

        user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
        blog = models.Blog.objects.filter(user=user_obj).first()
        print(blog)
        base_url = '/backend/categories/'
        data_count = models.Category.objects.filter(blog=blog).count()
        page_obj = Page(request.GET.get("p"), data_count, 5, 5)
        page_str = page_obj.page_str(base_url)
        categories_obj = models.Category.objects.filter(blog=blog).order_by('-nid')[page_obj.start: page_obj.end]
        print(categories_obj)
        for row in categories_obj:
            article_count = models.Article.objects.filter(category=row).count()
            category2article_dic[row.title] = [row.nid, article_count]

        obj = Category(request.POST)
        r1 = obj.is_valid()
        if r1:
            print("category create success")
            models.Category.objects.create(title=obj.cleaned_data["category_name"], blog=blog)
            return redirect("/backend/categories/")
        else:
            return render(request, "backend_category.html",
                          {"obj": obj, "category2article_dic": category2article_dic, "user_obj": user_obj, 'page_str': page_str})



@csrf_exempt
@check_login
def category_del(request):
    if request.method == "POST":
        nid = request.POST.get("nid")
        print(nid)
        models.Category.objects.filter(nid=nid).delete()
        return HttpResponse("ok")



@csrf_exempt
@check_login
def category_edit(request):
    if request.method == "POST":
        nid = request.POST.get("nid")
        category_title = request.POST.get("val")
        print("hahaha", nid, category_title)
        models.Category.objects.filter(nid=nid).update(title=category_title)
        return HttpResponse("ok")


@check_login
def baseinfo(request):
    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog_obj = models.Blog.objects.filter(user=user_obj).first()
    return render(request, "backend_baseinfo.html", {"user_obj": user_obj, "blog_obj": blog_obj})


@check_login
@xframe_options_exempt
def upload_avatar(request):
    avatarImg = request.FILES.get('avatarImg')
    print("hahaha", avatarImg)
    import os
    img_path = os.path.join('static/imgs', avatarImg.name)
    print(img_path)
    with open(img_path, 'wb') as f:
        for item in avatarImg.chunks():
            f.write(item)

    models.UserInfo.objects.filter(username=request.session["username"]).update(avatar="/"+img_path)

    ret = {'status': True, 'data': img_path}
    import json
    return HttpResponse(json.dumps(ret))



@csrf_exempt
@check_login
def baseinfo_update(request):
    if request.method == "POST":
        ret = {"status": True, "data": None}
        nickname = request.POST.get("nickname")
        theme = request.POST.get("theme")
        site = request.POST.get("site")
        title = request.POST.get("title")
        print(nickname, theme, site, title)
        models.UserInfo.objects.filter(username=request.session["username"]).update(
            nickname=nickname,
        )
        user = models.UserInfo.objects.filter(username=request.session["username"]).first()
        print("after update:", user.nickname)
        user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
        models.Blog.objects.filter(user=user_obj).update(
            site=site,
            theme=theme,
            title=title,
        )
        return HttpResponse(json.dumps(ret))


@check_login
def articles(request, **kwargs):
    """
    博主个人文章管理
    :param request:
    :return:
    """

    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog_obj = models.Blog.objects.filter(user=user_obj).first()
    article_type = models.Article.type_choices
    category = models.Category.objects.filter(blog=blog_obj).all()
    condition = {}
    condition["blog_id"] = blog_obj.nid
    for k, v in kwargs.items():
        print(k, v)
        kwargs[k] = int(v)
        if v == '0':
            pass
        else:
            condition[k] = v

    article_list = models.Article.objects.filter(**condition).all()

    data_count = models.Article.objects.filter(**condition).count()
    #for row in article_list:
    #    print("article_name: ", row.title)
    base_url = "/backend/articles-" + str(kwargs['article_type']) + "-" + str(kwargs['category_id']) + "/"
    page_obj = Page(request.GET.get("p", 1), data_count, 5, 5)
    page_str = page_obj.page_str(base_url)
    return render(
        request, "backend_article.html",
        {
            "user_obj": user_obj,
            "blog": blog_obj,
            "article_type": article_type,
            "category": category,
            "arg_dic": kwargs,
            "article_list": article_list,
            "data_count": data_count,
            "page_str": page_str,
        }
    )


@check_login
def del_article(request, nid):
    """
    删除文章
    :param request:
    :param nid:
    :return:
    """


    return HttpResponse(nid)


@check_login
def edit_article(request, nid):
    """
    编辑文章
    :param request:
    :param nid:
    :return:
    """
    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog_obj = models.Blog.objects.filter(user=user_obj).first()
    if request.method == "GET":
        article_obj = models.Article.objects.filter(nid=nid, blog=blog_obj).first()
        if not article_obj:
            return render(request, "backend_no_article.html")
        tags = article_obj.tags.values_list('nid') # QuerySet对象，内部元素是元组[(),(),()...]
        if tags:
            tags = list(zip(*tags))[0] #[()]
        init_dic = {
            "nid": article_obj.nid,
            "title": article_obj.title,
            "summary": article_obj.summary,
            "content": article_obj.articledetail.content,
            "category_id": article_obj.category_id,
            "article_type": article_obj.article_type,
            "tags": tags,
        }
        form = ArticleForm(request=request, data=init_dic)
        return render(request, 'backend_article_edit.html', {'form': form, 'nid': nid, "user_obj": user_obj})
    elif request.method == "POST":
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog=blog_obj).first()
            if not obj:
                return render(request, "backend_no_artcile.html")
            with transaction.atomic(): # 事务操作
                content = form.cleaned_data.pop("content")
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop("tags")
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag in tags:
                    tag_id = int(tag)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect("/backend/articles-0-0/")
        else:
            return render(request, "backend_article_edit.html", {"form": form, "nid": nid, "user_obj": user_obj})
    #return render(request, "backend_article_edit.html")


@check_login
def article_add(request):
    """
    新建文章
    :param request:
    :return:
    """

    user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
    blog_obj = models.Blog.objects.filter(user=user_obj).first()
    if request.method == "GET":
        form = ArticleForm(request)
        return render(request, 'backend_article_add.html', {'form': form, "user_obj": user_obj})
    elif request.method == "POST":
        form = ArticleForm(request, data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            with transaction.atomic():
                content = form.cleaned_data.pop("content")
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop("tags")
                form.cleaned_data['blog_id'] = blog_obj.nid
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag in tags:
                    tag_id = int(tag)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect("/backend/articles-0-0/")
        else:
            return render(request, "backend_article_add.html", {"form": form, "user_obj": user_obj})