from __future__ import print_function

import io
import os

here = os.path.abspath(os.path.dirname(__file__))
from setuptools import setup, find_packages
import sys

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = ''

# REQUIRED = read_requirements('requirements.txt')
setup(
    name='transfer_phone',
    version='1.0',
    author='White.tie',
    author_email='1042798703@qq.com',
    url='https://github.com/tieyongjie/transfer_phone',
    description='Defect relation mapping',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['transfer_phone'],
    install_requires=["pickle",""],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
