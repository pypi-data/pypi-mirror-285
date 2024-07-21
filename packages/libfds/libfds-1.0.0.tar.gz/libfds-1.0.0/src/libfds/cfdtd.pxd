# -*- coding: utf-8 -*-
#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False
#cython: cdivision=True
#
# Copyright © 2016-2023 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
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
FDTD solver

@author: Cyril Desjouy
"""

import numpy as np
cimport numpy as np
cimport cython
from libfds.includes cimport fields2d, fields3d, ThreadInfo
from libfds.includes cimport domain2d, domain3d, domain_ax2d, domain_ax3d


ctypedef np.npy_int8 INT8

cdef double[::1] get_timings(ThreadInfo *TI)
cdef void set_thread_infos(ThreadInfo *TI, unsigned int *glock,
                           unsigned int lock=?, unsigned int means=?)

@cython.final
cdef class CpuSetter:
    cdef readonly Py_ssize_t cpu
    cdef bint locked
    cdef Py_ssize_t _idx
    cdef double _time
    cdef readonly double[::1] _history


@cython.final
cdef class Face2d:
    cdef cFdtd2d fld
    cdef CpuSetter A_setter
    cdef str tag
    cdef Py_ssize_t ixmin, ixmax, iymin, iymax
    cdef Py_ssize_t axis, normal
    cdef double[:, ::1] profile
    cdef double[::1] evolution
    cdef double e, rho0

    cdef void apply_bc(self, Py_ssize_t it)
    cdef void _apply_V(self, Py_ssize_t it)
    cdef void _apply_W(self)
    cdef void _apply_A(self, Py_ssize_t cpu)


@cython.final
cdef class Face3d:
    cdef cFdtd3d fld
    cdef CpuSetter A_setter
    cdef str tag
    cdef Py_ssize_t ixmin, ixmax, iymin, iymax, izmin, izmax
    cdef Py_ssize_t axis, normal
    cdef double[:, :, ::1] profile
    cdef double[::1] evolution
    cdef double e, rho0

    cdef void apply_bc(self, Py_ssize_t it)
    cdef void _apply_V(self, Py_ssize_t it)
    cdef void _apply_W(self)
    cdef void _apply_A(self, Py_ssize_t cpu)


@cython.final
cdef class Monopole2d:

    cdef readonly double[:, ::1] profile
    cdef readonly double[::1] evolution


@cython.final
cdef class Monopole3d:

    cdef readonly double[:, :, ::1] profile
    cdef readonly double[::1] evolution


@cython.final
cdef class cFdtd2d:
    # inputs
    cdef msh, cfg, ics

    # vars
    cdef readonly double p0
    cdef readonly double[:, ::1] Tk, p, r, ru, rv, re, wz
    cdef readonly double[:, ::1] tau11, tau22, tau12
    cdef double[:, ::1] E, Eu, Ev, Ee
    cdef double[:, ::1] F, Fu, Fv, Fe
    cdef double[:, ::1] K, Ku, Kv, Ke

    # Flags
    cdef Py_ssize_t vsc, crv, vrt, cpt, flt

    # cvars / computation domains
    cdef Py_ssize_t nx, ny, nsize
    cdef list bc
    cdef fields2d vars
    cdef unsigned int dmns_n, dmns_x_n, dmns_y_n
    cdef domain2d *dmns
    cdef domain_ax2d *dmns_x
    cdef domain_ax2d *dmns_y

    # mesh constants
    cdef Py_ssize_t flag_x, flag_y
    cdef unsigned int[::1] P3x, P3y, P5x, P5y, P11x, P11y
    cdef double[:, ::1] invJ, dx_du, dx_dv, dy_du, dy_dv

    # Steps
    cdef double dt, odx, ody, odxdt, odydt, odxdtrk, odydtrk, dtrk
    cdef double[::1] odx_v, ody_v, odxdt_v, odydt_v, odxdtrk_v, odydtrk_v

    # bz
    cdef Py_ssize_t bz_n
    cdef double bz_forder
    cdef double[:, ::1] sigma

    # Source parameters
    cdef list src
    cdef Py_ssize_t src_size

    # Methods : Public API
    cpdef void efluxes_integrate(self) noexcept
    cpdef void vfluxes_integrate(self) noexcept
    cpdef void sf_apply(self) noexcept
    cpdef void sc_apply(self) noexcept
    cpdef void vrt_update(self) noexcept
    cpdef double residual(self) noexcept
    cpdef void subdomains_show_c(self) noexcept
    cpdef void subdomains_show_x(self) noexcept
    cpdef void subdomains_show_y(self) noexcept
    cpdef void log_ns(self) noexcept

    # Methods : Grid and domain initializations
    cdef void grid_init(self) noexcept
    cdef void init_spacial_steps(self) noexcept
    cdef void bc_init(self) noexcept
    cdef void subdomains_init(self) noexcept

    # Methods : Fields and other vars initializations
    cdef void fields_init(self) noexcept
    cdef void fields_init_old(self) noexcept
    cdef void fields_init_new(self) noexcept
    cdef void opt_init(self) noexcept
    cdef void vars_init(self) noexcept
    cdef void cvars_init(self) noexcept
    cdef void buffer_init(self) noexcept

    # Methods : Sources initialization
    cdef void ics_init(self) noexcept
    cdef void tes_init(self) noexcept
    cdef void tes_update(self) noexcept
    cdef void zero_obstacles(self) noexcept

    # Methods : update
    cdef void rk_steps_update(self, double rk) noexcept
    cdef void p_update(self) noexcept
    cdef void v_update(self) noexcept
    cdef void fx_update(self) noexcept
    cdef void fy_update(self) noexcept
    cdef void cx_update(self) noexcept
    cdef void cy_update(self) noexcept
    cdef void phys2num(self) noexcept
    cdef void num2phys(self) noexcept
    cdef void copy(self) noexcept
    cdef void cout(self) noexcept

    # Solver stuff
    cdef void efluxes_update(self) noexcept
    cdef void vfluxes_update(self) noexcept
    cdef void efluxes_integration_x(self) noexcept
    cdef void efluxes_integration_y(self) noexcept
    cdef void vfluxes_integration_x(self) noexcept
    cdef void vfluxes_integration_y(self) noexcept
    cdef void _sf_x(self) noexcept
    cdef void _sf_y(self) noexcept
    cdef void _lf_x(self) noexcept
    cdef void _lf_y(self) noexcept
    cdef void _sc_x(self) noexcept
    cdef void _sc_y(self) noexcept
    cdef void _sg_x(self) noexcept
    cdef void _sg_y(self) noexcept
    cdef void _dtk(self) noexcept
    cdef void _Sxx(self) noexcept


@cython.final
cdef class cFdtd3d:
    # inputs
    cdef msh, cfg, ics

    # vars
    cdef readonly double p0
    cdef readonly double[:, :, ::1] Tk, p, r, ru, rv, rw, re, wx, wy, wz
    cdef readonly double[:, :, ::1] tau11, tau22, tau33, tau12, tau13, tau23
    cdef double[:, :, ::1] E, Eu, Ev, Ew, Ee
    cdef double[:, :, ::1] F, Fu, Fv, Fw, Fe
    cdef double[:, :, ::1] G, Gu, Gv, Gw, Ge
    cdef double[:, :, ::1] K, Ku, Kv, Kw, Ke

    # Flags
    cdef Py_ssize_t vsc, crv, vrt, cpt, flt

    # cvars / computation domains
    cdef Py_ssize_t nx, ny, nz, nsize
    cdef list bc
    cdef fields3d vars
    cdef unsigned int dmns_n, dmns_x_n, dmns_y_n, dmns_z_n
    cdef domain3d *dmns
    cdef domain_ax3d *dmns_x
    cdef domain_ax3d *dmns_y
    cdef domain_ax3d *dmns_z

    # mesh constants
    cdef Py_ssize_t flag_x, flag_y, flag_z
    cdef unsigned int[::1] P3x, P3y, P3z, P5x, P5y, P5z, P11x, P11y, P11z
    cdef double[:, :, ::1] invJ, dx_du, dx_dv, dx_dw, dy_du, dy_dv, dy_dw, dz_du, dz_dv, dz_dw

    # Steps
    cdef double dt, odx, ody, odz, odxdt, odydt, odzdt, odxdtrk, odydtrk, odzdtrk, dtrk
    cdef double[::1] odx_v, ody_v, odz_v, odxdt_v, odydt_v, odzdt_v, odxdtrk_v, odydtrk_v, odzdtrk_v

    # bz
    cdef Py_ssize_t bz_n
    cdef double bz_forder
    cdef double[:, :, ::1] sigma

    # Sources parameters
    cdef list src
    cdef Py_ssize_t src_size

    # Methods : Public API
    cpdef void efluxes_integrate(self) noexcept
    cpdef void vfluxes_integrate(self) noexcept
    cpdef void sf_apply(self) noexcept
    cpdef void sc_apply(self) noexcept
    cpdef void vrt_update(self) noexcept
    cpdef double residual(self) noexcept
    cpdef void subdomains_show_c(self) noexcept
    cpdef void subdomains_show_x(self) noexcept
    cpdef void subdomains_show_y(self) noexcept
    cpdef void subdomains_show_z(self) noexcept
    cpdef void log_ns(self) noexcept

    # Methods : Grid and domain initializations
    cdef void grid_init(self) noexcept
    cdef void init_spacial_steps(self) noexcept
    cdef void bc_init(self) noexcept
    cdef void subdomains_init(self) noexcept

    # Methods : Fields and other vars initializations
    cdef void fields_init(self) noexcept
    cdef void fields_init_old(self) noexcept
    cdef void fields_init_new(self) noexcept
    cdef void opt_init(self) noexcept
    cdef void vars_init(self) noexcept
    cdef void cvars_init(self) noexcept
    cdef void buffer_init(self) noexcept

    # Methods : Sources initialization
    cdef void ics_init(self) noexcept
    cdef void tes_init(self) noexcept
    cdef void tes_update(self) noexcept
    cdef void zero_obstacles(self) noexcept

    # Methods : update
    cdef void rk_steps_update(self, double rk) noexcept
    cdef void p_update(self) noexcept
    cdef void fx_update(self) noexcept
    cdef void fy_update(self) noexcept
    cdef void fz_update(self) noexcept
    cdef void cx_update(self) noexcept
    cdef void cy_update(self) noexcept
    cdef void cz_update(self) noexcept
    cdef void v_update(self) noexcept
    cdef void phys2num(self) noexcept
    cdef void num2phys(self) noexcept
    cdef void copy(self) noexcept
    cdef void cout(self) noexcept

    # Solver stuff
    cdef void efluxes_update(self) noexcept
    cdef void vfluxes_update(self) noexcept
    cdef void efluxes_integration(self) noexcept
    cdef void vfluxes_integration(self) noexcept
    cdef void _sf_x(self) noexcept
    cdef void _sf_y(self) noexcept
    cdef void _sf_z(self) noexcept
    cdef void _lf_x(self) noexcept
    cdef void _lf_y(self) noexcept
    cdef void _lf_z(self) noexcept
    cdef void _sc_x(self) noexcept
    cdef void _sc_y(self) noexcept
    cdef void _sc_z(self) noexcept
    cdef void _sg_x(self) noexcept
    cdef void _sg_y(self) noexcept
    cdef void _sg_z(self) noexcept
    cdef void _dtk(self) noexcept
    cdef void _Sxx(self) noexcept


cpdef void p_update2d(double[:, ::1] p, double[:, ::1] r,
                     double[:, ::1] ru, double[:, ::1] rv, double[:, ::1] re,
                     double gamma, Py_ssize_t cpu=*)


cpdef void p_update3d(double[:, :, ::1] p, double[:, :, ::1] r,
                     double[:, :, ::1] ru, double[:, :, ::1] rv,
                     double[:, :, ::1] rw, double[:, :, ::1] re,
                     double gamma, Py_ssize_t cpu=*)