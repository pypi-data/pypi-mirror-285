"""
Created on 2024/7/19 上午10:12
@author:刘飞
@description:
"""
from django.utils.translation import gettext_lazy as _

file_menu_list = [
    {
        'name': _('文件模块'),
        'models': [
            {
                'name': _('文档库'),
                'url': 'yc_django_files/repositories/'
            },
            {
                'name': _('文件'),
                'url': 'yc_django_files/file/'
            }
        ]
    }
]
