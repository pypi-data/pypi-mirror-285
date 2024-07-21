#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2018 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of nsfds3
#
# nsfds3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# nsfds3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nsfds3. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : mar. 10 avril 2018 17:52:42 CEST
# Last Modified : ven. 11 mai 2018 16:13:55 CEST
"""
-----------

setup file for nsfds3

-----------
"""

import codecs
import os.path
import platform
import numpy
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")



if platform.system() == 'Windows':
#    libraries = ['msvcrt']
    libraries = []
    extra_compile_args = ["-O2"]
    extra_link_args = []
    include_dirs=[numpy.get_include(), ]
else:
    libraries = ['m']
    extra_compile_args = ["-O2", "-fopenmp"]
#    extra_compile_args = ["-Ofast", "-fopenmp"]
    extra_link_args = ['-fopenmp']
    include_dirs=[numpy.get_include(), ]

extensions = [
    Extension(
        'nsfds3.cpgrid.cutils',
        ["src/nsfds3/cpgrid/cutils.pyx"],
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,
    ),
    Extension(
        'nsfds3.cpgrid.gridutils',
        ["src/nsfds3/cpgrid/gridutils.pyx"],
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,
    ),
]

setup(
    include_dirs=[numpy.get_include()],
    ext_modules=cythonize(extensions),
    include_package_data=True,
    package_data={'nsfds3.cpgrid': ['*.pyx', '*.c'], },
    version=get_version("src/nsfds3/__init__.py")
)
