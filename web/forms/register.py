from django import forms
from django.forms import widgets
from django.forms import fields

class RegisterForm(forms.Form):
    username = fields.CharField(
        min_length=3,
        error_messages={"required": "用户名不能为空", "min_length": "长度不能小于3"},
        widget=widgets.TextInput(
            attrs={"class": "form-control", 'id': "username", 'placeholder': "请输入用户名", 'onchange': "change(this);"})
    )

    nickname = fields.CharField(
        min_length=3,
        error_messages={"required": "昵称不能为空", "min_length": "长度不能小于3"},
        widget=widgets.TextInput(
            attrs={"class": "form-control", 'id': "nickname", 'placeholder': "请输入昵称"})
    )

    email = fields.EmailField(
        min_length=6,
        error_messages={"required": "用户名不能为空", "min_length": "长度不能小于6"},
        widget=widgets.TextInput(
            attrs={"class": "form-control", 'id': "email", 'placeholder': "请输入邮箱"})
    )

    password = fields.CharField(
        min_length=3,
        error_messages={"required": "密码不能为空", "min_length": "长度不能小于3"},
        widget=widgets.PasswordInput(attrs={"class": "form-control", 'id': "password", 'placeholder': "请输入密码"})
    )

    title = fields.CharField(
        min_length=3,
        error_messages={"required": "用户名不能为空", "min_length": "长度不能小于3"},
        widget=widgets.TextInput(
            attrs={"class": "form-control", 'id': "title", 'placeholder': "请输入个人博客标题"})
    )

    site = fields.CharField(
        min_length=3,
        error_messages={"required": "用户名不能为空", "min_length": "长度不能小于3"},
        widget=widgets.TextInput(
            attrs={"class": "form-control", 'id': "site", 'placeholder': "请输入个人博客前缀"})
    )

    theme = fields.CharField(
        initial=3,
        widget=widgets.Select(choices=((1,'默认主题'),(2,'雪国风光'),(3,'红色火焰')))
    )