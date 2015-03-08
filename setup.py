#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

import mna
import mna.version
import mna.configuration

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    'License :: OSI Approved :: GNU General Public License (GPL)'
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications",
]

REQUIRES = [
    'setuptools',
    # 'PyQt4',
]


def find_files(directory, base, filter_func=None):
    for name, _subdirs, files in os.walk(directory):
        if files:
            yield (os.path.join(base[:-len(directory)], name),
                   [os.path.join(name, fname) for fname
                    in filter(filter_func, files)])


def get_data_files():
    for x in find_files('data', "data"):
        yield x


setup(
    name='mna',
    version=mna.version.VERSION,
    description='mna - web information aggregator.',
    long_description=open("README.rst").read(),
    classifiers=CLASSIFIERS,
    author='Karol Będkowski',
    author_email='karol.bedkowski at gmail.com',
    url='',
    download_url='',
    license='GPL v3',
    py_modules=['mna', 'mna_dbg'],
    packages=find_packages('.'),
    package_dir={'': '.'},
    include_package_data=True,
    # data_files=list(get_data_files()),
    install_requires=REQUIRES,
    entry_points="""
       [console_scripts]
       mna = mna.main:run
    """,
    zip_safe=False,
)
