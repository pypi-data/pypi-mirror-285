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
from cython.parallel cimport prange, parallel
from libc.math cimport exp, isnan, fabs


cdef extern from "../libcfds/coefficients.h":
    cdef double[6] a11c
    cdef double[5][11] a11d


cpdef Py_ssize_t argmin1d(double[::1] v):
    cdef Py_ssize_t i
    cdef Py_ssize_t k = 0
    cdef Py_ssize_t nx = v.shape[0]

    for i in range(1, nx):
        if v[i] < v[k]:
            k = i
    return k


cpdef Py_ssize_t argmax1d(double[::1] v):
    cdef Py_ssize_t i
    cdef Py_ssize_t k = 0
    cdef Py_ssize_t nx = v.shape[0]

    for i in range(1, nx):
        if v[i] > v[k]:
            k = i
    return k


cpdef double[::1] du1d(double[::1] v, double dx = 1.):
    """
        Returns derivative of v. The step dx can be provided.
    """
    cdef Py_ssize_t i
    cdef Py_ssize_t n = v.shape[0]
    cdef double odx = 1. / dx
    cdef double[::1] dv = np.zeros_like(v)


    for i in range(5, n - 5):
        dv[i] = (a11c[1] * (v[i+1] - v[i-1]) +
                 a11c[2] * (v[i+2] - v[i-2]) +
                 a11c[3] * (v[i+3] - v[i-3]) +
                 a11c[4] * (v[i+4] - v[i-4]) +
                 a11c[5] * (v[i+5] - v[i-5])) * odx

    for i in range(0, 5):
        dv[i] = (a11d[i][0] * v[0] +
                 a11d[i][1] * v[1] +
                 a11d[i][2] * v[2] +
                 a11d[i][3] * v[3] +
                 a11d[i][4] * v[4] +
                 a11d[i][5] * v[5] +
                 a11d[i][6] * v[6] +
                 a11d[i][7] * v[7] +
                 a11d[i][8] * v[8] +
                 a11d[i][9] * v[9] +
                 a11d[i][10] * v[10]) * odx

    for i in range(n-1, n-6, -1):
        dv[i] = - (a11d[n-i-1][0] * v[n-1] +
                   a11d[n-i-1][1] * v[n-2] +
                   a11d[n-i-1][2] * v[n-3] +
                   a11d[n-i-1][3] * v[n-4] +
                   a11d[n-i-1][4] * v[n-5] +
                   a11d[n-i-1][5] * v[n-6] +
                   a11d[n-i-1][6] * v[n-7] +
                   a11d[n-i-1][7] * v[n-8] +
                   a11d[n-i-1][8] * v[n-9] +
                   a11d[n-i-1][9] * v[n-10] +
                   a11d[n-i-1][10] * v[n-11]) * odx

    return dv


cpdef double[:, ::1] du2d(double[:, ::1] v, int axis, double dx = 1., double dy = 1.):
    """
        Returns derivative of v following provided axis. The steps dx and dy can be provided.
    """

    if axis == 0:
        return _du2d_x(v, dx)
    elif axis == 1:
        return _du2d_y(v, dy)

    raise ValueError('Wrong axis')


cpdef double[:, :, ::1] du3d(double[:, :, ::1] v, int axis, double dx = 1., double dy = 1., double dz = 1.):
    """
        Returns derivative of v following provided axis. The steps dx, dy and dz can be provided.
    """

    if axis == 0:
        return _du3d_x(v, dx)
    elif axis == 1:
        return _du3d_y(v, dy)
    elif axis == 2:
        return _du3d_z(v, dz)

    raise ValueError('Wrong axis')


cpdef double[::1] odu(double[::1] v):

    cdef Py_ssize_t i
    cdef Py_ssize_t n = v.shape[0]
    cdef double[::1] dv

    dv = du1d(v, 1.)

    for i in range(n):
        dv[i] = 1. / dv[i]

    return dv


cpdef double[::1] mult(double[::1] v, double a):

    cdef Py_ssize_t i
    cdef Py_ssize_t n = v.shape[0]
    cdef double[::1] out = np.zeros_like(v)

    for i in range(n):
        out[i] = a * v[i]

    return out


cpdef void mult_inplace(double[::1] out, double[::1] v, double a):

    cdef Py_ssize_t i
    cdef Py_ssize_t n = v.shape[0]

    for i in range(n):
        out[i] = a * v[i]


