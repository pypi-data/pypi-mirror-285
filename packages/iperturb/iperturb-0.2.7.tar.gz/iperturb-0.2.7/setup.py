# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import io

with io.open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with io.open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="iperturb",  # 包的名字
    version="0.2.7",  # 初始版本
    author="Billy Chen",
    author_email="cyz2022@stu.xjtu.edu.cn",
    description="Atlas-level data integration in multi-condition single-cell genomics",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BillyChen123/iPerturb",  # 项目的主页
    packages=find_packages(),  # 自动找到包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    tests_require=[
        'pytest',
    ],
)
