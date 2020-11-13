from bs4 import BeautifulSoup


class XSSFilter(object):
    __instance = None


    def __init__(self):
        """
        白名单
        """
        self.valid_tags = {
            "font": ['color', 'size', 'face', 'style'],
            'b': [],
            'div': [],
            "span": [],
            "table": [
                'border', 'cellspacing', 'cellpadding'
            ],
            'th': [
                'colspan', 'rowspan'
            ],
            'td': [
                'colspan', 'rowspan'
            ],
            "a": ['href', 'target', 'name'],
            "img": ['src', 'alt', 'title'],
            'p': [
                'align'
            ],
            "pre": ['class'],
            "hr": ['class'],
            'strong': []
        }


    def __new__(cls, *args, **kwargs):
        """
        单例模式
        :param args:
        :param kwargs:
        :return:
        """
        if not cls.__instance:
            obj = object.__new__(cls, *args, **kwargs)
            cls.__instance = obj
        return cls.__instance

    def process(self, content):
        soup = BeautifulSoup(content, "html.parser")
        # 遍历所有HTML标签
        for tag in soup.find_all(recursive=True):
            # 判断标签是否在白名单里
            if tag.name not in self.valid_tags:
                tag.hidden = True
                if tag.name not in ['html', 'body']:
                    tag.hidden = True
                    tag.clear()
                continue
            # 当前标签的所有属性白名单
            attr_rules = self.valid_tags[tag.name]
            keys = list(tag.attrs.keys())
            for key in keys:
                if key not in attr_rules:
                    del tag[key]

        return soup.decode()