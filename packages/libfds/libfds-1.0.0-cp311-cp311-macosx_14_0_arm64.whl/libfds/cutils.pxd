# -*- coding: utf-8 -*-
#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False
#cython: cdivision=True
#cython: initializedcheck=False
#
# Copyright © 2016-2019 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of ofdlib2
#
# ofdlib2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ofdlib2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ofdlib2. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : 2017-03-21 - 16:51:13
"""
-----------
Derivations classes :

    * du : classical derivation with finite differences (2D)
    * duA : helpers for PML areas

@author: Cyril Desjouy
"""

import numpy as np
cimport numpy as np
cimport cython
from cython.parallel cimport prange, parallel
from numpy cimport int64_t, uint8_t

ctypedef np.npy_int8 INT8


cdef extern from "../libcfds/coefficients.h":
    cdef double[6] a11c


cpdef where(mask, pattern)
cpdef nonzeros(mask)

cdef short[:, ::1] where3d(INT8[:, :, :, ::1] mask, Py_ssize_t px, Py_ssize_t py, Py_ssize_t pz)
cdef short[:, ::1] where2d(INT8[:, :, ::1] mask, Py_ssize_t px, Py_ssize_t py)


cdef short[:, ::1] nonzeros3d(INT8[:, :, ::1] mask)
cdef short[:, ::1] nonzeros2d(INT8[:, ::1] mask)

cpdef zconsecutives(short[:, ::1] splits, short[:, ::1] coords)
cpdef yconsecutives(short[:, ::1] splits, short[:, ::1] coords)

cpdef void test3d(double[:, :, ::1] K, double[:, :, ::1] E, double odx, int cpu) noexcept nogil
cpdef void test2d(double[:, ::1] K, double[:, ::1] E, double odx, int cpu) noexcept nogil