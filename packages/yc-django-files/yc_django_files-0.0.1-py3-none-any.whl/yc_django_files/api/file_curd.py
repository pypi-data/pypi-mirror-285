"""
Created on 2024/7/18 下午5:49
@author:刘飞
@description:
"""
from yc_django_utils.viewset import CustomModelViewSet
from ..serializers import FileSerializer
from ..models import File


class FileViewSet(CustomModelViewSet):
    """
    文件管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_fields = ['file_name', ]
    # permission_classes = []
