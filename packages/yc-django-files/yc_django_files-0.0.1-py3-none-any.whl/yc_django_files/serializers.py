"""
Created on 2024/7/18 下午4:40
@author:刘飞
@description:
"""
import hashlib
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from yc_django_utils.serializers import CustomModelSerializer
from .models import File, Repositories


class FileSerializer(CustomModelSerializer):
    # file = serializers.SerializerMethodField(read_only=True)
    #
    # def get_url(self, instance):
    #     # return 'media/' + str(instance.url)
    #     return instance.file_url or f'media/{str(instance.file)}'

    class Meta:
        model = File
        fields = "__all__"

    def create(self, validated_data):
        file_engine = 'local'  # 存储方案，备用
        file_backup = False  # 云存储时，是否在本地有备份，备用
        file = self.initial_data.get('file')
        file_size = file.size
        validated_data['file_name'] = str(file.name)
        validated_data['file_size'] = file_size
        md5 = hashlib.md5()
        for chunk in file.chunks():
            md5.update(chunk)
        validated_data['md5sum'] = md5.hexdigest()
        validated_data['engine'] = file_engine
        validated_data['mime_type'] = file.content_type
        if file_backup:
            validated_data['file'] = file
        if file_engine == 'oss':
            ...
            # from dvadmin_cloud_storage.views.aliyun import ali_oss_upload
            # file_path = ali_oss_upload(file)
            # if file_path:
            #     validated_data['file_url'] = file_path
            # else:
            #     raise ValueError("上传失败")
        elif file_engine == 'cos':
            ...
            # from dvadmin_cloud_storage.views.tencent import tencent_cos_upload
            # file_path = tencent_cos_upload(file)
            # if file_path:
            #     validated_data['file_url'] = file_path
            # else:
            #     raise ValueError("上传失败")
        else:
            validated_data['file'] = file
        # 审计字段
        try:
            request_user = self.request.user
            validated_data['creator'] = request_user
            validated_data['modifier'] = request_user
        except Exception:
            pass
        return super().create(validated_data)


class RepositoriesSerializers(CustomModelSerializer):
    """
    知识库模型序列化器
    """
    content_type = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = Repositories
        fields = "__all__"

    def get_content_type(self, obj):
        content_type = ContentType.objects.get_for_model(Repositories)
        return content_type.id

    def get_files(self, obj):
        data = [{"file_name": i.file_name, "file": i.file.url} for i in obj.file_list]
        return data
