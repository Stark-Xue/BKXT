from django.shortcuts import render, HttpResponse, redirect
from django import forms
from django.forms import widgets
from django.forms import fields
from django.urls import reverse
from io import BytesIO
import json, datetime, re
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from ..forms.register import RegisterForm
from ..forms.login import LoginForm

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


def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG')  # 图片信息写入内存
    request.session['checkCode'] = code
    return HttpResponse(stream.getvalue())  # 从内存中读取图片信息


@csrf_exempt
@xframe_options_exempt
def img_upload(request):
    """
    加载验证码图片
    :param request:
    :return:
    """

    avatarImg = request.FILES.get('avatarImg')
    print(avatarImg)
    import os
    img_path = os.path.join('static/imgs', avatarImg.name)
    print(img_path)
    with open(img_path, 'wb') as f:
        for item in avatarImg.chunks():
            f.write(item)

    ret = {'status': True, 'data': img_path}
    import json
    return HttpResponse(json.dumps(ret))


def login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == "GET":
        path_info = request.GET.get("path_info")
        print(path_info)
        obj = LoginForm()
        return render(request, "login.html", {"obj": obj, "path_info": path_info})
    if request.method == "POST":
        # 获取用户的所有信息
        # 每条数据的校验
        # 成功： 显示所有的信息
        # 失败： 显示错误信息
        obj = LoginForm(request.POST)
        r1 = obj.is_valid()
        rmb = request.POST.get("rmb")
        path_info = request.POST.get("path_info", "/")
        print(rmb)
        if r1:
            print(obj.cleaned_data)
            user_obj = models.UserInfo.objects.filter(**obj.cleaned_data)
            if user_obj:
                check_code = request.POST.get("check_code")
                if check_code.upper() != request.session["checkCode"].upper():
                    return render(request, "login.html", {"obj": obj, "check_err": "验证码错误"})
                # models.UserInf.objects.create(**obj.cleaned_data)
                if request.POST.get("rmb"):
                    print("rmb_rmb")
                    request.session['username'] = obj.cleaned_data['username']
                    request.session['password'] = obj.cleaned_data["password"]
                    request.session.set_expiry(1209600) # Session的cookie失效日期（2周）
                else:
                    request.session['username'] = obj.cleaned_data['username']
                    request.session['password'] = obj.cleaned_data["password"]
                    request.session.set_expiry(0) # 用户关闭浏览器session就会失效
                print(path_info, type(path_info))
                if path_info == "None":
                    return redirect("/")
                return redirect(path_info)
            else:
                return render(request, "login.html", {"obj": obj, "user_err": "用户名或密码错误", "path_info": path_info})
        else:
            # print(obj.errors["user"][0])
            return render(request, "login.html", {"obj": obj, "path_info": path_info})


def logout(request):
    request.session['username'] = None
    return redirect("/")


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.method == "GET":
        path_info = request.GET.get("path_info")
        obj = RegisterForm()
        return render(request, "register.html", {"obj": obj, "path_info": path_info})
    elif request.method == "POST":
        obj = RegisterForm(request.POST)
        r1 = obj.is_valid()
        path_info = request.POST.get("path_info")
        confirm_password = request.POST.get("confirm_password")
        check_code = request.POST.get("check_code")
        avatar = request.POST.get("img_file")
        if r1:
            if confirm_password != obj.cleaned_data["password"]:
                return render(request, "register.html", {"obj": obj, "error_msg_pwd": "两次密码不同", "path_info": path_info})
            if check_code.upper() != request.session["checkCode"].upper():
                return render(request, "register.html", {"obj": obj, "error_msg_check": "验证码错误", "path_info": path_info})
            with transaction.atomic():
                user_obj = models.UserInfo.objects.create(
                    username = obj.cleaned_data["username"],
                    password = obj.cleaned_data["password"],
                    nickname = obj.cleaned_data["nickname"],
                    email = obj.cleaned_data["email"],
                    avatar = avatar,
                )
                models.Blog.objects.create(
                    title = obj.cleaned_data["title"],
                    site = obj.cleaned_data["site"],
                    theme = obj.cleaned_data["theme"],
                    user = user_obj
                )
                return redirect(path_info)
            return render(request, "register.html", {"obj": obj, "path_info": path_info})
        else:
            # print(obj.errors["user"][0])
            return render(request, "register.html", {"obj": obj, "path_info": path_info})



        """
        ret = {'status': True, 'username': "", 'nickname': "", 'email': '', 'password': '', 'confirm_password': '', 'check_code': ''}
        img_file = request.POST.get("img_file")
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        check_code = request.POST.get("check_code")
        print(img_file, type(img_file))
        users = models.UserInfo.objects.all()
        if len(username) == 0:
            ret["status"] = False
            ret["username"] = "用户名不能为空"
        elif len(username) < 3:
            ret["status"] = False
            ret["username"] = "长度不能小于3"
        else:
            for user in users:
                if user.username == username:
                    ret["status"] = False
                    ret["username"] = "用户名已存在"

        if len(nickname) == 0:
            ret["status"] = False
            ret["nickname"] = "昵称不能为空"
        elif len(nickname) < 3:
            ret["status"] = False
            ret["nickname"] = "长度不能小于3"

        if len(email) == 0:
            ret["status"] = False
            ret["email"] = "邮箱地址不能为空"
        elif not re.search('([\w\.-]+)@([\w\.-]+)(\.[\w\.]+)', email):
            ret["status"] = False
            ret["email"] = "邮箱格式错误"
        else:
            for user in users:
                if user.email == email:
                    ret["status"] = False
                    ret["email"] = "邮箱已被使用"

        if len(password) == 0:
            ret["status"] = False
            ret["password"] = "密码不能为空"
        elif password != confirm_password:
            ret["status"] = False
            ret["confirm_password"] = "两次密码不相同"

        if len(check_code) == 0:
            ret["status"] = False
            ret["check_code"] = "验证码不能为空"
        elif check_code.upper() != request.session["checkCode"].upper():
            ret["status"] = False
            ret["check_code"] = "验证码错误"

        if ret['status']:
            models.UserInfo.objects.create(
                username=username,
                password=password,
                nickname=nickname,
                email=email,
                avatar=img_file,
                create_time=datetime.datetime.now()
            )
        return HttpResponse(json.dumps(ret))
        """

'''
@csrf_exempt
def register_blog(request):

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        title = request.POST.get("title")
        site = request.POST.get("site")
        theme = request.POST.get("theme")
        models.Blog.objects.create(title=title, site=site, theme=theme, user_id=user_id)
        return redirect("/login/")


@csrf_exempt
def register_sub(request):
    username = request.POST.get("username", "Seth")
    path_info = request.POST.get("path_info")
    user = models.UserInfo.objects.filter(username=username).first()
    return render(request, "register_blog.html", {"user_id": user.nid, "path_info": path_info})
'''