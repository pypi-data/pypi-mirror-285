# -*- coding: utf-8 -*-
"""
# @项目名称 :zsx_pack
# @文件名称 :setup.py
# @作者名称 :zsx
# @日期时间 :2024/4/3 17:06
# @文件介绍 :
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
requirements = [

]
setup(
    # 在 PyPI 上搜索的项目名称。
    name="zsx_pack",
    # 项目版本号，一般由三部分组成：MAJOR, MINOR, MAINTENANCE
    version="1.0.5",
    # 作者信息
    author="zsx",
    author_email="17630583910@163.com",
    # 维护者信息
    maintainer="zsx",
    maintainer_email="17630583910@163.com",
    # 项目许可证
    license="MIT",
    # 项目的简短描述，一般一句话就好，会显示在 PyPI 上名字下端。
    description="自用包，主要是为了logger无法屏蔽第三方包日志而开发的",
    # 对项目的完整描述，使用 long_description。如果此字符串是 rst 格式的，PyPI 会自动渲染成 HTML 显示。
    long_description=long_description,
    # 不设置格式，默认是rst格式文档解读
    long_description_content_type="text/markdown",
    # project home page 通常为 GitHub上 的链接或者 readthedocs 的链接。
    url="https://github.com/ziyueguyi/zsx_pack",
    # 项目相关额外连接，如代码仓库，文档地址等
    project_urls={
        "Bug Tracker": "https://github.com/ziyueguyi/zsx_pack",
    },
    # 提供给pypi的分类依据，参考：https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'colorama>=0.4.6',
    ],
    package_dir={"logger": "logger"},
    python_requires=">=3.6",
    platforms=["Windows", "Linux"],
    packages=find_packages(),

)