cpdef curvilinear2d_trans(double[:, ::1] xp, double[:, ::1] yp,
                          double[:, ::1] xn, double[:, ::1] yn):

    cdef Py_ssize_t nx = xp.shape[0]
    cdef Py_ssize_t ny = yp.shape[1]
    cdef double[:, ::1] dxp_dxn, dxp_dyn, dyp_dxn, dyp_dyn
    cdef double[:, ::1] J = np.empty_like(xp)
    cdef double[:, ::1] dxn_dxp = np.empty_like(xp)
    cdef double[:, ::1] dxn_dyp = np.empty_like(xp)
    cdef double[:, ::1] dyn_dxp = np.empty_like(xp)
    cdef double[:, ::1] dyn_dyp = np.empty_like(xp)

    # Can be optimized : (xn, yn) are actually 1d !
    dxp_dxn = cdiv2d(du2d(xp, axis=0), du2d(xn, axis=0))
    dxp_dyn = cdiv2d(du2d(xp, axis=1), du2d(yn, axis=1))

    dyp_dxn = cdiv2d(du2d(yp, axis=0), du2d(xn, axis=0))
    dyp_dyn = cdiv2d(du2d(yp, axis=1), du2d(yn, axis=1))

    for ix in range(nx):
        for iy in range(ny):
            J[ix, iy] = 1. / (dxp_dxn[ix, iy] * dyp_dyn[ix, iy] -
                                dxp_dyn[ix, iy] * dyp_dxn[ix, iy])

    # Jacobian matrix
    for ix in range(nx):
        for iy in range(ny):
            dxn_dxp[ix, iy] = J[ix, iy] * dyp_dyn[ix, iy]
            dxn_dyp[ix, iy] = -J[ix, iy] * dxp_dyn[ix, iy]

            dyn_dxp[ix, iy] = -J[ix, iy] * dyp_dxn[ix, iy]
            dyn_dyp[ix, iy] = J[ix, iy] * dxp_dxn[ix, iy]

    return J, dxn_dxp, dxn_dyp, dyn_dxp, dyn_dyp


cpdef curvilinear2d_metrics(double[:, ::1] J, double[:, ::1] dxn_dxp, double[:, ::1] dxn_dyp,
                                              double[:, ::1] dyn_dxp, double[:, ::1] dyn_dyp):

    cdef Py_ssize_t nx = dxn_dxp.shape[0]
    cdef Py_ssize_t ny = dyn_dyp.shape[1]
    cdef double[:, ::1] invariant_x = np.empty_like(dxn_dxp)
    cdef double[:, ::1] invariant_y = np.empty_like(dyn_dyp)
    cdef double[:, ::1] comp_x, comp_y

    comp_x = du2d(cdiv2d(dxn_dxp, J), axis=0)
    comp_y = du2d(cdiv2d(dyn_dxp, J), axis=1)

    for ix in range(nx):
        for iy in range(ny):
            invariant_x[ix, iy] = comp_x[ix, iy] + comp_y[ix, iy]

    comp_x = du2d(cdiv2d(dxn_dyp, J), axis=0)
    comp_y = du2d(cdiv2d(dyn_dyp, J), axis=1)

    for ix in range(nx):
        for iy in range(ny):
            invariant_y[ix, iy] = comp_x[ix, iy] + comp_y[ix, iy]

    return invariant_x, invariant_y


