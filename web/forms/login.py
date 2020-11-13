from django import forms
from django.forms import widgets
from django.forms import fields

class LoginForm(forms.Form):
    username = fields.CharField(
        min_length=3,
        error_messages={"required": "用户名不能为空", "min_length": "长度不能小于3"},
        widget=widgets.TextInput(attrs={"class":"form-control", 'id':"username", 'placeholder':"请输入用户名", 'onchange': "change(this);"})
    )

    password = fields.CharField(
        min_length=3,
        error_messages={"required": "密码不能为空", "min_length": "长度不能小于3"},
        widget=widgets.PasswordInput(attrs={"class":"form-control", 'id':"password", 'placeholder':"请输入密码"})
    )