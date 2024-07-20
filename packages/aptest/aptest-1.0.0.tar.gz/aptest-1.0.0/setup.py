#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os 
from setuptools import setup, find_packages

MAJOR =1
MINOR =0
PATCH =0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"

def get_install_requires():
    reqs = [
            'pandas>=0.18.0',
			'numpy>=1.9.2'
            ]
    return reqs
setup(
	name = "aptest",
	version = VERSION,
    author ="haobinherbert",
    author_email = "haobinherbert@163.com",
    long_description_content_type="text/markdown",
	url = 'https://github.com/hbyaoherbert/Apclusterv.git',
	long_description = open('README.md',encoding="utf-8").read(),
    python_requires=">=3.7",
    install_requires=get_install_requires(),
	packages = find_packages(),
    entry_points={
        "console_scripts" : ['aptest = aptest.mcl2map:main']
    },
 	license = 'Apache',
   	classifiers = [
       'License :: OSI Approved :: Apache Software License',
       'Natural Language :: English',
       'Operating System :: OS Independent',
       'Programming Language :: Python',       
       'Programming Language :: Python :: 3.7',
       'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    package_data={'': ['scripts/*.R', '*.txt','.toml']}, #这个很重要
    include_package_data=True #也选上

)
