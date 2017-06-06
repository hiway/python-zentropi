#!/usr/bin/env python
# coding=utf-8
from __future__ import (
    absolute_import,
    print_function
)

import io
from glob import glob
from os.path import (
    basename,
    dirname,
    join,
    splitext
)

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='zentinker',
    version='0.1.0',
    license='',  # Recommended: 'Apache 2.0'
    description='',
    author='',
    author_email='',
    url='',  # Repository (bitbucket, github, gitlab...)
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'zentropi>=0.1.3, <0.2.0',
    ],
    entry_points={
        'console_scripts': [
            'zentinker = zentinker.cli:main',
        ]
    },
)
