# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     setup.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/07/15
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from setuptools import setup, find_packages

setup(
    name='airtest-helper',
    version='0.0.1',
    description='This is my airtest helper package',
    long_description='This is my airtest helper package',
    author='ckf10000',
    author_email='ckf10000@sina.com',
    url='https://github.com/ckf10000/airtest-helper',
    packages=find_packages(),
    install_requires=[
        'numpy==1.26.4',
        'airtest>=1.3.4',
        'pocoui>=1.0.94'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)