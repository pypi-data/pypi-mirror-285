# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt', encoding='utf-8') as f:
    install_requires = f.read().splitlines()

setup(
    name='tool_net',
    version='1.0.0',
    author='tangjiadong',
    author_email='958999498@qq.com',
    description='一个在线工具',
    long_description=open("README.md").read(),  # 从 README 文件中读取长描述
    long_description_content_type="text/markdown",
    url='https://github.com/TungTJD/personage_net.git',
    packages=find_packages(),
    classifiers=[  # 分类器，用于在PyPI上显示项目的相关信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',  # Python版本要求
    install_requires=install_requires,
)