cpdef curvilinear3d_trans(double[:, :, ::1] xp, double[:, :, ::1] yp, double[:, :, ::1] zp,
                          double[:, :, ::1] xn, double[:, :, ::1] yn, double[:, :, ::1] zn):

    cdef Py_ssize_t nx = xp.shape[0]
    cdef Py_ssize_t ny = yp.shape[1]
    cdef Py_ssize_t nz = zp.shape[2]
    cdef double[:, :, ::1] dxp_dxn, dxp_dyn, dxp_dzn
    cdef double[:, :, ::1] dyp_dxn, dyp_dyn, dyp_dzn
    cdef double[:, :, ::1] dzp_dxn, dzp_dyn, dzp_dzn
    cdef double[:, :, ::1] J = np.empty_like(xp)
    cdef double[:, :, ::1] dxn_dxp = np.empty_like(xp)
    cdef double[:, :, ::1] dxn_dyp = np.empty_like(xp)
    cdef double[:, :, ::1] dxn_dzp = np.empty_like(xp)
    cdef double[:, :, ::1] dyn_dxp = np.empty_like(xp)
    cdef double[:, :, ::1] dyn_dyp = np.empty_like(xp)
    cdef double[:, :, ::1] dyn_dzp = np.empty_like(xp)
    cdef double[:, :, ::1] dzn_dxp = np.empty_like(xp)
    cdef double[:, :, ::1] dzn_dyp = np.empty_like(xp)
    cdef double[:, :, ::1] dzn_dzp = np.empty_like(xp)

    dxp_dxn = cdiv3d(du3d(xp, axis=0), du3d(xn, axis=0))
    dxp_dyn = cdiv3d(du3d(xp, axis=1), du3d(yn, axis=1))
    dxp_dzn = cdiv3d(du3d(xp, axis=2), du3d(zn, axis=2))

    dyp_dxn = cdiv3d(du3d(yp, axis=0), du3d(xn, axis=0))
    dyp_dyn = cdiv3d(du3d(yp, axis=1), du3d(yn, axis=1))
    dyp_dzn = cdiv3d(du3d(yp, axis=2), du3d(zn, axis=2))

    dzp_dxn = cdiv3d(du3d(zp, axis=0), du3d(xn, axis=0))
    dzp_dyn = cdiv3d(du3d(zp, axis=1), du3d(yn, axis=1))
    dzp_dzn = cdiv3d(du3d(zp, axis=2), du3d(zn, axis=2))

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                J[ix, iy, iz] = 1. / (dxp_dxn[ix, iy, iz] * (dyp_dyn[ix, iy, iz] * dzp_dzn[ix, iy, iz] -
                                                             dyp_dzn[ix, iy, iz] * dzp_dyn[ix, iy, iz]) +
                                      dxp_dyn[ix, iy, iz] * (dyp_dzn[ix, iy, iz] * dzp_dxn[ix, iy, iz] -
                                                             dyp_dxn[ix, iy, iz] * dzp_dzn[ix, iy, iz]) +
                                      dxp_dzn[ix, iy, iz] * (dyp_dxn[ix, iy, iz] * dzp_dyn[ix, iy, iz] -
                                                             dyp_dyn[ix, iy, iz] * dzp_dxn[ix, iy, iz]))

    # Jacobian matrix
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                dxn_dxp[ix, iy, iz] = J[ix, iy, iz] * (dyp_dyn[ix, iy, iz] * dzp_dzn[ix, iy, iz] - dyp_dzn[ix, iy, iz] * dzp_dyn[ix, iy, iz])
                dxn_dyp[ix, iy, iz] = J[ix, iy, iz] * (dzp_dyn[ix, iy, iz] * dxp_dzn[ix, iy, iz] - dzp_dzn[ix, iy, iz] * dxp_dyn[ix, iy, iz])
                dxn_dzp[ix, iy, iz] = J[ix, iy, iz] * (dxp_dyn[ix, iy, iz] * dyp_dzn[ix, iy, iz] - dxp_dzn[ix, iy, iz] * dyp_dyn[ix, iy, iz])

                dyn_dxp[ix, iy, iz] = J[ix, iy, iz] * (dyp_dzn[ix, iy, iz] * dzp_dxn[ix, iy, iz] - dyp_dxn[ix, iy, iz] * dzp_dzn[ix, iy, iz])
                dyn_dyp[ix, iy, iz] = J[ix, iy, iz] * (dzp_dzn[ix, iy, iz] * dxp_dxn[ix, iy, iz] - dzp_dxn[ix, iy, iz] * dxp_dzn[ix, iy, iz])
                dyn_dzp[ix, iy, iz] = J[ix, iy, iz] * (dxp_dzn[ix, iy, iz] * dyp_dxn[ix, iy, iz] - dxp_dxn[ix, iy, iz] * dyp_dzn[ix, iy, iz])

                dzn_dxp[ix, iy, iz] = J[ix, iy, iz] * (dyp_dxn[ix, iy, iz] * dzp_dyn[ix, iy, iz] - dyp_dyn[ix, iy, iz] * dzp_dxn[ix, iy, iz])
                dzn_dyp[ix, iy, iz] = J[ix, iy, iz] * (dzp_dxn[ix, iy, iz] * dxp_dyn[ix, iy, iz] - dzp_dyn[ix, iy, iz] * dxp_dxn[ix, iy, iz])
                dzn_dzp[ix, iy, iz] = J[ix, iy, iz] * (dxp_dxn[ix, iy, iz] * dyp_dyn[ix, iy, iz] - dxp_dyn[ix, iy, iz] * dyp_dxn[ix, iy, iz])

    return J, dxn_dxp, dxn_dyp, dxn_dzp, dyn_dxp, dyn_dyp, dyn_dzp, dzn_dxp, dzn_dyp, dzn_dzp


cpdef curvilinear3d_metrics(double[:, :, ::1] J, double[:, :, ::1] dxn_dxp, double[:, :, ::1] dxn_dyp, double[:, :, ::1] dxn_dzp,
                                                 double[:, :, ::1] dyn_dxp, double[:, :, ::1] dyn_dyp, double[:, :, ::1] dyn_dzp,
                                                 double[:, :, ::1] dzn_dxp, double[:, :, ::1] dzn_dyp, double[:, :, ::1] dzn_dzp):

    cdef Py_ssize_t nx = dxn_dxp.shape[0]
    cdef Py_ssize_t ny = dyn_dyp.shape[1]
    cdef Py_ssize_t nz = dzn_dzp.shape[2]
    cdef double[:, :, ::1] invariant_x = np.empty_like(dxn_dxp)
    cdef double[:, :, ::1] invariant_y = np.empty_like(dyn_dyp)
    cdef double[:, :, ::1] invariant_z = np.empty_like(dzn_dzp)
    cdef double[:, :, ::1] comp_x, comp_y, comp_z

    comp_x = du3d(cdiv3d(dxn_dxp, J), axis=0)
    comp_y = du3d(cdiv3d(dyn_dxp, J), axis=1)
    comp_z = du3d(cdiv3d(dzn_dxp, J), axis=2)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                invariant_x[ix, iy, iz] = comp_x[ix, iy, iz] + comp_y[ix, iy, iz] + comp_z[ix, iy, iz]

    comp_x = du3d(cdiv3d(dxn_dyp, J), axis=0)
    comp_y = du3d(cdiv3d(dyn_dyp, J), axis=1)
    comp_z = du3d(cdiv3d(dzn_dyp, J), axis=2)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                invariant_y[ix, iy, iz] = comp_x[ix, iy, iz] + comp_y[ix, iy, iz] + comp_z[ix, iy, iz]

    comp_x = du3d(cdiv3d(dxn_dzp, J), axis=0)
    comp_y = du3d(cdiv3d(dyn_dzp, J), axis=1)
    comp_z = du3d(cdiv3d(dzn_dzp, J), axis=2)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                invariant_z[ix, iy, iz] = comp_x[ix, iy, iz] + comp_y[ix, iy, iz] + comp_z[ix, iy, iz]

    return invariant_x, invariant_y, invariant_z


