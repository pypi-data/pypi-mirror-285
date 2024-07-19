import hashlib

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from yc_django_utils.models import BaseModel
from simple_history.models import HistoricalRecords
from .utils import media_file_name

table_prefix = settings.TABLE_PREFIX


class File(BaseModel):
    object_id = models.PositiveIntegerField(verbose_name=_('对象ID'), null=True, blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('对象类型'), on_delete=models.CASCADE, null=True,
                                     blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.FileField(verbose_name=_('文件'), upload_to=media_file_name)
    file_url = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("云文件地址"))
    file_name = models.CharField(verbose_name=_('文件名'), max_length=255, null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name=_('文件大小'), null=True, blank=True, default=0)
    engine = models.CharField(max_length=255, default='local', blank=True, verbose_name="引擎", help_text="引擎")
    mime_type = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Mime类型"))
    md5sum = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("文件md5"))
    history = HistoricalRecords(verbose_name=_("历史修改记录"))

    class Meta:
        db_table = table_prefix + 'file'
        verbose_name = _('文件')
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return str(self.file_name)

    def save(self, *args, **kwargs):
        if not self.md5sum:  # file is new
            md5 = hashlib.md5()
            for chunk in self.file.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        if not self.file_size:
            self.file_size = self.file.size
        if not self.file_name:
            self.file_name = self.file.name
        if not self.file_url:
            url = media_file_name(self, self.file_name)
            self.file_url = f'media/{url}'
        if not self.mime_type:
            self.mime_type = self.file.content_type
        super(File, self).save(*args, **kwargs)

    def get_readable_file_size(self):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = self.file_size
        i = 0
        if size:
            while size >= 1024 and i < len(suffixes) - 1:
                size /= 1024.
                i += 1
            return f"{size:.2f} {suffixes[i]}"
        return 0


class Repositories(BaseModel):
    """
    知识库
    """
    name = models.CharField(verbose_name=_('知识库名称'), max_length=255)
    description = models.TextField(verbose_name=_('知识库描述'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否激活'), default=True)
    history = HistoricalRecords(verbose_name=_("历史修改记录"))
    files = GenericRelation(File)

    class Meta:
        db_table = table_prefix + 'repositories'
        verbose_name = _('文档库')
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

    @property
    def file_list(self):
        return list(self.files.all())
