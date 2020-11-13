from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def filter_all(arg_dic, k):
    """
    {% if arg_dic.article_type == 0 %}
        <a class="active" href="/backend/articles-0-{{ arg_dic.category_id }}/">全部</a>
    {% else %}
        <a href="/backend/articles-0-{{ arg_dic.category_id }}/">全部</a>
    {% endif %}

    {% if arg_dic.category_id == 0 %}
        <a class="active" href="/backend/articles-{{ arg_dic.article_type }}-0/">全部</a>
    {% else %}
        <a href="/backend/articles-{{ arg_dic.article_type }}-0/">全部</a>
    {% endif %}
    :return:
    """

    ret = ""
    if k == "article_type":
        n1 = arg_dic["article_type"]
        n2 = arg_dic["category_id"]
        if n1 == 0:
            ret = '<a class="active" href="/backend/articles-0-%s/">全部</a>' % n2
        else:
            ret = '<a href="/backend/articles-0-%s/">全部</a>' % n2
    elif k == "category_id":
        n1 = arg_dic["category_id"]
        n2 = arg_dic["article_type"]
        if n1 == 0:
            ret = '<a class="active" href="/backend/articles-%s-0/">全部</a>' % n2
        else:
            ret = '<a href="/backend/articles-%s-0/">全部</a>' % n2

    return mark_safe(ret)


@register.simple_tag
def filter_combine(arg_dic, obj_list, k):
    """
    {% for row in article_type %}
        {% if row.0 == arg_dic.article_type %}
            <a class="active" href="/backend/articles-{{ row.0 }}-{{ arg_dic.category_id }}/">{{ row.1 }}</a>
        {% else %}
            <a href="/backend/articles-{{ row.0 }}-{{ arg_dic.category_id }}/">{{ row.1 }}</a>
        {% endif %}
    {% endfor %}

    {% for row in category %}
        {% if row.nid == arg_dic.category_id %}
            <a class="active" href="/backend/articles-{{ arg_dic.article_type }}-{{ row.nid }}/">{{ row.title }}</a>
        {% else %}
            <a href="/backend/articles-{{ arg_dic.article_type }}-{{ row.nid }}/">{{ row.title }}</a>
        {% endif %}
    {% endfor %}
    :return:
    """

    list = []
    if k == "article_type":
        for row in obj_list:
            if row[0] == arg_dic["article_type"]:
                ret = '<a class="active" href="/backend/articles-%s-%s/">%s</a>' % (row[0], arg_dic["category_id"], row[1])
            else:
                ret = '<a href="/backend/articles-%s-%s/">%s</a>' % (row[0], arg_dic["category_id"], row[1])
            list.append(ret)
    elif k == "category_id":
        for row in obj_list:
            if row.nid == arg_dic["category_id"]:
                ret = '<a class="active" href="/backend/articles-%s-%s/">%s</a>' % (arg_dic["article_type"], row.nid, row.title)
            else:
                ret = '<a href="/backend/articles-%s-%s/">%s</a>' % (arg_dic["article_type"], row.nid, row.title)
            list.append(ret)

    return mark_safe("".join(list))