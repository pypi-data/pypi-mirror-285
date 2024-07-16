# !/usr/bin/env python3.9
# -*- coding:utf-8 -*-
# ---------------------------------------------------------
# @Time    : 2024/07/15 17:41
# @Author  : huwenxue
# @FileName: setup.py.py
# ---------------------------------------------------------
# Common reference
from setuptools import setup, find_packages
# ---------------------------------------------------------

setup(
    name='enochcolor',
    version='0.1',
    packages=find_packages(),
    install_requires=[
    'colour-science'
    ],
    entry_points={
        'console_scripts': [
            # 如果你有任何命令行工具，可以在这里定义
            # 'my_command=my_sdk.module:function',
        ],
    },
    author='Think Different',
    author_email='your.email@example.com',
    description='A brief description of your SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/enoch/my_sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

