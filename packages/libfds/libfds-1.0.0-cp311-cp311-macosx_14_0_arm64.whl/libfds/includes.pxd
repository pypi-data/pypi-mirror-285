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


cdef extern from "../libcfds/coefficients.h":
    cdef double[7] rk

cdef extern from "../libcfds/kernels_diffraw.c":
    pass

cdef extern from "../libcfds/kernels_diffsub.c":
    pass

cdef extern from "../libcfds/kernels_diffadd.c":
    pass

cdef extern from "../libcfds/kernels_diffcpy.c":
    pass

cdef extern from "../libcfds/kernels_sf.c":
    pass

cdef extern from "../libcfds/kernels_sc.c":
    pass

cdef extern from "../libcfds/cfields.h":
    pass

cdef extern from "../libcfds/cfields.c":

    void velocity2d(fields2d *, unsigned int)
    void velocity3d(fields3d *, unsigned int)

    void pressure2d(fields2d *)
    void pressure3d(fields3d *)

    void vorticity2d(fields2d *)
    void vorticity3d(fields3d *)

    void residual2d(fields2d *)
    void residual3d(fields3d *)

    void tes_update2d(fields2d *, double *, double)
    void tes_update3d(fields3d *, double *, double)

    void phys2num2d(fields2d *)
    void phys2num3d(fields3d *)

    void num2phys2d(fields2d *)
    void num2phys3d(fields3d *)

    void global_pressure2d(double *, double *, double *, double *, double *, double, unsigned int, unsigned int, unsigned int)
    void global_pressure3d(double *, double *, double *, double *, double *, double *, double, unsigned int, unsigned int, unsigned int, unsigned int)

    ctypedef struct ThreadInfo:
        unsigned int cpu
        unsigned int calls
        unsigned int lock
        unsigned int *glock
        unsigned int *cpus
        unsigned int ncpus
        unsigned int means
        unsigned int cycles
        double *timings

    ctypedef struct domain2d:
        unsigned int ixmin, ixmax, iymin, iymax, size_d
        unsigned int *n
        ThreadInfo thread_info_eul
        ThreadInfo thread_info_vsc
        ThreadInfo thread_info_pup
        ThreadInfo thread_info_rsd
        ThreadInfo thread_info_vup
        ThreadInfo thread_info_cpy
        ThreadInfo thread_info_n2p
        ThreadInfo thread_info_tes

    ctypedef struct domain3d:
        unsigned int ixmin, ixmax, iymin, iymax, izmin, izmax, size_d
        unsigned int *n
        ThreadInfo thread_info_eul
        ThreadInfo thread_info_vsc
        ThreadInfo thread_info_pup
        ThreadInfo thread_info_rsd
        ThreadInfo thread_info_vup
        ThreadInfo thread_info_cpy
        ThreadInfo thread_info_n2p
        ThreadInfo thread_info_tes

    ctypedef struct domain_ax2d:
        unsigned int ixmin, ixmax, iymin, iymax, size_d
        unsigned int *n
        unsigned int sc_flag
        double *fu_gtime
        double *fu_stime
        int dscm, fscm
        ThreadInfo thread_info_du
        ThreadInfo thread_info_lf
        ThreadInfo thread_info_sc
        ThreadInfo thread_info_sg
        ThreadInfo thread_info_fu

    ctypedef struct domain_ax3d:
        unsigned int ixmin, ixmax, iymin, iymax, izmin, izmax, size_d
        unsigned int *n
        unsigned int sc_flag
        double *fu_gtime
        double *fu_stime
        int dscm, fscm
        ThreadInfo thread_info_du
        ThreadInfo thread_info_lf
        ThreadInfo thread_info_sc
        ThreadInfo thread_info_sg
        ThreadInfo thread_info_fu

    ctypedef struct fields2d:
        unsigned int nx, ny, size, dmns_n, dmns_x_n, dmns_y_n
        unsigned int crv, vsc
        domain2d *dmns
        domain_ax2d *dmns_x
        domain_ax2d *dmns_y

        double eul_gtime, vsc_gtime, pup_gtime, vup_gtime, n2p_gtime, tes_gtime, cpy_gtime
        double eul_stime, vsc_stime, pup_stime, vup_stime, n2p_stime, tes_stime, cpy_stime

        unsigned int eul_call, vsc_call, pup_call, vup_call, n2p_call, tes_call, cpy_call
        unsigned int eul_glob, vsc_glob, pup_glob, vup_glob, n2p_glob, tes_glob, cpy_glob
        unsigned int eul_lock, vsc_lock, pup_lock, vup_lock, n2p_lock, tes_lock, cpy_lock, rsd_lock

        double dux_gtime, lfx_gtime, scx_gtime, sgx_gtime, fux_gtime
        double duy_gtime, lfy_gtime, scy_gtime, sgy_gtime, fuy_gtime
        double dux_stime, lfx_stime, scx_stime, sgx_stime, fux_stime
        double duy_stime, lfy_stime, scy_stime, sgy_stime, fuy_stime

        unsigned int dux_glob, lfx_glob, scx_glob, sgx_glob, fux_glob
        unsigned int duy_glob, lfy_glob, scy_glob, sgy_glob, fuy_glob
        unsigned int dux_call, lfx_call, scx_call, sgx_call, fux_call
        unsigned int duy_call, lfy_call, scy_call, sgy_call, fuy_call
        unsigned int dux_lock, lfx_lock, scx_lock, sgx_lock, fux_lock
        unsigned int duy_lock, lfy_lock, scy_lock, sgy_lock, fuy_lock

        double p0, mu0, cppr, cpmcv, Tref, Ssu, SsuTref
        double gm1, gm1_over_c, gm1_over_cpmcv

        double xnu_n, xnu_0
        double rsd
        double *odx
        double *ody
        double *odx_v
        double *ody_v
        double * odxdt
        double * odydt
        double * odxdt_v
        double * odydt_v
        double *odxdtrk
        double *odydtrk
        double *odxdtrk_v
        double *odydtrk_v
        unsigned int *P3x
        unsigned int *P3y
        unsigned int *P5x
        unsigned int *P5y
        unsigned int *P11x
        unsigned int *P11y
        double *r
        double *ru
        double *rv
        double *re
        double *p
        double *Tk
        double *E
        double *Eu
        double *Ev
        double *Ee
        double *F
        double *Fu
        double *Fv
        double *Fe
        double *K
        double *Ku
        double *Kv
        double *Ke
        double *invJ
        double *dx_du
        double *dx_dv
        double *dy_du
        double *dy_dv
        double *tau11
        double *tau22
        double *tau12
        double *wz

    ctypedef struct fields3d:
        unsigned int nx, ny, nz, size, dmns_n, dmns_x_n, dmns_y_n, dmns_z_n
        unsigned int crv, vsc
        domain3d *dmns
        domain_ax3d *dmns_x
        domain_ax3d *dmns_y
        domain_ax3d *dmns_z

        double eul_gtime, vsc_gtime, pup_gtime, vup_gtime, n2p_gtime, tes_gtime, cpy_gtime
        double eul_stime, vsc_stime, pup_stime, vup_stime, n2p_stime, tes_stime, cpy_stime

        unsigned int eul_call, vsc_call, pup_call, vup_call, n2p_call, tes_call, cpy_call
        unsigned int eul_glob, vsc_glob, pup_glob, vup_glob, n2p_glob, tes_glob, cpy_glob
        unsigned int eul_lock, vsc_lock, pup_lock, vup_lock, n2p_lock, tes_lock, cpy_lock, rsd_lock

        double dux_gtime, lfx_gtime, scx_gtime, sgx_gtime, fux_gtime
        double duy_gtime, lfy_gtime, scy_gtime, sgy_gtime, fuy_gtime
        double duz_gtime, lfz_gtime, scz_gtime, sgz_gtime, fuz_gtime

        double dux_stime, lfx_stime, scx_stime, sgx_stime, fux_stime
        double duy_stime, lfy_stime, scy_stime, sgy_stime, fuy_stime
        double duz_stime, lfz_stime, scz_stime, sgz_stime, fuz_stime

        unsigned int dux_glob, lfx_glob, scx_glob, sgx_glob, fux_glob
        unsigned int duy_glob, lfy_glob, scy_glob, sgy_glob, fuy_glob
        unsigned int duz_glob, lfz_glob, scz_glob, sgz_glob, fuz_glob

        unsigned int dux_call, lfx_call, scx_call, sgx_call, fux_call
        unsigned int duy_call, lfy_call, scy_call, sgy_call, fuy_call
        unsigned int duz_call, lfz_call, scz_call, sgz_call, fuz_call

        unsigned int dux_lock, lfx_lock, scx_lock, sgx_lock, fux_lock
        unsigned int duy_lock, lfy_lock, scy_lock, sgy_lock, fuy_lock
        unsigned int duz_lock, lfz_lock, scz_lock, sgz_lock, fuz_lock

        double p0, mu0, cppr, cpmcv, Tref, Ssu, SsuTref
        double gm1, gm1_over_c, gm1_over_cpmcv

        double xnu_n, xnu_0
        double rsd
        double *odx
        double *ody
        double *odz
        double *odx_v
        double *ody_v
        double *odz_v
        double * odxdt
        double * odydt
        double * odzdt
        double * odxdt_v
        double * odydt_v
        double * odzdt_v
        double *odxdtrk
        double *odydtrk
        double *odzdtrk
        double *odxdtrk_v
        double *odydtrk_v
        double *odzdtrk_v
        unsigned int *P3x
        unsigned int *P3y
        unsigned int *P3z
        unsigned int *P5x
        unsigned int *P5y
        unsigned int *P5z
        unsigned int *P11x
        unsigned int *P11y
        unsigned int *P11z
        double *r
        double *ru
        double *rv
        double *rw
        double *re
        double *p
        double *Tk
        double *E
        double *Eu
        double *Ev
        double *Ew
        double *Ee
        double *F
        double *Fu
        double *Fv
        double *Fw
        double *Fe
        double *G
        double *Gu
        double *Gv
        double *Gw
        double *Ge
        double *K
        double *Ku
        double *Kv
        double *Kw
        double *Ke
        double *invJ
        double *dx_du
        double *dx_dv
        double *dx_dw
        double *dy_du
        double *dy_dv
        double *dy_dw
        double *dz_du
        double *dz_dv
        double *dz_dw
        double *tau11
        double *tau22
        double *tau33
        double *tau12
        double *tau13
        double *tau23
        double * wx
        double * wy
        double * wz

