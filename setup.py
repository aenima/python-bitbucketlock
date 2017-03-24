#! /usr/bin/python
# -*- coding: utf8 -*-
"""
Setup.py for the bitbucketbackuplock module
"""

import setuptools


VERSION = "0.1"


setuptools.setup(
    name="hello", version=VERSION,
    packages=setuptools.find_packages(),
    author="Alexander Fittkau",
    author_email="a.fittkau@e.ito.de",
    description="Atlassian Bitbucket Backup Lock handler",
    license="MIT",
    platforms="all",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=[
        "requests",
    ],
)