cdef double[:, ::1] cinv2d(double[:, ::1] b):

    cdef Py_ssize_t nx = b.shape[0]
    cdef Py_ssize_t ny = b.shape[1]
    cdef double[:, ::1] out = np.empty_like(b)

    for ix in range(nx):
        for iy in range(ny):
            out[ix, iy] = 1. / b[ix, iy]

    return out


cdef double[:, :, ::1] cinv3d(double[:, :, ::1] b):

    cdef Py_ssize_t nx = b.shape[0]
    cdef Py_ssize_t ny = b.shape[1]
    cdef Py_ssize_t nz = b.shape[2]
    cdef double[:, :, ::1] out = np.empty_like(b)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                out[ix, iy, iz] = 1. / b[ix, iy, iz]

    return out


cdef double[::1] cdiv1d(double[::1] a, double[::1] b):

    cdef Py_ssize_t nx = a.shape[0]
    cdef double[::1] out = np.empty_like(a)

    for ix in range(nx):
        out[ix] = a[ix] / b[ix]

    return out


cdef double[:, ::1] cdiv2d(double[:, ::1] a, double[:, ::1] b):

    cdef Py_ssize_t nx = a.shape[0]
    cdef Py_ssize_t ny = a.shape[1]
    cdef double[:, ::1] out = np.empty_like(a)

    for ix in range(nx):
        for iy in range(ny):
            out[ix, iy] = a[ix, iy] / b[ix, iy]

    return out


cdef double[:, :, ::1] cdiv3d(double[:, :, ::1] a, double[:, :, ::1] b):

    cdef Py_ssize_t nx = a.shape[0]
    cdef Py_ssize_t ny = a.shape[1]
    cdef Py_ssize_t nz = a.shape[2]
    cdef double[:, :, ::1] out = np.empty_like(a)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                out[ix, iy, iz] = a[ix, iy, iz] / b[ix, iy, iz]

    return out


cdef double[:, ::1] _du2d_x(double[:, ::1] v, double dx = 1.):

    cdef Py_ssize_t ix, iy
    cdef double odx = 1. / dx
    cdef Py_ssize_t nx = v.shape[0]
    cdef Py_ssize_t ny = v.shape[1]
    cdef double[:, ::1] dv = np.zeros_like(v)

    for ix in range(5, nx - 5):
        for iy in range(ny):
            dv[ix, iy] = (a11c[1] * (v[ix+1, iy] - v[ix-1, iy]) +
                          a11c[2] * (v[ix+2, iy] - v[ix-2, iy]) +
                          a11c[3] * (v[ix+3, iy] - v[ix-3, iy]) +
                          a11c[4] * (v[ix+4, iy] - v[ix-4, iy]) +
                          a11c[5] * (v[ix+5, iy] - v[ix-5, iy])) * odx

    for ix in range(0, 5):
        for iy in range(ny):
            dv[ix, iy] = (a11d[ix][0] * v[0, iy] +
                          a11d[ix][1] * v[1, iy] +
                          a11d[ix][2] * v[2, iy] +
                          a11d[ix][3] * v[3, iy] +
                          a11d[ix][4] * v[4, iy] +
                          a11d[ix][5] * v[5, iy] +
                          a11d[ix][6] * v[6, iy] +
                          a11d[ix][7] * v[7, iy] +
                          a11d[ix][8] * v[8, iy] +
                          a11d[ix][9] * v[9, iy] +
                          a11d[ix][10] * v[10, iy]) * odx

    for ix in range(nx-1, nx-6, -1):
        for iy in range(ny):
            dv[ix, iy] = - (a11d[nx-ix-1][0] * v[nx-1, iy] +
                            a11d[nx-ix-1][1] * v[nx-2, iy] +
                            a11d[nx-ix-1][2] * v[nx-3, iy] +
                            a11d[nx-ix-1][3] * v[nx-4, iy] +
                            a11d[nx-ix-1][4] * v[nx-5, iy] +
                            a11d[nx-ix-1][5] * v[nx-6, iy] +
                            a11d[nx-ix-1][6] * v[nx-7, iy] +
                            a11d[nx-ix-1][7] * v[nx-8, iy] +
                            a11d[nx-ix-1][8] * v[nx-9, iy] +
                            a11d[nx-ix-1][9] * v[nx-10, iy] +
                            a11d[nx-ix-1][10] * v[nx-11, iy]) * odx

    return dv


