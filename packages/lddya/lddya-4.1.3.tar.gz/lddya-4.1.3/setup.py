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
    version = "4.1.3",
    keywords = {"pip", "license","licensetool", "tool", "gm"},
    description = "* 给栅格图的绘制路径功能添加一个label参数；给算法的run函数添加一个show_process参数；给Map添加一个识别路径的功能；给Clock添加一个获取delta数值的方法；给算法的迭代数据添加一个保存为excel的方法；给Map添加一个size属性。",
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
