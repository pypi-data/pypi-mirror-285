from django.contrib import admin
from .models import Repositories
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import File


class FileInline(GenericTabularInline):
    model = File
    fields = ('file', 'file_name', 'file_size')  # , 'content_type', 'object_id'
    extra = 0  # 控制额外展示的空白行数

    def has_change_permission(self, request, obj=None):
        # 禁用修改功能
        return False

    def has_add_permission(self, request, obj=None):
        # 禁用添加功能
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除功能
        return False


@admin.register(Repositories)
class RepositoriesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'is_active', 'create_time', 'update_time', 'file_list')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_per_page = 10
    ordering = ('-id',)
    list_editable = ('is_active',)
    date_hierarchy = 'create_time'

    inlines = [FileInline]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'file_name', 'file', 'content_type', 'content_object', 'create_time', 'get_readable_file_size')
    list_display_links = ('id', 'file_name')
    list_filter = ('content_type',)
    search_fields = ('file_name',)
    list_per_page = 10
    list_max_show_all = 100
    ordering = ('-id',)
    readonly_fields = ('create_time', 'update_time')
    date_hierarchy = 'create_time'