cdef double[:, ::1] _du2d_y(double[:, ::1] v, double dy = 1.):

    cdef Py_ssize_t ix, iy
    cdef double ody = 1. / dy
    cdef Py_ssize_t nx = v.shape[0]
    cdef Py_ssize_t ny = v.shape[1]
    cdef double[:, ::1] dv = np.zeros_like(v)

    for ix in range(nx):
        for iy in range(5, ny - 5):
            dv[ix, iy] = (a11c[1] * (v[ix, iy+1] - v[ix, iy-1]) +
                          a11c[2] * (v[ix, iy+2] - v[ix, iy-2]) +
                          a11c[3] * (v[ix, iy+3] - v[ix, iy-3]) +
                          a11c[4] * (v[ix, iy+4] - v[ix, iy-4]) +
                          a11c[5] * (v[ix, iy+5] - v[ix, iy-5])) * ody

    for ix in range(nx):
        for iy in range(0, 5):
            dv[ix, iy] = (a11d[iy][0] * v[ix, 0] +
                          a11d[iy][1] * v[ix, 1] +
                          a11d[iy][2] * v[ix, 2] +
                          a11d[iy][3] * v[ix, 3] +
                          a11d[iy][4] * v[ix, 4] +
                          a11d[iy][5] * v[ix, 5] +
                          a11d[iy][6] * v[ix, 6] +
                          a11d[iy][7] * v[ix, 7] +
                          a11d[iy][8] * v[ix, 8] +
                          a11d[iy][9] * v[ix, 9] +
                          a11d[iy][10] * v[ix, 10]) * ody

    for ix in range(nx):
        for iy in range(ny-1, ny-6, -1):
            dv[ix, iy] = - (a11d[ny-iy-1][0] * v[ix, ny-1] +
                            a11d[ny-iy-1][1] * v[ix, ny-2] +
                            a11d[ny-iy-1][2] * v[ix, ny-3] +
                            a11d[ny-iy-1][3] * v[ix, ny-4] +
                            a11d[ny-iy-1][4] * v[ix, ny-5] +
                            a11d[ny-iy-1][5] * v[ix, ny-6] +
                            a11d[ny-iy-1][6] * v[ix, ny-7] +
                            a11d[ny-iy-1][7] * v[ix, ny-8] +
                            a11d[ny-iy-1][8] * v[ix, ny-9] +
                            a11d[ny-iy-1][9] * v[ix, ny-10] +
                            a11d[ny-iy-1][10] * v[ix, ny-11]) * ody

    return dv


cdef double[:, :, ::1] _du3d_x(double[:, :, ::1] v, double dx = 1.):

    cdef Py_ssize_t ix, iy, iz
    cdef double odx = 1. / dx
    cdef Py_ssize_t nx = v.shape[0]
    cdef Py_ssize_t ny = v.shape[1]
    cdef Py_ssize_t nz = v.shape[2]
    cdef double[:, :, ::1] dv = np.zeros_like(v)

    for ix in range(5, nx - 5):
        for iy in range(ny):
            for iz in range(nz):
                dv[ix, iy, iz] = (a11c[1] * (v[ix+1, iy, iz] - v[ix-1, iy, iz]) +
                                  a11c[2] * (v[ix+2, iy, iz] - v[ix-2, iy, iz]) +
                                  a11c[3] * (v[ix+3, iy, iz] - v[ix-3, iy, iz]) +
                                  a11c[4] * (v[ix+4, iy, iz] - v[ix-4, iy, iz]) +
                                  a11c[5] * (v[ix+5, iy, iz] - v[ix-5, iy, iz])) * odx

    for ix in range(0, 5):
        for iy in range(ny):
            for iz in range(nz):
                dv[ix, iy, iz] = (a11d[ix][0] * v[0, iy, iz] +
                                  a11d[ix][1] * v[1, iy, iz] +
                                  a11d[ix][2] * v[2, iy, iz] +
                                  a11d[ix][3] * v[3, iy, iz] +
                                  a11d[ix][4] * v[4, iy, iz] +
                                  a11d[ix][5] * v[5, iy, iz] +
                                  a11d[ix][6] * v[6, iy, iz] +
                                  a11d[ix][7] * v[7, iy, iz] +
                                  a11d[ix][8] * v[8, iy, iz] +
                                  a11d[ix][9] * v[9, iy, iz] +
                                  a11d[ix][10] * v[10, iy, iz]) * odx

    for ix in range(nx-1, nx-6, -1):
        for iy in range(ny):
            for iz in range(nz):
                dv[ix, iy, iz] = - (a11d[nx-ix-1][0] * v[nx-1, iy, iz] +
                                    a11d[nx-ix-1][1] * v[nx-2, iy, iz] +
                                    a11d[nx-ix-1][2] * v[nx-3, iy, iz] +
                                    a11d[nx-ix-1][3] * v[nx-4, iy, iz] +
                                    a11d[nx-ix-1][4] * v[nx-5, iy, iz] +
                                    a11d[nx-ix-1][5] * v[nx-6, iy, iz] +
                                    a11d[nx-ix-1][6] * v[nx-7, iy, iz] +
                                    a11d[nx-ix-1][7] * v[nx-8, iy, iz] +
                                    a11d[nx-ix-1][8] * v[nx-9, iy, iz] +
                                    a11d[nx-ix-1][9] * v[nx-10, iy, iz] +
                                    a11d[nx-ix-1][10] * v[nx-11, iy, iz]) * odx

    return dv


