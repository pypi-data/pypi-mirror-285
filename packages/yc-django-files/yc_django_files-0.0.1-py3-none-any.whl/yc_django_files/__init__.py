"""
Created on 2024-07-18
@author:LiuFei
@description:文件模块【每次发布须修改版本号】
常用命令
# 导出依赖库
pip list --format=freeze > requirements.txt

# 安装依赖环境
pip install -r requirements.txt

# 打包成wheel格式
python setup.py bdist_wheel

# 发布、上传
twine upload --repository-url https://upload.pypi.org/legacy/  dist/*

# 用户安装
pip install yc_django_files

使用
1、settings.py中注册app【yc_django_files】
2、主url中添加路由 【】
3、simpleui_config中引入后台配置
try:
    from yc_django_files.settings import file_menu_list

    menu_list.extend(file_menu_list)
except Exception as e:
    pass


在这个Django模型中，md5sum 字段用于存储文件的 MD5 哈希值。MD5 哈希是一种广泛使用的哈希函数，它产生一个128位（16字节）的哈希值，通常用32位十六进制数表示。
这个哈希值用于确保文件的完整性，也就是说可以通过比较文件的 MD5 值来检测文件是否在传输或存储过程中被篡改或损坏。

在 FileList 模型的 save 方法中，如果发现 md5sum 字段是空的（即可能是一个新文件或者未曾计算过 MD5），
它会计算文件的 MD5 哈希值。这是通过读取文件的每一个块（chunk），并用 hashlib.md5() 函数更新哈希值来完成的。最后，得到的哈希值（MD5）被存储在 md5sum 字段中。

这样，每个文件在数据库中都有一个对应的 MD5 哈希值，可以在之后用于验证文件的完整性或者检测重复的文件。
在一些应用场景中，比如文件上传服务，通过对比MD5值可以快速检查上传的文件是否已经存在，从而避免存储重复的文件，节省存储空间并提高效率。
"""