cdef extern from "../libcfds/ceulerianfluxes.c":
    void copy2d(fields2d *)
    void copy3d(fields3d *)
    void eulerian_fluxes2d(fields2d *)
    void eulerian_fluxes3d(fields3d *)
    void eulerian_derivatives2d_x(fields2d *)
    void eulerian_derivatives2d_y(fields2d *)
    void eulerian_derivatives3d_x(fields3d *)
    void eulerian_derivatives3d_y(fields3d *)
    void eulerian_derivatives3d_z(fields3d *)
    void eulerian_fluxes2d_init(fields2d *)
    void eulerian_fluxes3d_init(fields3d *)

cdef extern from "../libcfds/cviscousfluxes.c":
    void s11_2d_x(fields2d *)
    void s11_2d_y(fields2d *)
    void s22_2d_x(fields2d *)
    void s22_2d_y(fields2d *)

    void s11_3d_x(fields3d *)
    void s11_3d_y(fields3d *)
    void s11_3d_z(fields3d *)
    void s22_3d_x(fields3d *)
    void s22_3d_y(fields3d *)
    void s22_3d_z(fields3d *)
    void s33_3d_x(fields3d *)
    void s33_3d_y(fields3d *)
    void s33_3d_z(fields3d *)

    void dtk2d_x(fields2d *)
    void dtk2d_y(fields2d *)
    void dtk3d_x(fields3d *)
    void dtk3d_y(fields3d *)
    void dtk3d_z(fields3d *)

    void viscous_fluxes2d(fields2d *)
    void viscous_fluxes3d(fields3d *)
    void vfluxes_integration2d_x(fields2d *)
    void vfluxes_integration2d_y(fields2d *)
    void vfluxes_integration3d_x(fields3d *)
    void vfluxes_integration3d_y(fields3d *)
    void vfluxes_integration3d_z(fields3d *)
    void viscous_fluxes2d_init(fields2d *)
    void viscous_fluxes3d_init(fields3d *)

