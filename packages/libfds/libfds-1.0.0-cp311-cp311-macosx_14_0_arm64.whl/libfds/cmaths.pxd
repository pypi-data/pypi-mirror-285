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
Mathematic functions

    * du : derivation

@author: Cyril Desjouy
"""

import numpy as np
cimport numpy as np
cimport cython


cpdef Py_ssize_t argmin1d(double[::1] v)
cpdef Py_ssize_t argmax1d(double[::1] v)


cpdef double[::1] du1d(double[::1] v, double dx = *)
cpdef double[:, ::1] du2d(double[:, ::1] v, int axis, double dx = *, double dy = *)
cpdef double[:, :, ::1] du3d(double[:, :, ::1] v, int axis, double dx = *, double dy = *, double dz = *)

cpdef double[::1] odu(double[::1] v)
cpdef double[::1] mult(double[::1] v, double a)
cpdef void mult_inplace(double[::1] out, double[::1] v, double a)

cpdef curvilinear2d_trans(double[:, ::1] xp, double[:, ::1] yp,
                          double[:, ::1] xn, double[:, ::1] yn)

cpdef curvilinear2d_metrics(double[:, ::1] J, double[:, ::1] dxn_dxp, double[:, ::1] dxn_dyp,
                                              double[:, ::1] dyn_dxp, double[:, ::1] dyn_dyp)

cpdef curvilinear3d_trans(double[:, :, ::1] xp, double[:, :, ::1] yp, double[:, :, ::1] zp,
                          double[:, :, ::1] xn, double[:, :, ::1] yn, double[:, :, ::1] zn)

cpdef curvilinear3d_metrics(double[:, :, ::1] J, double[:, :, ::1] dxn_dxp, double[:, :, ::1] dxn_dyp, double[:, :, ::1] dxn_dzp,
                                                 double[:, :, ::1] dyn_dxp, double[:, :, ::1] dyn_dyp, double[:, :, ::1] dyn_dzp,
                                                 double[:, :, ::1] dzn_dxp, double[:, :, ::1] dzn_dyp, double[:, :, ::1] dzn_dzp)

cdef double[:, ::1] cinv2d(double[:, ::1] b)
cdef double[:, :, ::1] cinv3d(double[:, :, ::1] b)

cdef double[::1] cdiv1d(double[::1] a, double[::1] b)
cdef double[:, ::1] cdiv2d(double[:, ::1] a, double[:, ::1] b)
cdef double[:, :, ::1] cdiv3d(double[:, :, ::1] a, double[:, :, ::1] b)


cdef double[:, ::1] _du2d_x(double[:, ::1] v, double dx = *)
cdef double[:, ::1] _du2d_y(double[:, ::1] v, double dy = *)
cdef double[:, :, ::1] _du3d_x(double[:, :, ::1] v, double dx = *)
cdef double[:, :, ::1] _du3d_y(double[:, :, ::1] v, double dy = *)
cdef double[:, :, ::1] _du3d_z(double[:, :, ::1] v, double dz = *)
cpdef double[::1] chunk_mean(double[::1] array, Py_ssize_t chunks)

cpdef nan_check(double[:, ::1] a)

cpdef double[:, ::1] super_gaussian2d(x, y, Py_ssize_t ix0, Py_ssize_t iy0, double S0=*,
                                      double kx=*, double ky=*, double k=*,
                                      double Bx=*, double By=*, double Rx=*)

cdef double[:, ::1] super_gaussian2dcrt(double[::1] x, double[::1] y,
                                        Py_ssize_t ix0, Py_ssize_t iy0, double S0,
                                        double kx, double ky, double k,
                                        double Bx, double By, double Rx)

cdef double[:, ::1] super_gaussian2dcrv(double[:, ::1] x, double[:, ::1] y,
                                         Py_ssize_t ix0, Py_ssize_t iy0, double S0,
                                         double kx, double ky, double k,
                                         double Bx, double By, double Rx)

cpdef double[:, :, ::1] super_gaussian3d(x, y, z,
                                         Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                         double S0=*,
                                         double kx=*, double ky=*, double kz=*,
                                         double k=*,
                                         double Bx=*, double By=*, double Bz=*,
                                         double Rx=*)

cdef double[:, :, ::1] super_gaussian3dcrt(double[::1] x, double[::1] y, double[::1] z,
                                           Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                           double S0,
                                           double kx, double ky, double kz, double k,
                                           double Bx, double By, double Bz, double Rx)

cdef double[:, :, ::1] super_gaussian3dcrv(double[:, :, ::1] x, double[:, :, ::1] y, double[:, :, ::1] z,
                                           Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                           double S0,
                                           double kx, double ky, double kz, double k,
                                           double Bx, double By, double Bz, double Rx)