#! /usr/bin/python
# -*- coding: utf8 -*-
"""
Setup.py for the bitbucketlock module
"""

from os import path

import setuptools


from bitbucketlock import __version__

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, "README.md")) as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="bitbucketlock",
    packages=setuptools.find_packages(),
    version=__version__,
    author="Alexander Fittkau",
    author_email="alexander.fittkau@gmail.com",
    description="Atlassian Bitbucket Backup Lock handler",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    platforms="all",
    keywords='bitbucket atlassian lock backup',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'bitbucketlock=bitbucketlock:main',
        ], }
)
