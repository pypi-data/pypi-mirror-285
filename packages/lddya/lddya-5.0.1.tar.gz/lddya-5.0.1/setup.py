#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: lidongdong
# Mail: 927052521@qq.com
# Created Time: 2022.10.21  19.50
############################################

from setuptools import setup, find_packages

setup(
    name = "lddya",
    version = "5.0.1",
    keywords = {"pip", "license","licensetool", "tool", "gm"},
    description = "将Algorithm中的几个算法进行分类，暂分两类：Heuristic与Traditional。这将为后续强化学习的添加提供支持。",
    long_description = "具体功能，请自行挖掘。",
    license = "MIT Licence",

    url = "https://github.com/not_define/please_wait",
    author = "lidongdong",
    author_email = "927052521@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['numpy','matplotlib','pygame','pandas']
)