cdef double[:, :, ::1] _du3d_y(double[:, :, ::1] v, double dy = 1.):

    cdef Py_ssize_t ix, iy, iz
    cdef double ody = 1. / dy
    cdef Py_ssize_t nx = v.shape[0]
    cdef Py_ssize_t ny = v.shape[1]
    cdef Py_ssize_t nz = v.shape[2]
    cdef double[:, :, ::1] dv = np.zeros_like(v)

    for ix in range(nx):
        for iy in range(5, ny - 5):
            for iz in range(nz):
                dv[ix, iy, iz] = (a11c[1] * (v[ix, iy+1, iz] - v[ix, iy-1, iz]) +
                                  a11c[2] * (v[ix, iy+2, iz] - v[ix, iy-2, iz]) +
                                  a11c[3] * (v[ix, iy+3, iz] - v[ix, iy-3, iz]) +
                                  a11c[4] * (v[ix, iy+4, iz] - v[ix, iy-4, iz]) +
                                  a11c[5] * (v[ix, iy+5, iz] - v[ix, iy-5, iz])) * ody

    for ix in range(nx):
        for iy in range(0, 5):
            for iz in range(nz):
                dv[ix, iy, iz] = (a11d[iy][0] * v[ix, 0, iz] +
                                  a11d[iy][1] * v[ix, 1, iz] +
                                  a11d[iy][2] * v[ix, 2, iz] +
                                  a11d[iy][3] * v[ix, 3, iz] +
                                  a11d[iy][4] * v[ix, 4, iz] +
                                  a11d[iy][5] * v[ix, 5, iz] +
                                  a11d[iy][6] * v[ix, 6, iz] +
                                  a11d[iy][7] * v[ix, 7, iz] +
                                  a11d[iy][8] * v[ix, 8, iz] +
                                  a11d[iy][9] * v[ix, 9, iz] +
                                  a11d[iy][10] * v[ix, 10, iz]) * ody

    for ix in range(nx):
        for iy in range(ny-1, ny-6, -1):
            for iz in range(nz):
                dv[ix, iy, iz] = - (a11d[ny-iy-1][0] * v[ix, ny-1, iz] +
                                    a11d[ny-iy-1][1] * v[ix, ny-2, iz] +
                                    a11d[ny-iy-1][2] * v[ix, ny-3, iz] +
                                    a11d[ny-iy-1][3] * v[ix, ny-4, iz] +
                                    a11d[ny-iy-1][4] * v[ix, ny-5, iz] +
                                    a11d[ny-iy-1][5] * v[ix, ny-6, iz] +
                                    a11d[ny-iy-1][6] * v[ix, ny-7, iz] +
                                    a11d[ny-iy-1][7] * v[ix, ny-8, iz] +
                                    a11d[ny-iy-1][8] * v[ix, ny-9, iz] +
                                    a11d[ny-iy-1][9] * v[ix, ny-10, iz] +
                                    a11d[ny-iy-1][10] * v[ix, ny-11, iz]) * ody

    return dv


cdef double[:, :, ::1] _du3d_z(double[:, :, ::1] v, double dz = 1.):

    cdef Py_ssize_t ix, iy, iz
    cdef double odz = 1. / dz
    cdef Py_ssize_t nx = v.shape[0]
    cdef Py_ssize_t ny = v.shape[1]
    cdef Py_ssize_t nz = v.shape[2]
    cdef double[:, :, ::1] dv = np.zeros_like(v)

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(5, nz - 5):
                dv[ix, iy, iz] = (a11c[1] * (v[ix, iy, iz+1] - v[ix, iy, iz-1]) +
                                  a11c[2] * (v[ix, iy, iz+2] - v[ix, iy, iz-2]) +
                                  a11c[3] * (v[ix, iy, iz+3] - v[ix, iy, iz-3]) +
                                  a11c[4] * (v[ix, iy, iz+4] - v[ix, iy, iz-4]) +
                                  a11c[5] * (v[ix, iy, iz+5] - v[ix, iy, iz-5])) * odz

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(0, 5):
                dv[ix, iy, iz] = (a11d[iz][0] * v[ix, iz, 0] +
                                  a11d[iz][1] * v[ix, iz, 1] +
                                  a11d[iz][2] * v[ix, iz, 2] +
                                  a11d[iz][3] * v[ix, iz, 3] +
                                  a11d[iz][4] * v[ix, iz, 4] +
                                  a11d[iz][5] * v[ix, iz, 5] +
                                  a11d[iz][6] * v[ix, iz, 6] +
                                  a11d[iz][7] * v[ix, iz, 7] +
                                  a11d[iz][8] * v[ix, iz, 8] +
                                  a11d[iz][9] * v[ix, iz, 9] +
                                  a11d[iz][10] * v[ix, iz, 10]) * odz

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz-1, nz-6, -1):
                dv[ix, iy, iz] = - (a11d[nz-iz-1][0] * v[ix, iy, nz-1] +
                                    a11d[nz-iz-1][1] * v[ix, iy, nz-2] +
                                    a11d[nz-iz-1][2] * v[ix, iy, nz-3] +
                                    a11d[nz-iz-1][3] * v[ix, iy, nz-4] +
                                    a11d[nz-iz-1][4] * v[ix, iy, nz-5] +
                                    a11d[nz-iz-1][5] * v[ix, iy, nz-6] +
                                    a11d[nz-iz-1][6] * v[ix, iy, nz-7] +
                                    a11d[nz-iz-1][7] * v[ix, iy, nz-8] +
                                    a11d[nz-iz-1][8] * v[ix, iy, nz-9] +
                                    a11d[nz-iz-1][9] * v[ix, iy, nz-10] +
                                    a11d[nz-iz-1][10] * v[ix, iy, nz-11]) * odz
    return dv


