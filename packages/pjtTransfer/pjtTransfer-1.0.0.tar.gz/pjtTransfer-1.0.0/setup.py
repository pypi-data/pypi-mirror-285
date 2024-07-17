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
    name='pjtTransfer',
    version='1.0.0',
    author='hsy',
    author_email='532848352@qq.com',
    url='https://github.com/jacsons8/zhenzhi/blob/main/%E6%B5%8B%E8%AF%95/data/paramTransfer.py',
    description='Defect relation mapping',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pjtTransfer'],
    install_requires=[],
    package_data={
        'pjtTransfer': ['pjtTransferDictionary.pkl'],
    },
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
