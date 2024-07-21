# -*- coding: utf-8 -*-
# @Time        : 2024/07/20 19:44
# @File        : setup.py
# @Description : None
# ----------------------------------------------
# ☆ ☆ ☆ ☆ ☆ ☆ ☆ 
# >>> Author    : Alex
# >>> Mail      : liu_zhao_feng_alex@163.com
# >>> Github    : https://github.com/koking0
# >>> Blog      : https://alex007.blog.csdn.net/
# ☆ ☆ ☆ ☆ ☆ ☆ ☆
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Hu-Tu-Tu",
    version="0.0.1",
    author="alex",
    author_email="liu_zhao_feng_alex@163.com",
    description="基于视觉基座模型的图片识别与理解功能库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Matrix-King-Studio/TuTu",
    project_urls={
        "Bug Tracker": "https://github.com/Matrix-King-Studio/TuTu/issues",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires=">=3.9",
    platforms="any",
    install_requires=[
        "requests==2.32.3"
    ]
)