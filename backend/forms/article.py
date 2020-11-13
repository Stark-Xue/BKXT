from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets

from repository import models

class ArticleForm(django_forms.Form):
    title = django_fields.CharField(
        widget=django_widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '文章标题'}),
    )

    summary = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class': 'form-control', 'placeholder': '文章简介', 'rows': '3'})
    )

    content = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class': 'kind-content'})
    )

    article_type = django_fields.IntegerField(
        widget=django_widgets.RadioSelect(choices=models.Article.type_choices)
    )

    category_id = django_fields.ChoiceField(
        choices=[],
        widget=django_widgets.RadioSelect
    )

    tags = django_fields.MultipleChoiceField(
        choices=[],
        widget=django_widgets.CheckboxSelectMultiple
    )

    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        user_obj = models.UserInfo.objects.filter(username=request.session["username"]).first()
        blog_obj = models.Blog.objects.filter(user=user_obj).first()
        self.fields["category_id"].choices = models.Category.objects.filter(blog=blog_obj).values_list('nid', 'title')
        self.fields["tags"].choices = models.Tag.objects.filter(blog=blog_obj).values_list('nid', 'title')