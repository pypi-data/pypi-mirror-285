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


cpdef where(mask, pattern):

    cdef Py_ssize_t px, py, pz

    if mask.ndim == 4:
        px, py, pz = pattern
        return np.asarray(where3d(mask, px, py, pz))
    elif mask.ndim == 3:
        px, py = pattern
        return np.asarray(where2d(mask, px, py))
    else:
        raise ValueError('Bad dimensions')


cpdef nonzeros(mask):
    if mask.ndim == 3:
        return np.asarray(nonzeros3d(mask))
    elif mask.ndim == 2:
        return np.asarray(nonzeros2d(mask))
    else:
        raise ValueError('Bad dimensions')


cdef short[:, ::1] where3d(INT8[:, :, :, ::1] mask,
               Py_ssize_t px, Py_ssize_t py, Py_ssize_t pz):

    cdef Py_ssize_t ix, iy, iz, ii = 0
    cdef int nx = mask.shape[0]
    cdef int ny = mask.shape[1]
    cdef int nz = mask.shape[2]

    cdef short[:, ::1] out = np.empty((nx*ny*nz, 3), dtype=np.int16)

    #for ix in prange(nx, nogil=True, num_threads=4):
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                if mask[ix, iy, iz, 0] == px and \
                   mask[ix, iy, iz, 1] == py and \
                   mask[ix, iy, iz, 2] == pz:
                    out[ii, 0] = ix
                    out[ii, 1] = iy
                    out[ii, 2] = iz
                    ii = ii + 1

    return out[:ii, :]


cdef short[:, ::1] where2d(INT8[:, :, ::1] mask, Py_ssize_t px, Py_ssize_t py):

    cdef Py_ssize_t ix, iy, ii = 0
    cdef int nx = mask.shape[0]
    cdef int ny = mask.shape[1]

    cdef short[:, ::1] out = np.empty((nx*ny, 3), dtype=np.int16)

    #for ix in prange(nx, nogil=True, num_threads=4):
    for ix in range(nx):
        for iy in range(ny):
            if mask[ix, iy, 0] == px and mask[ix, iy, 1] == py:
                out[ii, 0] = ix
                out[ii, 1] = iy
                ii = ii + 1

    return out[:ii, :]


cdef short[:, ::1] nonzeros3d(INT8[:, :, ::1] mask):

    cdef Py_ssize_t ix, iy, iz, ii = 0
    cdef int nx = mask.shape[0]
    cdef int ny = mask.shape[1]
    cdef int nz = mask.shape[2]

    cdef short[:, ::1] out = np.empty((nx*ny*nz, 3), dtype=np.int16)

    #for ix in prange(nx, nogil=True, num_threads=4):
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                if mask[ix, iy, iz] == True:
                    out[ii, 0] = ix
                    out[ii, 1] = iy
                    out[ii, 2] = iz
                    ii = ii + 1

    return out[:ii, :]


cdef short[:, ::1] nonzeros2d(INT8[:, ::1] mask):

    cdef Py_ssize_t ix, iy, ii = 0
    cdef int nx = mask.shape[0]
    cdef int ny = mask.shape[1]

    cdef short[:, ::1] out = np.empty((nx*ny, 2), dtype=np.int16)

    #for ix in prange(nx, nogil=True, num_threads=4):
    for ix in range(nx):
        for iy in range(ny):
            if mask[ix, iy] == True:
                    out[ii, 0] = ix
                    out[ii, 1] = iy
                    ii = ii + 1

    return out[:ii, :]


cpdef zconsecutives(short[:, ::1] splits, short[:, ::1] coords):

    cdef int nc = coords.shape[0]
    cdef int ns = splits.shape[0]
    cdef int old_length
    cdef Py_ssize_t ix, ii, iii = 0, jjj = 0

    cdef short start_new, stop_new, x_new, y_new
    cdef short x_old = -1
    cdef short y_old = -1
    cdef short start_old = splits[0, 0]
    cdef short stop_old = splits[0, 1]
    cdef short[:, ::1] out = np.empty((nc, 4), dtype=np.int16)

    for ix in range(ns):
        start_new = splits[ix, 0]
        stop_new = splits[ix, 1]
        for ii in range(stop_new - start_new + 1):
            x_new = coords[iii, 0]
            y_new = coords[iii, 1]
            if x_new != x_old or y_new != y_old or start_new != start_old or stop_new != stop_old:
                out[jjj, 0] = start_new
                out[jjj, 1] = stop_new
                out[jjj, 2] = x_new
                out[jjj, 3] = y_new
                jjj += 1
            iii += 1
            x_old = x_new
            y_old = y_new
        start_old = start_new
        stop_old = stop_new

    return np.asarray(out[:jjj, :])


