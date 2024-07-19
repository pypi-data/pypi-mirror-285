#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='url2',
    version='1.2.0',
    author='zkung',
    author_email='du163455@gmail.com',
    url='https://pypi.org/project/url2',
    description='爬虫系列工具集',
    # 需要打包的目录，只有这些目录才能 from import
    packages=find_packages(),
    # 安装此包时需要同时安装的依赖包
    install_requires=[],
)