cpdef double[::1] chunk_mean(double[::1] array, Py_ssize_t chunks):
    """Compute mean of each chunk of the array."""
    cdef Py_ssize_t i
    cdef Py_ssize_t N = len(array)
    cdef double[::1] mean = np.empty(int(N / chunks))

    for i in range(N):
        mean[i // chunks] += array[i]
        if not (i+1) % chunks:
            mean[i // chunks] /= chunks

    return mean


cpdef nan_check(double[:, ::1] a):

    cdef Py_ssize_t i, j
    cdef int nx = a.shape[0]
    cdef int ny = a.shape[1]
    cdef bint nans = False

    for i in range(nx):
        for j in range(ny):
            if isnan(a[i, j]):
                nans = True
                break
        if nans:
            break
    if nans:
        return i, j
    return None


cpdef double[:, ::1] super_gaussian2d(x, y, Py_ssize_t ix0, Py_ssize_t iy0,
                                      double S0=1,
                                      double kx=2, double ky=2, double k=1,
                                      double Bx=0.1, double By=0.1, double Rx=0):
    r"""Super Gaussian distribution.

   .. math::

        sg = e^{- (\sqrt{(x - x_0)^2 + (y - y_0)^2} + \sqrt{x_r^2 + y_r^2})^{\beta} / (B_x \delta x))^{\beta}}

    Parameters
    ----------
    x, y : numpy.ndarray
        Axis of the grid.
    ix0, iy0 : int
        Indices of the initial position of the pulse :math:`(x_0, y_0)`.
    S0 : float, optional
        Amplitude
    Bx, By : float, optional
        Widths :math:`B_x, B_y, B_z` of the pulse in m. 0.1 by default.
    kx, ky, k: float, optional
        Orders :math:`\beta` of the pulse. Order 2 by default for axis and 1 for global.
    Rx: float, optional
        Radius following x for annular source

    References
    ----------

    .. [1] S. Kang et al. « A Physics-Based Approach to Oversample Multi-Satellite,
        Multi-Species Observations to a Common Grid ». Preprint. Gases/Remote Sensing/Data
        Processing and Information Retrieval, 23 août 2018. https://doi.org/10.5194/amt-2018-253.
    """
    if x.ndim == 2:
        return super_gaussian2dcrv(x, y, ix0, iy0, S0, kx, ky, k, Bx, By, Rx)

    return super_gaussian2dcrt(x, y, ix0, iy0, S0, kx, ky, k, Bx, By, Rx)


@cython.cpow(True)
cdef double[:, ::1] super_gaussian2dcrt(double[::1] x, double[::1] y,
                                        Py_ssize_t ix0, Py_ssize_t iy0,
                                        double S0,
                                        double kx, double ky, double k,
                                        double Bx, double By, double Rx):

    cdef Py_ssize_t ix, iy

    cdef Py_ssize_t nx = x.shape[0]
    cdef Py_ssize_t ny = y.shape[0]

    cdef double wx = (np.log(2)**(1 / (kx * k))) / Bx
    cdef double wy = (np.log(2)**(1 / (ky * k))) / By
    cdef double R = (Rx / wx)**kx

    cdef double xc = x[ix0]
    cdef double yc = y[iy0]

    cdef double[:, ::1] m = np.empty((nx, ny))

    for ix in prange(nx, nogil=True):
        for iy in range(ny):
            m[ix, iy] = S0 * exp(-(fabs((x[ix] - xc) * wx)**kx +
                                   fabs((y[iy] - yc) * wy)**ky - R)**k)

    return m


@cython.cpow(True)
cdef double[:, ::1] super_gaussian2dcrv(double[:, ::1] x, double[:, ::1] y,
                                         Py_ssize_t ix0, Py_ssize_t iy0,
                                         double S0,
                                         double kx, double ky, double k,
                                         double Bx, double By, double Rx):

    cdef Py_ssize_t ix, iy

    cdef Py_ssize_t nx = x.shape[0]
    cdef Py_ssize_t ny = y.shape[1]

    cdef double wx = (np.log(2)**(1 / (kx * k))) / Bx
    cdef double wy = (np.log(2)**(1 / (ky * k))) / By
    cdef double R = (Rx / wx)**kx

    cdef double xc = x[ix0, iy0]
    cdef double yc = y[ix0, iy0]

    cdef double[:, ::1] m = np.empty((nx, ny))

    for ix in prange(nx, nogil=True):
        for iy in range(ny):
            m[ix, iy] = S0 * exp(-(fabs((x[ix, iy] - xc) * wx)**kx +
                                   fabs((y[ix, iy] - yc) * wy)**ky - R)**k)

    return m


cpdef double[:, :, ::1] super_gaussian3d(x, y, z,
                                         Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                         double S0=1.,
                                         double kx=2, double ky=2, double kz=2,
                                         double k=1,
                                         double Bx=0.09, double By=0.09, double Bz=0.09,
                                         double Rx=0):
    """Super Gaussian distribution.

   .. math::

        sg = e^{- (\sqrt{(x - x_0)^2 + (y - y_0)^2} + \sqrt{x_r^2 + y_r^2})^{\beta} / (B_x \delta x))^{\beta}}


    Parameters
    ----------
    x, y, z : numpy.ndarray
        Axis of the grid.
    ix0, iy0, iz0 : int
        Indices of the initial position of the pulse :math:`(x_0, y_0)`.
    S0 : float, optional
        Amplitude
    Bx, By, Bz : float, optional
        Widths :math:`B_x, B_y, B_z` of the pulse in m. 0.1 by default.
    kx, ky, kz, k: float, optional
        Orders :math:`\beta` of the pulse. Order 2 by default for axis and 1 for global.
    Rx: float, optional
        Radius following x for annular source

    References
    ----------

    .. [1] S. Kang et al. « A Physics-Based Approach to Oversample Multi-Satellite,
        Multi-Species Observations to a Common Grid ». Preprint. Gases/Remote Sensing/Data
        Processing and Information Retrieval, 23 août 2018. https://doi.org/10.5194/amt-2018-253.
    """
    if x.ndim == 3:
        return super_gaussian3dcrv(x, y, z, ix0, iy0, iz0, S0, kx, ky, kz, k, Bx, By, Bz, Rx)

    return super_gaussian3dcrt(x, y, z, ix0, iy0, iz0, S0, kx, ky, kz, k, Bx, By, Bz, Rx)


@cython.cpow(True)
cdef double[:, :, ::1] super_gaussian3dcrt(double[::1] x, double[::1] y, double[::1] z,
                                           Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                           double S0,
                                           double kx, double ky, double kz, double k,
                                           double Bx, double By, double Bz, double Rx):

    cdef Py_ssize_t ix, iy, iz

    cdef Py_ssize_t nx = x.shape[0]
    cdef Py_ssize_t ny = y.shape[0]
    cdef Py_ssize_t nz = z.shape[0]

    cdef double wx = (np.log(2)**(1 / (kx * k))) / Bx
    cdef double wy = (np.log(2)**(1 / (ky * k))) / By
    cdef double wz = (np.log(2)**(1 / (kz * k))) / Bz
    cdef double R = (Rx * wx)**kx

    cdef double xc = x[ix0]
    cdef double yc = y[iy0]
    cdef double zc = z[iz0]

    cdef double[:, :, ::1] m = np.empty((nx, ny, nz))

    for ix in prange(nx, nogil=True):
        for iy in range(ny):
            for iz in range(nz):
                m[ix, iy, iz] = S0 * exp(-(fabs((x[ix] - xc) * wx)**kx +
                                           fabs((y[iy] - yc) * wy)**ky +
                                           fabs((z[iz] - zc) * wz)**kz - R)**k)
    return m


@cython.cpow(True)
cdef double[:, :, ::1] super_gaussian3dcrv(double[:, :, ::1] x, double[:, :, ::1] y, double[:, :, ::1] z,
                                           Py_ssize_t ix0, Py_ssize_t iy0, Py_ssize_t iz0,
                                           double S0,
                                           double kx, double ky, double kz, double k,
                                           double Bx, double By, double Bz, double Rx):

    cdef Py_ssize_t ix, iy, iz

    cdef Py_ssize_t nx = x.shape[0]
    cdef Py_ssize_t ny = y.shape[1]
    cdef Py_ssize_t nz = z.shape[2]

    cdef double wx = (np.log(2)**(1 / (kx * k))) / Bx
    cdef double wy = (np.log(2)**(1 / (ky * k))) / By
    cdef double wz = (np.log(2)**(1 / (kz * k))) / Bz
    cdef double R = (Rx * wx)**kx

    cdef double xc = x[ix0, iy0, iz0]
    cdef double yc = y[ix0, iy0, iz0]
    cdef double zc = z[ix0, iy0, iz0]

    cdef double[:, :, ::1] m = np.empty((nx, ny, nz))

    for ix in prange(nx, nogil=True):
        for iy in range(ny):
            for iz in range(nz):
                m[ix, iy, iz] = S0 * exp(-(fabs((x[ix, iy, iz] - xc) * wx)**kx +
                                           fabs((y[ix, iy, iz] - yc) * wy)**ky +
                                           fabs((z[ix, iy, iz] - zc) * wz)**kz - R)**k)

    return m