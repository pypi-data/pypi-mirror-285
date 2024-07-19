"""
Created on 2024/7/18 下午4:40
@author:刘飞
@description:
"""
from rest_framework import routers
from .api.file_curd import FileViewSet
from .api.rep_curd import RepositoriesViewSet

system_url = routers.SimpleRouter()
system_url.register('files', FileViewSet)
system_url.register('repositories', RepositoriesViewSet)

urlpatterns = []
urlpatterns += system_url.urls
