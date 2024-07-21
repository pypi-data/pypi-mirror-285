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
# Creation Date : 2017-03-21 - 16:51:13
"""
-----------
Filters :

    * Selective filter
    * Laplacian filter

@author: Cyril Desjouy
"""

cimport cython
import numpy as _np
cimport numpy as _np


cpdef sfilter(u, xnu_n=0.5, xnu_0=0.01, copy=False, axis=-1, threads=1):
    """Selective filter.

    Parameters
    ----------
    u: numpy.array
        Contiguous array to be filtered
    xnu_n, xnu_0: double
        Filter coefficients
    copy: bool
        Whether to apply filter on a copy or not. Default to False.
    axis: int
        axis to filter.
    threads: int, optional
        Number of threads to use for the computation. Default to 1.

    Returns
    -------
    uf: numpy.array
        The filtered array
    """
    if not isinstance(threads, int):
        threads = 1

    if not axis in [-1, 0, 1]:
        axis = -1

    if u.ndim == 3:
        return sf3d(u, xnu_n, xnu_0, copy, axis, threads)

    return sf2d(u, xnu_n, xnu_0, copy, axis, threads)


cdef double[:, ::1] sf2d(double[:, ::1] v, double xnu_n, double xnu_0, bint copy, int axis, int threads):

    cdef int nx = v.shape[0]
    cdef int ny = v.shape[1]
    cdef double[:, ::1] vf = _np.empty((nx, ny))
    cdef double[:, ::1] vc

    if copy:
        vc = v.copy()
    else:
        vc = v

    if axis == 0 or axis == -1:
        sf2d_x(&vf[0, 0], &vc[0, 0], xnu_n, xnu_0, nx, ny, threads)
    if axis == 1 or axis == -1:
        sf2d_y(&vf[0, 0], &vc[0, 0], xnu_n, xnu_0, nx, ny, threads)
    return vc


cdef double[:, :, ::1] sf3d(double[:, :, ::1] v, double xnu_n, double xnu_0, bint copy, int axis, int threads):

    cdef int nx = v.shape[0]
    cdef int ny = v.shape[1]
    cdef int nz = v.shape[2]
    cdef double[:, :, ::1] vf = _np.empty((nx, ny, nz))
    cdef double[:, :, ::1] vc

    if copy:
        vc = v.copy()
    else:
        vc = v

    if axis == 0 or axis == -1:
        sf3d_x(&vf[0, 0, 0], &vc[0, 0, 0], xnu_n, xnu_0, nx, ny, nz, threads)
    if axis == 1 or axis == -1:
        sf3d_y(&vf[0, 0, 0], &vc[0, 0, 0], xnu_n, xnu_0, nx, ny, nz, threads)
    if axis == 2 or axis == -1:
        sf3d_z(&vf[0, 0, 0], &vc[0, 0, 0], xnu_n, xnu_0, nx, ny, nz, threads)
    return vc


cpdef laplacian(u, xnu_n=0.5, xnu_0=0.01, axis=-1, threads=1):
    """Laplacian filter.

    Parameters
    ----------
    u: numpy.array
        Array to be filtered
    axis: int
        axis to filter.
    threads: int, optional
        Number of cpu to use for the computation.

    Returns
    -------
    uf: numpy.array
        The filtered array
    """
    if not isinstance(threads, int):
        threads = 1

    if not axis in [-1, 0, 1]:
        axis = -1

    if u.ndim == 3:
        return lf3d(u, axis, threads)

    return lf2d(u, axis, threads)


cdef double[:, ::1] lf2d(double[:, ::1] v, int axis, int threads):

    cdef int nx = v.shape[0]
    cdef int ny = v.shape[1]
    cdef double[:, ::1] vf = _np.empty((nx, ny))

    if axis == 0 or axis == -1:
        lf2d_x(&vf[0, 0], &v[0, 0], nx, ny, threads)
    if axis == 1 or axis == -1:
        lf2d_y(&vf[0, 0], &v[0, 0], nx, ny, threads)
    return vf


cdef double[:, :, ::1] lf3d(double[:, :, ::1] v, int axis, int threads):

    cdef int nx = v.shape[0]
    cdef int ny = v.shape[1]
    cdef int nz = v.shape[2]
    cdef double[:, :, ::1] vf = _np.empty((nx, ny, nz))

    if axis == 0 or axis == -1:
        lf3d_x(&vf[0, 0, 0], &v[0, 0, 0], nx, ny, nz, threads)
    if axis == 1 or axis == -1:
        lf3d_y(&vf[0, 0, 0], &v[0, 0, 0], nx, ny, nz, threads)
    if axis == 2 or axis == -1:
        lf3d_z(&vf[0, 0, 0], &v[0, 0, 0], nx, ny, nz, threads)
    return vf