cdef extern from "../libcfds/cfilters.c":
    void apply_filter2d_x(fields2d *fld)
    void apply_filter2d_y(fields2d *fld)
    void apply_capture2d_x(fields2d *fld)
    void apply_capture2d_y(fields2d *fld)
    void apply_filter3d_x(fields3d *fld)
    void apply_filter3d_y(fields3d *fld)
    void apply_filter3d_z(fields3d *fld)
    void apply_capture3d_x(fields3d *fld)
    void apply_capture3d_y(fields3d *fld)
    void apply_capture3d_z(fields3d *fld)
    void selective_filter2d_x(fields2d *fld)
    void selective_filter2d_y(fields2d *fld)
    void selective_filter3d_x(fields3d *fld)
    void selective_filter3d_y(fields3d *fld)
    void selective_filter3d_z(fields3d *fld)
    void laplacian_filter2d_x(fields2d *fld)
    void laplacian_filter2d_y(fields2d *fld)
    void laplacian_filter3d_x(fields3d *fld)
    void laplacian_filter3d_y(fields3d *fld)
    void laplacian_filter3d_z(fields3d *fld)
    void sigma2d_x(fields2d *fld)
    void sigma2d_y(fields2d *fld)
    void sigma3d_x(fields3d *fld)
    void sigma3d_y(fields3d *fld)
    void sigma3d_z(fields3d *fld)
    void shock_capture2d_x(fields2d *fld)
    void shock_capture2d_y(fields2d *fld)
    void shock_capture3d_x(fields3d *fld)
    void shock_capture3d_y(fields3d *fld)
    void shock_capture3d_z(fields3d *fld)
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