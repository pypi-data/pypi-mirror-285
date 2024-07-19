# -*- coding: utf-8 -*-
# -*- author: Jiangtao -*-

"""setup file"""


from setuptools import setup, find_packages
from os import path as os_path
from codecs import open

this_directory = os_path.abspath(os_path.dirname(__file__))


# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


# 获取依赖
def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


__author__ = 'jiangtao'
__date__ = '2018/09/18'


setup(
    name='do-utils',                                             # 名称
    version='0.0.4.2',                                           # 版本号
    author='jiangtao',                                           # 作者
    author_email='jiangtao.work@gmail.com',                      # 邮箱
    description='Utils for tornado api cache, function timer.',  # 简单描述, 显示在PyPI上
    long_description=read_file('README.md'),                     # 详细描述, 读取的Readme文档内容
    long_description_content_type="text/markdown",               # 指定包文档格式为markdown
    url='https://github.com/hustjiangtao/do_utils',              # 包含包的项目地址
    packages=find_packages(),                                    # 包列表
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
    license='http://www.apache.org/licenses/LICENSE-2.0',        # 授权方式
    keywords=[
        'utils',
        'do_utils',
        'cache',
        'time',
        'do_cache',
        'do_time',
    ],                                                           # 关键字
    install_requires=[
        'ujson==1.35',
        'xlwt>=1.3.0,<=2.0.0',
        'openpyxl>=2.6.2',
    ],                                                           # 指定需要安装的依赖
    include_package_data=True,
    zip_safe=True,
    python_requires='>=2.7.14',                                  # python环境
)
