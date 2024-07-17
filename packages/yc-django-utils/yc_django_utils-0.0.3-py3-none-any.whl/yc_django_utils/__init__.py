"""
Created on 2024/7/10 11:27
@author:刘飞
@description: django 工具集开发 【每次发布须修改版本号】
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
pip install yc_django_utils

# 使用方法【直接导入即可】
from yc_django_utils.xx import xx
"""
