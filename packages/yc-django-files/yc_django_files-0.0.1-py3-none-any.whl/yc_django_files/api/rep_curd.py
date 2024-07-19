"""
Created on 2024/7/19 上午10:01
@author:刘飞
@description: 文档库增删改查
"""
from ..models import Repositories
from yc_django_utils.viewset import CustomModelViewSet
from ..serializers import RepositoriesSerializers


class RepositoriesViewSet(CustomModelViewSet):
    queryset = Repositories.objects.all()
    serializer_class = RepositoriesSerializers
    create_serializer_class = RepositoriesSerializers
    update_serializer_class = RepositoriesSerializers
    filter_fields = ["name", "is_active"]
    search_fields = ["name"]