cpdef yconsecutives(short[:, ::1] splits, short[:, ::1] coords):

    cdef int nc = coords.shape[0]
    cdef int ns = splits.shape[0]
    cdef int old_length
    cdef Py_ssize_t ix, ii, iii = 0, jjj = 0

    cdef short start_new, stop_new, x_new, x_old = -1
    cdef short start_old = splits[0, 0]
    cdef short stop_old = splits[0, 1]
    cdef short[:, ::1] out = np.empty((nc, 3), dtype=np.int16)

    for ix in range(ns):
        start_new = splits[ix, 0]
        stop_new = splits[ix, 1]
        for ii in range(stop_new - start_new + 1):
            x_new = coords[iii, 0]
            if x_new != x_old or start_new != start_old or stop_new != stop_old:
                out[jjj, 0] = start_new
                out[jjj, 1] = stop_new
                out[jjj, 2] = x_new
                jjj += 1
            iii += 1
            x_old = x_new
        start_old = start_new
        stop_old = stop_new

    return np.asarray(out[:jjj, :])


cpdef void test3d(double[:, :, ::1] K, double[:, :, ::1] E, double odx, int cpu) noexcept nogil:

    cdef Py_ssize_t ix, iy, iz
    cdef int nx = K.shape[0]
    cdef int ny = K.shape[1]
    cdef int nz = K.shape[2]

    if cpu == 1:
        for ix in range(5, nx - 5):
            for iy in range(5, ny - 5):
                for iz in range(5, nz - 5):
                    K[ix, iy, iz] = (a11c[1]*(E[ix+1, iy+1, iz+1] - E[ix-1, iy-1, iz-1]) +
                                    a11c[2]*(E[ix+2, iy+2, iz+2] - E[ix-2, iy-2, iz-2]) +
                                    a11c[3]*(E[ix+3, iy+3, iz+3] - E[ix-3, iy-3, iz-3]) +
                                    a11c[4]*(E[ix+4, iy+4, iz+4] - E[ix-4, iy-4, iz-4]) +
                                    a11c[5]*(E[ix+5, iy+5, iz+5] - E[ix-5, iy-5, iz-5]))*odx

    else:
        for ix in prange(5, nx - 5, nogil=True, num_threads=cpu):
            for iy in range(5, ny - 5):
                for iz in range(5, nz - 5):
                    K[ix, iy, iz] = (a11c[1]*(E[ix+1, iy+1, iz+1] - E[ix-1, iy-1, iz-1]) +
                                    a11c[2]*(E[ix+2, iy+2, iz+2] - E[ix-2, iy-2, iz-2]) +
                                    a11c[3]*(E[ix+3, iy+3, iz+3] - E[ix-3, iy-3, iz-3]) +
                                    a11c[4]*(E[ix+4, iy+4, iz+4] - E[ix-4, iy-4, iz-4]) +
                                    a11c[5]*(E[ix+5, iy+5, iz+5] - E[ix-5, iy-5, iz-5]))*odx


cpdef void test2d(double[:, ::1] K, double[:, ::1] E, double odx, int cpu) noexcept nogil:

    cdef Py_ssize_t ix, iy
    cdef int nx = K.shape[0]
    cdef int ny = K.shape[1]

    if cpu == 1:
        for ix in range(5, nx - 5):
            for iy in range(5, ny - 5):
                K[ix, iy] = (a11c[1]*(E[ix+1, iy+1] - E[ix-1, iy-1]) +
                            a11c[2]*(E[ix+2, iy+2] - E[ix-2, iy-2]) +
                            a11c[3]*(E[ix+3, iy+3] - E[ix-3, iy-3]) +
                            a11c[4]*(E[ix+4, iy+4] - E[ix-4, iy-4]) +
                            a11c[5]*(E[ix+5, iy+5] - E[ix-5, iy-5]))*odx
    else:
        for ix in prange(5, nx - 5, nogil=True, num_threads=cpu):
            for iy in range(5, ny - 5):
                K[ix, iy] = (a11c[1]*(E[ix+1, iy+1] - E[ix-1, iy-1]) +
                            a11c[2]*(E[ix+2, iy+2] - E[ix-2, iy-2]) +
                            a11c[3]*(E[ix+3, iy+3] - E[ix-3, iy-3]) +
                            a11c[4]*(E[ix+4, iy+4] - E[ix-4, iy-4]) +
                            a11c[5]*(E[ix+5, iy+5] - E[ix-5, iy-5]))*odx