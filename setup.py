#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


redis = [
    'aioredis==0.3.0, <0.4',
]


setup(
    name='zentropi',
    version='0.1.3',
    license='Apache 2.0',
    description='Script Your World.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Harshad Sharma',
    author_email='harshad@sharma.io',
    url='https://github.com/zentropi/python-zentropi',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    keywords=[
        'agent-based',
        'automation',
        'event-based'
        'iot',
        'iot-framework',
        'iot-platform',
        'pub-sub',
    ],
    install_requires=[
        'bloom_filter >= 1.3, <2.0'
        'click>=6.7, <7.0',
        'fuzzywuzzy>=0.15.0, <0.20',
        'parse>=1.8.0, <2.0',
        'prompt_toolkit==1.0.14, <1.1',
        'Pygments>=2.2.0, <2.3',
        'python-Levenshtein>=0.12.0',
        'sortedcontainers>=1.5.7, <1.6',
    ],
    extras_require={
        'redis': redis,
    },
    entry_points={
        'console_scripts': [
            'zentropi = zentropi.cli:main',
        ]
    },
)
