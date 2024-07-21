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
Derivations classes :

    * du : classical derivation with finite differences (2D)
    * duA : helpers for PML areas

@author: Cyril Desjouy
"""

cdef extern from "../libcfds/cfilters.c":

    void sf2d_x(double *, double *, double, double, unsigned int, unsigned int, unsigned int)
    void sf2d_y(double *, double *, double, double, unsigned int, unsigned int, unsigned int)
    void sf3d_x(double *, double *, double, double, unsigned int, unsigned int, unsigned int, unsigned int)
    void sf3d_y(double *, double *, double, double, unsigned int, unsigned int, unsigned int, unsigned int)
    void sf3d_z(double *, double *, double, double, unsigned int, unsigned int, unsigned int, unsigned int)

    void lf2d_x(double *, double *, unsigned int, unsigned int, unsigned int)
    void lf2d_y(double *, double *, unsigned int, unsigned int, unsigned int)
    void lf3d_x(double *, double *, unsigned int, unsigned int, unsigned int, unsigned int)
    void lf3d_y(double *, double *, unsigned int, unsigned int, unsigned int, unsigned int)
    void lf3d_z(double *, double *, unsigned int, unsigned int, unsigned int, unsigned int)

cpdef sfilter(u, xnu_n=?, xnu_0=?, copy=?, axis=?, threads=?)
cdef double[:, ::1] sf2d(double[:, ::1] v, double xnu_n, double xnu_0, bint copy, int axis, int threads)
cdef double[:, :, ::1] sf3d(double[:, :, ::1] v, double xnu_n, double xnu_0, bint copy, int axis, int threads)

cpdef laplacian(u, xnu_n=?, xnu_0=?, axis=?, threads=?)
cdef double[:, ::1] lf2d(double[:, ::1] v, int axis, int threads)
cdef double[:, :, ::1] lf3d(double[:, :, ::1] v, int axis, int threads)