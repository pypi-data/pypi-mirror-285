"""
Created on 2024/7/18 下午4:50
@author:刘飞
@description:
"""
import os

"""上传文件格式限制"""
FILE_UPLOAD_FORMAT = ['pdf', 'jpeg', 'jpg', 'png', 'txt']


def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return os.path.join("files", h[:1], h[1:2], h + ext.lower())
