#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2019 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of libfds
#
# libfds is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libfds is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libfds. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : 2018-04-10 - 17:52:42
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""

import pathlib
import platform
import numpy
from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
from Cython.Compiler import Options


package_names = ['cfdtd', 'filters', 'cmaths', 'cutils']

# Options

Options.annotate = True
Options.fast_fail = True
compiler_directives = {'linetrace': True, 'profile': True}
#compiler_directives = dict()
force=True

if platform.system() == 'Windows':
#    libraries = ['msvcrt']
    libraries = []
    extra_compile_args = ["-O2", "-ftree-vectorize", "/openmp"]
    extra_link_args = ["/openmp"]
    define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    include_dirs=[numpy.get_include(), "./src/libcfds"]
    library_dirs=[]
else:
    libraries = ['m',]
#    extra_compile_args = ["-O2", "-fopenmp"]
    extra_compile_args = ["-O3", "-mcpu=native", "-fopenmp", "-ftree-vectorize"]
    extra_link_args = ['-fopenmp']
    define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    include_dirs=[numpy.get_include(), "./src/libcfds"]
    library_dirs=[]


extensions = [Extension(name=f"libfds.{name}", sources=[f"src/libfds/{name}.pyx"],
                        libraries=libraries,
                        extra_compile_args=extra_compile_args,
                        extra_link_args=extra_link_args,
                        define_macros=define_macros,
                        include_dirs=include_dirs,
                        library_dirs=library_dirs) for name in package_names]

setup(
    version='1.0.0',
    license="GPL",
    author="Cyril Desjouy",
    author_email="cyril.desjouy@univ-lemans.fr",
    install_requires=["numpy"],
    setup_requires=['numpy'],
    ext_modules=cythonize(extensions, force=force, compiler_directives=compiler_directives),
    include_package_data=True,
    packages=['libfds', 'libcfds'],
    package_dir={'': 'src'},
    package_data={'libcfds': ['*.c', '*.h'],
                  'libfds': ['*.pxd', '*.so']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ]
)
