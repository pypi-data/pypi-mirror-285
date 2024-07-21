# -*- coding: utf-8 -*-
#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False
#cython: cdivision=True
#cython: initializedcheck=False
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

TODO :

    * 7 points Selective Filter ?
    * RG : filters rho, rhou, rhov, rhow and p ! But not rhoe.
    * Compare ShockCapture with RG version
    * If a mean flow is taken into account, SelectiveFilter must be done on variables without this flow.
    * clean up sc section of show_domain that does not reflect reality

@author: Cyril Desjouy
"""

cimport cython
import numpy as _np
cimport numpy as _np
import os
from itertools import compress
from time import perf_counter as pc
from cython.parallel cimport prange

from rich.table import Table as _Table
import rich.box as _box
from rich.console import Console
console = Console()

from libc.math cimport abs, sin, M_PI
from libc.stdlib cimport malloc, free
from libc.float cimport DBL_MAX

from libfds.cmaths import super_gaussian2d, super_gaussian3d
from libfds.cmaths cimport odu, mult, mult_inplace, argmin1d, cinv2d, cinv3d
from libfds.includes cimport domain2d, domain3d, domain_ax2d, domain_ax3d, rk
from libfds.includes cimport eulerian_fluxes2d_init, eulerian_fluxes3d_init
from libfds.includes cimport viscous_fluxes2d_init, viscous_fluxes3d_init
from libfds.includes cimport eulerian_derivatives2d_x, eulerian_derivatives2d_y
from libfds.includes cimport eulerian_derivatives3d_x, eulerian_derivatives3d_y, eulerian_derivatives3d_z
from libfds.includes cimport eulerian_fluxes2d, eulerian_fluxes3d
from libfds.includes cimport viscous_fluxes2d, viscous_fluxes3d
from libfds.includes cimport global_pressure2d, global_pressure3d, tes_update2d, tes_update3d
from libfds.includes cimport pressure2d, pressure3d, velocity2d, velocity3d, vorticity2d, vorticity3d
from libfds.includes cimport copy2d, copy3d, residual2d, residual3d
from libfds.includes cimport phys2num2d, num2phys2d, phys2num3d, num2phys3d
from libfds.includes cimport s11_2d_x,s11_2d_y, s22_2d_x, s22_2d_y
from libfds.includes cimport s11_3d_x, s11_3d_y, s11_3d_z, s22_3d_x, s22_3d_y, s22_3d_z, s33_3d_x, s33_3d_y, s33_3d_z
from libfds.includes cimport apply_filter2d_x, apply_filter2d_y, apply_filter3d_x, apply_filter3d_y, apply_filter3d_z
from libfds.includes cimport apply_capture2d_x, apply_capture2d_y, apply_capture3d_x, apply_capture3d_y, apply_capture3d_z
from libfds.includes cimport vfluxes_integration2d_x, vfluxes_integration2d_y
from libfds.includes cimport vfluxes_integration3d_x, vfluxes_integration3d_y, vfluxes_integration3d_z
from libfds.includes cimport selective_filter2d_x, selective_filter2d_y
from libfds.includes cimport selective_filter3d_x, selective_filter3d_y, selective_filter3d_z
from libfds.includes cimport laplacian_filter2d_x, laplacian_filter2d_y
from libfds.includes cimport laplacian_filter3d_x, laplacian_filter3d_y, laplacian_filter3d_z
from libfds.includes cimport sigma2d_x, sigma2d_y, sigma3d_x, sigma3d_y, sigma3d_z
from libfds.includes cimport shock_capture2d_x, shock_capture2d_y, shock_capture3d_x, shock_capture3d_y, shock_capture3d_z
from libfds.includes cimport dtk2d_x, dtk2d_y, dtk3d_x, dtk3d_y, dtk3d_z



cdef:
    unsigned[::1] cpus = _np.array([1, ] + list(range(2, os.cpu_count(), 2)), dtype=_np.uint32)
    Py_ssize_t opt_mean = 5
    Py_ssize_t cpu_counts = len(cpus)
    Py_ssize_t opt_cycles = len(cpus) * opt_mean
    str true = '[bold bright_green]⦿'
    str false = '[bold bright_red]⦿'
    str locked = '[bolt bright_green]L'   # ':locked-emoji:'
    str unlocked = '[bolt bright_magenta]U'


def convert(arr, limit=10e10):
    return '[dim italic orange1]' + '\n'.join([f'{item:.2e}' if item < limit else '' for item in _np.array(arr)])


cdef double[::1] get_timings(ThreadInfo *TI):
    cdef Py_ssize_t i
    cdef timings = _np.zeros(TI.ncpus)

    for i in range(TI.ncpus):
        timings[i] = TI.timings[i]

    return timings


cdef void set_thread_infos(ThreadInfo *TI, unsigned int *glock,
                           unsigned int lock=0, unsigned int means=2):
    """Set thread info of subdomains."""
    cdef int i

    TI.cpu = 1
    TI.calls = 0
    TI.lock = lock
    TI.glock = glock
    TI.timings = <double *> malloc(len(cpus) * sizeof(double))
    for i in range(len(cpus)):
        TI.timings[i] = DBL_MAX
    TI.cpus = &cpus[0]
    TI.ncpus = len(cpus)
    TI.means = means
    TI.cycles = len(cpus) * means


@cython.final
cdef class CpuSetter:

    def __init__(self, bint mp):

        self.cpu = 1
        if mp:
            self.locked = False
        else:
            self.locked = True
        self._time = 0.
        self._idx = 0
        self._history = _np.zeros(cpu_counts, dtype=float)

    def __enter__(self):
        if not self.locked:
            self.cpu = cpus[(self._idx) // opt_mean]
            if self.cpu == cpus[3] and self._history[2] > self._history[0]:
                self.cpu = 1
                self.locked = True
            self._time = pc()
        return self

    def __exit__(self, *_):

        cdef Py_ssize_t idx

        if not self.locked:
            if self._idx < opt_cycles:
                self._history[self._idx // opt_mean] += pc() - self._time
                self._idx += 1
            if self._idx >= opt_cycles:
                idx = argmin1d(self._history)
                self.cpu = cpus[idx]
                self.locked = True

    def __str__(self):
        return f'CPU: {self.cpu} / locked: {self.locked}'

    def __repr__(self):
        return self.__str__()


@cython.final
cdef class Face2d:

    def __cinit__(self, cFdtd2d fld, face):

        self.fld = fld
        self.tag = face.bc
        self.normal = face.normal
        self.axis = face.axis
        self.rho0 = self.fld.cfg.tp.rho0
        self.e = self.fld.cfg.tp.p0 / (self.fld.cfg.tp.gamma - 1.)

        self.A_setter = CpuSetter(mp=True)

        if self.tag == 'A':
            if face.normal == 1:
                cd = [(c[0], c[1] + self.fld.bz_n - 1) if face.axis == i else c for i, c in enumerate(face.cn)]
            elif face.normal == -1:
                cd = [(c[0] - self.fld.bz_n + 1, c[1]) if face.axis == i else c for i, c in enumerate(face.cn)]
            (self.ixmin, self.ixmax), (self.iymin, self.iymax) = cd

        else:
            (self.ixmin, self.ixmax), (self.iymin, self.iymax) = face.cn

        if self.tag == 'V' and face.source_profile == 'sine':

            pn = _np.zeros([max(s, 1) for s in face.size])
            n = 2

            for ix0, ix in enumerate(face.rn[0]):
                for iy0, iy in enumerate(face.rn[1]):

                    sn = tuple([face.cn[i][0] if i == face.axis else face.sn[i] for i in range(2)])
                    ax = self.fld.msh.paxis[face.not_axis[0]]
                    L1 = ax[sn][len(ax[sn]) - 1] - ax[sn][0]

                    pn[ix0, iy0] = sin(2 * M_PI * (ax[ix, iy] - ax[sn][0]) / (n * L1))

            self.profile = pn.copy()
            self.evolution = face.source_evolution

    cdef void apply_bc(self, Py_ssize_t it):

        if self.tag == 'W':
            self._apply_W()

        elif self.tag == 'A':
            with self.A_setter as setter:
                self._apply_A(setter.cpu)

        elif self.tag == 'V':
            self._apply_V(it)

    cdef void _apply_W(self):

        cdef Py_ssize_t ix, iy

        for ix in range(self.ixmin, self.ixmax + 1):
            for iy in range(self.iymin, self.iymax + 1):
                self.fld.ru[ix, iy] = 0
                self.fld.rv[ix, iy] = 0

    cdef void _apply_A(self, Py_ssize_t cpu):

        cdef Py_ssize_t ix, iy

        if cpu > 1:
            for ix in prange(self.ixmin, self.ixmax + 1, nogil=True, num_threads=cpu):
                for iy in range(self.iymin, self.iymax + 1):
                    self.fld.r[ix, iy] -= self.fld.sigma[ix, iy] * (self.fld.r[ix, iy] - self.rho0)
                    self.fld.ru[ix, iy] -= self.fld.sigma[ix, iy] * self.fld.ru[ix, iy]
                    self.fld.rv[ix, iy] -= self.fld.sigma[ix, iy] * self.fld.rv[ix, iy]
                    self.fld.re[ix, iy] -= self.fld.sigma[ix, iy] * (self.fld.re[ix, iy] - self.e)
        else:
            for ix in range(self.ixmin, self.ixmax + 1):
                for iy in range(self.iymin, self.iymax + 1):
                    self.fld.r[ix, iy] -= self.fld.sigma[ix, iy] * (self.fld.r[ix, iy] - self.rho0)
                    self.fld.ru[ix, iy] -= self.fld.sigma[ix, iy] * self.fld.ru[ix, iy]
                    self.fld.rv[ix, iy] -= self.fld.sigma[ix, iy] * self.fld.rv[ix, iy]
                    self.fld.re[ix, iy] -= self.fld.sigma[ix, iy] * (self.fld.re[ix, iy] - self.e)

    cdef void _apply_V(self, Py_ssize_t it):

        cdef Py_ssize_t ix, iy
        cdef double u, v, prof

        if self.axis == 0:
            u = self.evolution[it]
            v = 0
        else:
            u = 0
            v = self.evolution[it]

        for ix in range(self.ixmin, self.ixmax + 1):
            for iy in range(self.iymin, self.iymax + 1):
                prof = self.profile[ix - self.ixmin, iy - self.iymin]
                self.fld.ru[ix, iy] = u * self.fld.r[ix, iy] * prof
                self.fld.rv[ix, iy] = v * self.fld.r[ix, iy] * prof


@cython.final
cdef class Face3d:

    def __cinit__(self, cFdtd3d fld, face):

        self.fld = fld
        self.tag = face.bc
        self.normal = face.normal
        self.axis = face.axis
        self.rho0 = self.fld.cfg.tp.rho0
        self.e = self.fld.cfg.tp.p0 / (self.fld.cfg.tp.gamma - 1.)

        self.A_setter = CpuSetter(mp=True)

        if self.tag == 'A':
            if face.normal == 1:
                cd = [(c[0], c[1] + self.fld.bz_n - 1) if face.axis == i else c for i, c in enumerate(face.cn)]
            elif face.normal == -1:
                cd = [(c[0] - self.fld.bz_n + 1, c[1]) if face.axis == i else c for i, c in enumerate(face.cn)]
            (self.ixmin, self.ixmax), (self.iymin, self.iymax), (self.izmin, self.izmax) = cd
        else:
            (self.ixmin, self.ixmax), (self.iymin, self.iymax), (self.izmin, self.izmax) = face.cn

        if self.tag == 'V':
            pn = _np.zeros([max(s, 1) for s in face.size])
            n = 2

            for ix0, ix in enumerate(self.rn[0]):
                for iy0, iy in enumerate(self.rn[1]):
                    for iz0, iz in enumerate(self.rn[2]):

                        c = (ix, iy, iz)
                        x1 = self.fld.msh.paxis[face.not_axis[0]]
                        x2 = self.fld.msh.paxis[face.not_axis[1]]
                        s1 = tuple([c if i in [self.axis, face.not_axis[1]] else self.sn[i] for i, c in enumerate(c)])
                        s2 = tuple([c if i in [self.axis, face.not_axis[0]] else self.sn[i] for i, c in enumerate(c)])
                        L1 = x1[s1][len(x1[s1]) - 1] - x1[s1][0]
                        L2 = x2[s2][len(x2[s2]) - 1] - x2[s2][0]

                        pn[ix0, iy0, iz0] = (sin(2 * M_PI * (x1[ix, iy, iz] - x1[s1][0]) / (n * L1)) *
                                                  sin(2 * M_PI * (x2[ix, iy, iz] - x2[s2][0]) / (n * L2)))

            self.profile = pn.copy()
            self.evolution = face.source_evolution

    cdef void apply_bc(self, Py_ssize_t it):

        if self.tag == 'W':
            self._apply_W()

        elif self.tag == 'A':
            with self.A_setter as setter:
                self._apply_A(setter.cpu)

        elif self.tag == 'V':
            self._apply_V(it)

    cdef void _apply_W(self):

        cdef Py_ssize_t ix, iy, iz

        for ix in range(self.ixmin, self.ixmax + 1):
            for iy in range(self.iymin, self.iymax + 1):
                for iz in range(self.izmin, self.izmax + 1):
                    self.fld.ru[ix, iy, iz] = 0
                    self.fld.rv[ix, iy, iz] = 0
                    self.fld.rw[ix, iy, iz] = 0

    cdef void _apply_A(self, Py_ssize_t cpu):

        cdef Py_ssize_t ix, iy, iz

        if cpu > 1:
            for ix in prange(self.ixmin, self.ixmax + 1, nogil=True, num_threads=cpu):
                for iy in range(self.iymin, self.iymax + 1):
                    for iz in range(self.iymin, self.izmax + 1):
                        self.fld.r[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * (self.fld.r[ix, iy, iz] - self.rho0)
                        self.fld.ru[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.ru[ix, iy, iz]
                        self.fld.rv[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.rv[ix, iy, iz]
                        self.fld.rw[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.rw[ix, iy, iz]
                        self.fld.re[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * (self.fld.re[ix, iy, iz] - self.e)
        else:
            for ix in range(self.ixmin, self.ixmax + 1):
                for iy in range(self.iymin, self.iymax + 1):
                    for iz in range(self.iymin, self.izmax + 1):
                        self.fld.r[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * (self.fld.r[ix, iy, iz] - self.rho0)
                        self.fld.ru[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.ru[ix, iy, iz]
                        self.fld.rv[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.rv[ix, iy, iz]
                        self.fld.rw[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * self.fld.rw[ix, iy, iz]
                        self.fld.re[ix, iy, iz] -= self.fld.sigma[ix, iy, iz] * (self.fld.re[ix, iy, iz] - self.e)

    cdef void _apply_V(self, Py_ssize_t it):

        cdef Py_ssize_t ix, iy, iz
        cdef double u, v, w, prof

        if self.axis == 0:
            u = self.evolution[it]
            v, w = 0, 0
        elif self.axis == 1:
            v = self.evolution[it]
            u, w = 0, 0
        else:
            w = self.evolution[it]
            u, v = 0, 0

        for ix in range(self.ixmin, self.ixmax + 1):
            for iy in range(self.iymin, self.iymax + 1):
                for iz in range(self.izmin, self.izmax + 1):
                    prof = self.profile[ix - self.ixmin, iy - self.iymin, iz - self.izmin]
                    self.fld.ru[ix, iy, iz] = u * self.fld.r[ix, iy, iz] * prof
                    self.fld.rv[ix, iy, iz] = v * self.fld.r[ix, iy, iz] * prof
                    self.fld.rw[ix, iy, iz] = w * self.fld.r[ix, iy, iz] * prof


@cython.final
cdef class Monopole2d:

    def __cinit__(self, double[:, ::1] profile, double[::1] evolution):

        self.profile = profile
        self.evolution = evolution


@cython.final
cdef class Monopole3d:

    def __cinit__(self, double[:, :, ::1] profile, double[::1] evolution):

        self.profile = profile
        self.evolution = evolution


cpdef cFdtd(cfg, msh, ics):
    """FTDT solver.

    Parameters
    ----------
    cfg: nsfds3.solver.CfgSetup object
        Configuration of the solver
    msh: nsfds3.cpgrid.CartesianGrid or nsfds3.cpgrid.CurvilinearGrid
        Configuration of the solver
    ics: nsfds3.solver.InitialConditions
        Initial Conditions
    """
    if len(msh.shape) == 2:
        return cFdtd2d(cfg, msh, ics)
    return cFdtd3d(cfg, msh, ics)


@cython.final
cdef class cFdtd2d:

    def __init__(self, cfg, msh, ics):

        self.msh = msh
        self.cfg = cfg
        self.ics = ics

        self.p0 = cfg.tp.p0

        self.cpt = int(self.cfg.sol.cpt)
        self.flt = int(self.cfg.sol.flt)
        self.vsc = int(self.cfg.sol.vsc)
        self.vrt = int(self.cfg.sol.vrt)

        # Computational domain initialization
        self.grid_init()        # t = 0
        self.bc_init()          # t = 0
        self.opt_init()
        self.subdomains_init()  # t = 0.5

        # Variable initialization
        self.fields_init()      # t = 0.7
        self.tes_init()         # t = 0.2
        self.vars_init()        # t = 0.4
        self.cvars_init()       # t = ?
        self.buffer_init()      # t = 0.1

        eulerian_fluxes2d_init(&self.vars)
        viscous_fluxes2d_init(&self.vars)

    cdef void grid_init(self) noexcept:
        """Initialize grid parameters.

        Note
        ----
        Cartesian : crv == 0
        Curvilinear : crv == 1

        """
        self.dt = self.cfg.dt
        self.nx, self.ny = self.msh.shape
        self.nsize = self.nx * self.ny
        self.init_spacial_steps()

        self.crv = 0 if self.msh.mesh_type.lower() == "cartesian" else 1

        if self.crv == 1:
            self.invJ = cinv2d(self.msh.J)
            self.dx_du = self.msh.dx_du
            self.dx_dv = self.msh.dx_dv
            self.dy_du = self.msh.dy_du
            self.dy_dv = self.msh.dy_dv
        else:
            self.invJ = _np.zeros((0, ) * len(self.msh.shape))
            self.dx_du = _np.zeros((0, ) * len(self.msh.shape))
            self.dx_dv = _np.zeros((0, ) * len(self.msh.shape))
            self.dy_du = _np.zeros((0, ) * len(self.msh.shape))
            self.dy_dv = _np.zeros((0, ) * len(self.msh.shape))


        # Buffer zone
        self.bz_n = self.msh.bz_n
        self.bz_forder = self.msh.bz_filter_order

    cdef void init_spacial_steps(self) noexcept:

        self.flag_x = 0 if self.msh.flag_x == "s" else 1
        self.flag_y = 0 if self.msh.flag_y == "s" else 1

        self.dtrk = 0

        self.odx = 1. / self.msh.dx
        self.ody = 1. / self.msh.dy

        self.odxdt = self.odx * self.dt
        self.odydt = self.ody * self.dt

        self.odxdtrk = 0.
        self.odydtrk = 0.

        if self.flag_x == 1:
            self.odx_v = odu(self.msh.x)
            self.odxdt_v = mult(self.odx_v, self.dt)
            self.odxdtrk_v = _np.zeros_like(self.msh.x)
        else:
            self.odx_v = _np.zeros(0)
            self.odxdt_v = _np.zeros(0)
            self.odxdtrk_v = _np.zeros(0)

        if self.flag_y == 1:
            self.ody_v = odu(self.msh.y)
            self.odydt_v = mult(self.ody_v, self.dt)
            self.odydtrk_v = _np.zeros_like(self.msh.y)
        else:
            self.ody_v = _np.zeros(0)
            self.odydt_v = _np.zeros(0)
            self.odydtrk_v = _np.zeros(0)

    cdef void bc_init(self) noexcept:

        # Periodic BC (SG: 3 pts / SC : 5 pts)
        if 'P' in self.msh.bc[:2]:
            self.P11x = _np.array(list(range(self.nx - 5, self.nx)) + list(range(self.nx)) + list(range(5)), dtype=_np.uint32)
        else:
            self.P11x = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[:2] and self.cpt:
            self.P3x = _np.array(list(range(self.nx - 1, self.nx)) + list(range(self.nx)) + list(range(1)), dtype=_np.uint32)
            self.P5x = _np.array(list(range(self.nx - 2, self.nx)) + list(range(self.nx)) + list(range(2)), dtype=_np.uint32)
        else:
            self.P3x = _np.zeros(0, dtype=_np.uint32)
            self.P5x = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[2:]:
            self.P11y = _np.array(list(range(self.ny - 5, self.ny)) + list(range(self.ny)) + list(range(5)), dtype=_np.uint32)
        else:
            self.P11y = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[2:] and self.cpt:
            self.P3y = _np.array(list(range(self.ny - 1, self.ny)) + list(range(self.ny)) + list(range(1)), dtype=_np.uint32)
            self.P5y = _np.array(list(range(self.ny - 2, self.ny)) + list(range(self.ny)) + list(range(2)), dtype=_np.uint32)
        else:
            self.P3y = _np.zeros(0, dtype=_np.uint32)
            self.P5y = _np.zeros(0, dtype=_np.uint32)

        # Wall and NR BC
        self.bc = []

        for face in self.msh.obstacles.faces:
            if not face.covered and not face.clamped:
                self.bc.append(Face2d(self, face))

        for face in self.msh.bounds.faces:
            self.bc.append(Face2d(self, face))

    cdef void subdomains_init(self) noexcept:

        self.dmns_n = len(self.msh.cdomains)
        self.dmns = <domain2d *> malloc(self.dmns_n * sizeof(domain2d))
        for i in range(self.dmns_n):
            self.dmns[i].n = &self.dmns_n
            self.dmns[i].ixmin = self.msh.cdomains[i].cx[0]
            self.dmns[i].ixmax = self.msh.cdomains[i].cx[1]
            self.dmns[i].iymin = self.msh.cdomains[i].cy[0]
            self.dmns[i].iymax = self.msh.cdomains[i].cy[1]
            self.dmns[i].size_d = _np.prod(self.msh.cdomains[i].size)
            set_thread_infos(&self.dmns[i].thread_info_eul, &self.vars.eul_lock)
            set_thread_infos(&self.dmns[i].thread_info_vsc, &self.vars.vsc_lock)
            set_thread_infos(&self.dmns[i].thread_info_rsd, &self.vars.rsd_lock)
            set_thread_infos(&self.dmns[i].thread_info_pup, &self.vars.pup_lock)
            set_thread_infos(&self.dmns[i].thread_info_vup, &self.vars.vup_lock)
            set_thread_infos(&self.dmns[i].thread_info_cpy, &self.vars.cpy_lock)
            set_thread_infos(&self.dmns[i].thread_info_tes, &self.vars.tes_lock)
            set_thread_infos(&self.dmns[i].thread_info_n2p, &self.vars.n2p_lock)

        self.dmns_x_n = len(self.msh.xdomains)
        self.dmns_x = <domain_ax2d *> malloc(self.dmns_x_n * sizeof(domain_ax2d))
        for i in range(self.dmns_x_n):
            self.dmns_x[i].n = &self.dmns_x_n
            self.dmns_x[i].fu_stime = &self.vars.fux_stime
            self.dmns_x[i].fu_gtime = &self.vars.fux_gtime
            self.dmns_x[i].sc_flag = 1
            self.dmns_x[i].ixmin = self.msh.xdomains[i].cx[0]
            self.dmns_x[i].ixmax = self.msh.xdomains[i].cx[1]
            self.dmns_x[i].iymin = self.msh.xdomains[i].cy[0]
            self.dmns_x[i].iymax = self.msh.xdomains[i].cy[1]
            self.dmns_x[i].dscm = self.msh.xdomains[i].scm_code + self.flag_x
            self.dmns_x[i].fscm = self.msh.xdomains[i].scm_code
            self.dmns_x[i].size_d = _np.prod(self.msh.xdomains[i].size)
            set_thread_infos(&self.dmns_x[i].thread_info_du, &self.vars.dux_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_lf, &self.vars.lfx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_sg, &self.vars.sgx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_sc, &self.vars.scx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_fu, &self.vars.fux_lock)

        self.dmns_y_n = len(self.msh.ydomains)
        self.dmns_y = <domain_ax2d *> malloc(self.dmns_y_n * sizeof(domain_ax2d))
        for i in range(self.dmns_y_n):
            self.dmns_y[i].n = &self.dmns_y_n
            self.dmns_y[i].fu_stime = &self.vars.fuy_stime
            self.dmns_y[i].fu_gtime = &self.vars.fuy_gtime
            self.dmns_y[i].sc_flag = 1
            self.dmns_y[i].ixmin = self.msh.ydomains[i].cx[0]
            self.dmns_y[i].ixmax = self.msh.ydomains[i].cx[1]
            self.dmns_y[i].iymin = self.msh.ydomains[i].cy[0]
            self.dmns_y[i].iymax = self.msh.ydomains[i].cy[1]
            self.dmns_y[i].dscm = self.msh.ydomains[i].scm_code + self.flag_y
            self.dmns_y[i].fscm = self.msh.ydomains[i].scm_code
            self.dmns_y[i].size_d = _np.prod(self.msh.ydomains[i].size)
            set_thread_infos(&self.dmns_y[i].thread_info_du, &self.vars.duy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_lf, &self.vars.lfy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_sc, &self.vars.scy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_sg, &self.vars.sgy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_fu, &self.vars.fuy_lock)

    cpdef void subdomains_show_c(self) noexcept:
        """Show table gathering the results of thread optimization for global domain. """
        cdef Py_ssize_t i = 0
        cdef domain2d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True, True if self.vars.vsc else False, True, True, True,
                True if self.src_size else None,
                True if self.vars.crv else None]
        procs = list(compress(['eul', 'vsc', 'cpy', 'pup', 'vup', 'tes', 'n2p'], mask))
        globs = list(compress([self.vars.eul_glob, self.vars.vsc_glob, self.vars.cpy_glob,
                               self.vars.pup_glob, self.vars.vup_glob,
                               self.vars.tes_glob, self.vars.n2p_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.eul_gtime, self.vars.vsc_gtime, self.vars.cpy_gtime,
                                self.vars.pup_gtime, self.vars.vup_gtime,
                                self.vars.tes_gtime, self.vars.n2p_gtime], mask))
        stimes = list(compress([self.vars.eul_stime, self.vars.vsc_stime, self.vars.cpy_stime,
                                self.vars.pup_stime, self.vars.vup_stime,
                                self.vars.tes_stime, self.vars.n2p_stime], mask))
        calls = list(compress([self.vars.eul_call, self.vars.vsc_call, self.vars.cpy_call,
                               self.vars.pup_call, self.vars.vup_call,
                               self.vars.tes_call, self.vars.n2p_call], mask))
        locks = list(compress([self.vars.eul_lock, self.vars.vsc_lock, self.vars.cpy_lock,
                               self.vars.pup_lock, self.vars.vup_lock,
                               self.vars.tes_lock, self.vars.n2p_lock], mask))

        table = _Table(title='[bold bright_red]Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]Subdomain parameters (n={self.dmns_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_n):
            dmn = self.dmns[i]
            threads = compress([dmn.thread_info_eul.cpu, dmn.thread_info_vsc.cpu, dmn.thread_info_cpy.cpu,
                                dmn.thread_info_pup.cpu, dmn.thread_info_vup.cpu, dmn.thread_info_rsd.cpu,
                                dmn.thread_info_tes.cpu, dmn.thread_info_n2p.cpu], mask)
            calls = compress([dmn.thread_info_eul.calls, dmn.thread_info_vsc.calls, dmn.thread_info_cpy.calls,
                              dmn.thread_info_pup.calls, dmn.thread_info_vup.calls, dmn.thread_info_rsd.calls,
                              dmn.thread_info_tes.calls, dmn.thread_info_n2p.calls], mask)
            locks = compress([dmn.thread_info_eul.lock, dmn.thread_info_vsc.lock, dmn.thread_info_cpy.lock,
                              dmn.thread_info_pup.lock, dmn.thread_info_vup.lock, dmn.thread_info_rsd.lock,
                              dmn.thread_info_tes.lock, dmn.thread_info_n2p.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_eul)),
                                convert(get_timings(&dmn.thread_info_vsc)),
                                convert(get_timings(&dmn.thread_info_cpy)),
                                convert(get_timings(&dmn.thread_info_pup)),
                                convert(get_timings(&dmn.thread_info_vup)),
                                convert(get_timings(&dmn.thread_info_rsd)),
                                convert(get_timings(&dmn.thread_info_tes)),
                                convert(get_timings(&dmn.thread_info_n2p))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cpdef void subdomains_show_x(self) noexcept:
        """Show table gathering the results of thread optimization for x domains. """
        cdef Py_ssize_t i = 0
        cdef domain_ax2d dmn


        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.flt or self.cpt else False]
        procs = list(compress(['du', 'lf', 'sg', 'sc', 'fu'], mask))
        globs = list(compress([self.vars.dux_glob, self.vars.lfx_glob, self.vars.sgx_glob,
                               self.vars.scx_glob, self.vars.fux_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.dux_gtime, self.vars.lfx_gtime, self.vars.sgx_gtime,
                                self.vars.scx_gtime, self.vars.fux_gtime], mask))
        stimes = list(compress([self.vars.dux_stime, self.vars.lfx_stime, self.vars.sgx_stime,
                                self.vars.scx_stime, self.vars.fux_stime], mask))
        calls =  list(compress([self.vars.dux_call, self.vars.lfx_call, self.vars.sgx_call,
                                self.vars.scx_call, self.vars.fux_call], mask))
        locks =  list(compress([self.vars.dux_lock, self.vars.lfx_lock, self.vars.sgx_lock,
                                self.vars.scx_lock, self.vars.fux_lock], mask))

        table = _Table(title='[bold bright_red]x-Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]x-Subdomain parameters (n={self.dmns_x_n} [cpu (calls/lock)])', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_x_n):
            dmn = self.dmns_x[i]
            threads = compress([dmn.thread_info_du.cpu, dmn.thread_info_lf.cpu, dmn.thread_info_sg.cpu,
                                dmn.thread_info_sc.cpu, dmn.thread_info_fu.cpu], mask)
            calls =   compress([dmn.thread_info_du.calls, dmn.thread_info_lf.calls, dmn.thread_info_sg.calls,
                                dmn.thread_info_sc.calls, dmn.thread_info_fu.calls], mask)
            locks =   compress([dmn.thread_info_du.lock, dmn.thread_info_lf.lock, dmn.thread_info_sg.lock,
                                dmn.thread_info_sc.lock, dmn.thread_info_fu.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_du)),
                                convert(get_timings(&dmn.thread_info_lf)),
                                convert(get_timings(&dmn.thread_info_sg)),
                                convert(get_timings(&dmn.thread_info_sc)),
                                convert(get_timings(&dmn.thread_info_fu))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cpdef void subdomains_show_y(self) noexcept:
        """Show table gathering the results of thread optimization for global domain. """
        cdef Py_ssize_t i = 0
        cdef domain_ax2d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.flt or self.cpt else False]
        procs = list(compress(['du', 'lf', 'sg', 'sc', 'fu'], mask))
        globs = list(compress([self.vars.duy_glob, self.vars.lfy_glob, self.vars.sgy_glob, self.vars.scy_glob, self.vars.fuy_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.duy_gtime, self.vars.lfy_gtime, self.vars.sgy_gtime, self.vars.scy_gtime, self.vars.fuy_gtime], mask))
        stimes = list(compress([self.vars.duy_stime, self.vars.lfy_stime, self.vars.sgy_stime, self.vars.scy_stime, self.vars.fuy_stime], mask))
        calls =  list(compress([self.vars.duy_call, self.vars.lfy_call, self.vars.sgy_call, self.vars.scy_call, self.vars.fuy_call], mask))
        locks =  list(compress([self.vars.duy_lock, self.vars.lfy_lock, self.vars.sgy_lock, self.vars.scy_lock, self.vars.fuy_lock], mask))

        table = _Table(title='[bold bright_red]y-Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]y-Subdomain parameters (n={self.dmns_x_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_y_n):
            dmn = self.dmns_y[i]
            threads = compress([dmn.thread_info_du.cpu, dmn.thread_info_lf.cpu, dmn.thread_info_sg.cpu, dmn.thread_info_sc.cpu, dmn.thread_info_fu.cpu], mask)
            calls =   compress([dmn.thread_info_du.calls, dmn.thread_info_lf.calls, dmn.thread_info_sg.calls, dmn.thread_info_sc.calls, dmn.thread_info_fu.calls], mask)
            locks =   compress([dmn.thread_info_du.lock, dmn.thread_info_lf.lock, dmn.thread_info_sg.lock, dmn.thread_info_sc.lock, dmn.thread_info_fu.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_du)),
                                convert(get_timings(&dmn.thread_info_lf)),
                                convert(get_timings(&dmn.thread_info_sg)),
                                convert(get_timings(&dmn.thread_info_sc)),
                                convert(get_timings(&dmn.thread_info_fu))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cdef void fields_init(self) noexcept:

        cdef double p0 = self.cfg.tp.p0
        cdef double rho0 = self.cfg.tp.rho0

        self.p = _np.full((self.nx, self.ny), p0)
        self.r = _np.full_like(self.p, rho0)
        self.ru = _np.zeros_like(self.p)
        self.rv = _np.zeros_like(self.p)
        self.re = _np.zeros_like(self.p)

        if self.ics.has_old_fields:
            self.fields_init_old()
        else:
            self.fields_init_new()

        # Vorticity
        if self.vrt:
            self.wz = _np.zeros_like(self.p)
        else:
            self.wz = _np.zeros((0, ) * len(self.msh.shape))   # Because it's public!

    cdef void fields_init_old(self) noexcept:

        cdef Py_ssize_t ix, iy

        for ix in range(self.nx):
            for iy in range(self.ny):
                self.r[ix, iy] = self.ics._r[ix, iy]
                self.ru[ix, iy] = self.ics._ru[ix, iy]
                self.rv[ix, iy] = self.ics._rv[ix, iy]
                self.re[ix, iy] = self.ics._re[ix, iy]
        self.p_update()

    cdef void fields_init_new(self) noexcept:

        cdef domain2d dmn
        cdef Py_ssize_t c, ix, iy
        cdef double[:, ::1] ci
        cdef double p0 = self.cfg.tp.p0
        cdef double c0_2 = self.cfg.tp.c0 * self.cfg.tp.c0
        cdef double gm1 = self.cfg.tp.gamma - 1.

        if self.ics.p is not None:
            ci = self.ics.p
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        self.p[ix, iy] += ci[ix, iy]

        # Initial pressure pulses
        if len(self.cfg.src.ics) != 0:
            self.ics_init()

        # Density
        for c in range(self.dmns_n):
            dmn = self.dmns[c]
            for ix in range(dmn.ixmin, dmn.ixmax + 1):
                for iy in range(dmn.iymin, dmn.iymax + 1):
                    self.r[ix, iy] += (self.p[ix, iy] - p0) / c0_2

        # x-velocity
        if self.ics.vx is not None:
            ci = self.ics.vx
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        self.ru[ix, iy] = ci[ix, iy] * self.r[ix, iy]

        # y-velocity
        if self.ics.vy is not None:
            ci = self.ics.vy
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        self.rv[ix, iy] = ci[ix, iy] * self.r[ix, iy]

        # Energy
        for c in range(self.dmns_n):
            dmn = self.dmns[c]
            for ix in range(dmn.ixmin, dmn.ixmax + 1):
                for iy in range(dmn.iymin, dmn.iymax + 1):
                    self.re[ix, iy] = self.p[ix, iy] / gm1 + \
                                        0.5 * (self.ru[ix, iy] * self.ru[ix, iy] +
                                               self.rv[ix, iy] * self.rv[ix, iy]) / self.r[ix, iy]

        # Set velocity to 0 at obstacle locations (can be optimized...)
        self.zero_obstacles()

    cdef void opt_init(self) noexcept:

        # Optimization stuff
        self.vars.rsd_lock = 0

        self.vars.eul_lock = 0
        self.vars.eul_call = 0
        self.vars.eul_glob = 0
        self.vars.eul_gtime = DBL_MAX
        self.vars.eul_stime = DBL_MAX

        self.vars.vsc_lock = 0
        self.vars.vsc_call = 0
        self.vars.vsc_glob = 0
        self.vars.vsc_gtime = DBL_MAX
        self.vars.vsc_stime = DBL_MAX

        self.vars.cpy_lock = 0
        self.vars.cpy_call = 0
        self.vars.cpy_glob = 0
        self.vars.cpy_gtime = DBL_MAX
        self.vars.cpy_stime = DBL_MAX

        self.vars.pup_lock = 0
        self.vars.pup_call = 0
        self.vars.pup_glob = 0
        self.vars.pup_gtime = DBL_MAX
        self.vars.pup_stime = DBL_MAX

        self.vars.vup_lock = 0
        self.vars.vup_call = 0
        self.vars.vup_glob = 0
        self.vars.vup_gtime = DBL_MAX
        self.vars.vup_stime = DBL_MAX

        self.vars.n2p_lock = 0
        self.vars.n2p_call = 0
        self.vars.n2p_glob = 0
        self.vars.n2p_gtime = DBL_MAX
        self.vars.n2p_stime = DBL_MAX

        self.vars.tes_lock = 0
        self.vars.tes_call = 0
        self.vars.tes_glob = 0
        self.vars.tes_gtime = DBL_MAX
        self.vars.tes_stime = DBL_MAX

        self.vars.dux_lock = 0
        self.vars.dux_call = 0
        self.vars.dux_glob = 0
        self.vars.dux_gtime = DBL_MAX
        self.vars.dux_stime = DBL_MAX

        self.vars.duy_lock = 0
        self.vars.duy_call = 0
        self.vars.duy_glob = 0
        self.vars.duy_gtime = DBL_MAX
        self.vars.duy_stime = DBL_MAX

        self.vars.lfx_lock = 0
        self.vars.lfx_call = 0
        self.vars.lfx_glob = 0
        self.vars.lfx_gtime = DBL_MAX
        self.vars.lfx_stime = DBL_MAX

        self.vars.lfy_lock = 0
        self.vars.lfy_call = 0
        self.vars.lfy_glob = 0
        self.vars.lfy_gtime = DBL_MAX
        self.vars.lfy_stime = DBL_MAX

        self.vars.sgx_lock = 0
        self.vars.sgx_call = 0
        self.vars.sgx_glob = 0
        self.vars.sgx_gtime = DBL_MAX
        self.vars.sgx_stime = DBL_MAX

        self.vars.sgy_lock = 0
        self.vars.sgy_call = 0
        self.vars.sgy_glob = 0
        self.vars.sgy_gtime = DBL_MAX
        self.vars.sgy_stime = DBL_MAX

        self.vars.scx_lock = 0
        self.vars.scx_call = 0
        self.vars.scx_glob = 0
        self.vars.scx_gtime = DBL_MAX
        self.vars.scx_stime = DBL_MAX

        self.vars.scy_lock = 0
        self.vars.scy_call = 0
        self.vars.scy_glob = 0
        self.vars.scy_gtime = DBL_MAX
        self.vars.scy_stime = DBL_MAX

        self.vars.fux_lock = 0
        self.vars.fux_call = 0
        self.vars.fux_glob = 0
        self.vars.fux_gtime = DBL_MAX
        self.vars.fux_stime = DBL_MAX

        self.vars.fuy_lock = 0
        self.vars.fuy_call = 0
        self.vars.fuy_glob = 0
        self.vars.fuy_gtime = DBL_MAX
        self.vars.fuy_stime = DBL_MAX

    cdef void vars_init(self) noexcept:

        # Fluxes along x direction
        self.E = _np.zeros_like(self.p)
        self.Eu = _np.zeros_like(self.p)
        self.Ev = _np.zeros_like(self.p)
        self.Ee = _np.zeros_like(self.p)

        # Fluxes along y direction
        self.F = _np.zeros_like(self.p)
        self.Fu = _np.zeros_like(self.p)
        self.Fv = _np.zeros_like(self.p)
        self.Fe = _np.zeros_like(self.p)

        # Used as fields copy and for filters
        self.K = _np.zeros_like(self.p)
        self.Ku = _np.zeros_like(self.p)
        self.Kv = _np.zeros_like(self.p)
        self.Ke = _np.zeros_like(self.p)

        # Temperature
        if self.vsc:
            self.Tk = _np.zeros_like(self.p)
        else: # because it's public
            self.Tk = _np.zeros((0, ) * len(self.msh.shape))

        # Stress tensor
        self.tau11 = _np.zeros_like(self.Tk)
        self.tau22 = _np.zeros_like(self.Tk)
        self.tau12 = _np.zeros_like(self.Tk)

    cdef void cvars_init(self) noexcept:
        self.vars.dmns = self.dmns
        self.vars.dmns_n = self.dmns_n
        self.vars.dmns_x = self.dmns_x
        self.vars.dmns_x_n = self.dmns_x_n
        self.vars.dmns_y = self.dmns_y
        self.vars.dmns_y_n = self.dmns_y_n

        self.vars.crv = self.crv
        self.vars.vsc = self.vsc

        self.vars.nx = self.nx
        self.vars.ny = self.ny
        self.vars.size = self.nx * self.ny

        # Constants
        self.vars.p0 = self.cfg.tp.p0
        self.vars.mu0 = self.cfg.tp.mu0
        self.vars.Tref = self.cfg.tp.Tref
        self.vars.Ssu = self.cfg.tp.Ssu
        self.vars.SsuTref = self.cfg.tp.Tref + self.cfg.tp.Ssu
        self.vars.cppr = self.cfg.tp.Cp / self.cfg.tp.prandtl
        self.vars.cpmcv = self.cfg.tp.Cp - self.cfg.tp.Cv
        self.vars.gm1 = self.cfg.tp.gamma - 1.
        self.vars.gm1_over_c = self.vars.gm1 / (self.cfg.tp.c0 * self.cfg.tp.c0)
        self.vars.gm1_over_cpmcv = self.vars.gm1 / (self.cfg.tp.Cp - self.cfg.tp.Cv)
        self.vars.xnu_n = self.cfg.sol.xnu_n
        self.vars.xnu_0 = self.cfg.sol.xnu_0
        self.vars.rsd = 0

        # Steps
        self.vars.odx = &self.odx
        self.vars.ody = &self.ody
        self.vars.odx_v = &self.odx_v[0]
        self.vars.ody_v = &self.ody_v[0]

        self.vars.odxdt = &self.odxdt
        self.vars.odydt = &self.odydt
        self.vars.odxdt_v = &self.odxdt_v[0]
        self.vars.odydt_v = &self.odydt_v[0]

        self.vars.odxdtrk = &self.odxdtrk
        self.vars.odydtrk = &self.odydtrk
        self.vars.odxdtrk_v = &self.odxdtrk_v[0]
        self.vars.odydtrk_v = &self.odydtrk_v[0]

        self.vars.P3x = &self.P3x[0]
        self.vars.P3y = &self.P3y[0]
        self.vars.P5x = &self.P5x[0]
        self.vars.P5y = &self.P5y[0]
        self.vars.P11x = &self.P11x[0]
        self.vars.P11y = &self.P11y[0]

        # fields
        self.vars.r = &self.r[0, 0]
        self.vars.ru = &self.ru[0, 0]
        self.vars.rv = &self.rv[0, 0]
        self.vars.re = &self.re[0, 0]
        self.vars.p = &self.p[0, 0]
        self.vars.Tk = &self.Tk[0, 0]
        self.vars.wz = &self.wz[0, 0]

        # intermediate variables
        self.vars.K = &self.K[0, 0]
        self.vars.Ku = &self.Ku[0, 0]
        self.vars.Kv = &self.Kv[0, 0]
        self.vars.Ke = &self.Ke[0, 0]

        self.vars.E = &self.E[0, 0]
        self.vars.Eu = &self.Eu[0, 0]
        self.vars.Ev = &self.Ev[0, 0]
        self.vars.Ee = &self.Ee[0, 0]
        self.vars.F = &self.F[0, 0]
        self.vars.Fu = &self.Fu[0, 0]
        self.vars.Fv = &self.Fv[0, 0]
        self.vars.Fe = &self.Fe[0, 0]

        self.vars.invJ = &self.invJ[0, 0]
        self.vars.dx_du = &self.dx_du[0, 0]
        self.vars.dx_dv = &self.dx_dv[0, 0]
        self.vars.dy_du = &self.dy_du[0, 0]
        self.vars.dy_dv = &self.dy_dv[0, 0]

        self.vars.tau11 = &self.tau11[0, 0]
        self.vars.tau22 = &self.tau22[0, 0]
        self.vars.tau12 = &self.tau12[0, 0]

    cdef void buffer_init(self) noexcept:

        cdef double s0 = 1.
        cdef Py_ssize_t i, ix, iy
        cdef double Dx_l = self.msh.x[self.bz_n] - self.msh.x[0]
        cdef double Dx_r = self.msh.x[self.nx - 1 - self.bz_n] - self.msh.x[0]
        cdef double Dy_l = self.msh.y[self.bz_n] - self.msh.y[0]
        cdef double Dy_r = self.msh.y[self.ny - 1 - self.bz_n] - self.msh.y[0]

        cdef double[::1] sx = _np.zeros(self.nx)
        cdef double[::1] sy = _np.zeros(self.ny)

        self.sigma = _np.zeros((self.nx, self.ny))

        for i in range(0, self.bz_n):

            if self.msh.bounds.faces[0].bc == 'A':
                sx[i] = s0 * abs((self.msh.x[i] - self.msh.x[self.bz_n]) / Dx_l) ** self.bz_forder
            if self.msh.bounds.faces[1].bc == 'A':
                sx[self.nx - 1 - i] = s0 * abs((self.msh.x[self.nx - 1 - i] - self.msh.x[self.nx - 1 - self.bz_n]) / Dx_r) ** self.bz_forder
            if self.msh.bounds.faces[2].bc == 'A':
                sy[i] = s0 * abs((self.msh.y[i] - self.msh.y[self.bz_n]) / Dy_l) ** self.bz_forder
            if self.msh.bounds.faces[3].bc == 'A':
                sy[self.ny - 1 - i] = s0 * abs((self.msh.y[self.ny - 1 - i] - self.msh.y[self.ny - 1 - self.bz_n]) / Dy_r) ** self.bz_forder

        for ix in range(self.nx):
            for iy in range(self.ny):
                self.sigma[ix, iy] = sx[ix] / (1 + sy[iy]) + sy[iy] / (1 + sx[ix])

        for obs in self.msh.obstacles:
            for ix in range(obs.cn[0][0], obs.cn[0][1] + 1):
                for iy in range(obs.cn[1][0], obs.cn[1][1] + 1):
                    self.sigma[ix, iy] = 0

    cdef void ics_init(self) noexcept:
        """Super Gaussian pressure initial source."""

        cdef domain2d dmn
        cdef Py_ssize_t ix, iy
        cdef double[:, ::1] profile
        cdef list ics = self.cfg.src.ics

        for src in ics:
            profile = super_gaussian2d(*self.msh.paxis, *src.origin[:2], src.S0,
                                       src.kx, src.ky, src.k, src.Bx, src.By, src.Rx)

            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        self.p[ix, iy] += profile[ix, iy]

    cdef void tes_init(self) noexcept:

        cdef double[:, ::1] profile
        cdef double gm1 = self.cfg.tp.gamma - 1.

        self.src = []
        for src in self.cfg.src.tes:
            profile = super_gaussian2d(*self.msh.paxis, *src.origin[:2],
                                       src.S0 / (src.I * gm1),
                                       src.kx, src.ky, src.k, src.Bx, src.By, src.Rx)
            self.src.append(Monopole2d(profile, src.evolution))
        self.src_size = len(self.src)

    cdef void tes_update(self) noexcept:
        """Update sources by adding the evolution of each source to the global pressure field."""

        cdef Monopole2d s
        cdef Py_ssize_t it = self.cfg.sol.it
        cdef double alpha

        for s in self.src:
            alpha = s.evolution[it] * self.dtrk
            tes_update2d(&self.vars, &s.profile[0, 0], alpha)

    cdef void zero_obstacles(self) noexcept:
        """Set velocity to 0 in obstacles."""

        cdef Py_ssize_t ix, iy

        for sub in self.msh.obstacles:
            for ix in sub.rx:
                for iy in sub.ry:
                    self.ru[ix, iy] = 0
                    self.rv[ix, iy] = 0

    cdef void rk_steps_update(self, const double rk) noexcept:
        """Flag_X can be 0 for scalar or 1 for vector."""

        if self.flag_x == 0:
            self.odxdtrk = - self.odxdt * rk
        else:
            mult_inplace(self.odxdtrk_v, self.odxdt_v, - rk)

        if self.flag_y == 0:
            self.odydtrk = - self.odydt * rk
        else:
            mult_inplace(self.odydtrk_v, self.odydt_v, - rk)

        if self.src_size:
            self.dtrk = self.dt * rk

    cdef void p_update(self) noexcept:
        pressure2d(&self.vars)

    cpdef void vrt_update(self) noexcept:
        if self.vrt:
            vorticity2d(&self.vars)

    cpdef double residual(self) noexcept:
        residual2d(&self.vars)
        return self.vars.rsd

    cdef void phys2num(self) noexcept:
        phys2num2d(&self.vars)

    cdef void num2phys(self) noexcept:
        num2phys2d(&self.vars)

    cdef void copy(self) noexcept:
        """Make a copy of old fields. """
        copy2d(&self.vars)

    cpdef void log_ns(self) noexcept:
        if self.vsc:
            print('tau11 : ', _np.array(self.tau11).min(), _np.array(self.tau11).max())
            print('tau22 : ', _np.array(self.tau22).min(), _np.array(self.tau22).max())
            print('tau12 : ', _np.array(self.tau12).min(), _np.array(self.tau12).max())
            print('Tk    : ', _np.array(self.Tk).min() - self.cfg.tp.T0, _np.array(self.Tk).max() - self.cfg.tp.T0)

    cpdef void efluxes_integrate(self) noexcept:
        """2d Eulerian fluxes calculation using schemes described in [1]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        """

        cdef Py_ssize_t irk

        # Make copy of (r, ru, rv, re) => (K, Ku, Kv, Ke)
        # or (r/J, ru/J, ...) in curvilinear rather than (r, ru, ...)
        if self.crv == 1:
            self.phys2num()

        self.copy()

        # Get back to physical vars to calculate fluxes
        if self.crv == 1:
            self.num2phys()

        for irk in range(1, 7):

            # Eulerian fluxes
            self.rk_steps_update(rk[irk])

            # Update fluxes
            self.efluxes_update()

            # Derivate + integrate fluxes
            self.efluxes_integration_x()
            self.efluxes_integration_y()

            # update sources
            if self.src_size:
                self.tes_update()

            # got (U/J) from cin() in curvilinear so get back to physical vars
            if self.crv == 1:
                self.num2phys()

            # Boundary conditions
            self.cout()

            # Compute p
            self.p_update()

    cdef void efluxes_update(self) noexcept:
        """Compute fluxes."""
        eulerian_fluxes2d(&self.vars)

    cdef void efluxes_integration_x(self) noexcept:
        """Derivate and integrate fluxes. """
        eulerian_derivatives2d_x(&self.vars)

    cdef void efluxes_integration_y(self) noexcept:
        """Derivate and integrate fluxes. """
        eulerian_derivatives2d_y(&self.vars)

    cdef void cout(self) noexcept:

        cdef Face2d face

        for face in self.bc:
                face.apply_bc(self.cfg.sol.it)

    cpdef void vfluxes_integrate(self) noexcept:
        """2d Viscous fluxes calculation using schemes described in [1]_. Curvilinear viscous
        fluxes are calculated following [2]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        .. [2] Marsden, Olivier. « Calcul direct du rayonnement acoustique de profils par une
            approche curviligne d’ordre élevé », 2005.
        """
        if self.vsc:

            # Calculate u and v and assign to E and F
            self.v_update()

            # Strain tensor
            self._Sxx()

            # Temperature gradient
            self._dtk()

            # Viscous fluxes
            self.vfluxes_update()

            # Viscous fluxes derivation then integration in numerical coordinate (1/J)
            if self.crv == 1:
                self.phys2num()

            self.vfluxes_integration_x()
            self.vfluxes_integration_y()

            if self.crv == 1:
                self.num2phys()

            # Update bc
            self.cout()

            # Update p
            self.p_update()

    cdef void vfluxes_update(self) noexcept:
        """Viscous fluxes computation. """
        viscous_fluxes2d(&self.vars)

    cdef void vfluxes_integration_x(self) noexcept:
        """Viscous fluxes integration. """
        vfluxes_integration2d_x(&self.vars)

    cdef void vfluxes_integration_y(self) noexcept:
        """Viscous fluxes integration. """
        vfluxes_integration2d_y(&self.vars)

    cdef void v_update(self) noexcept:
        """Calculate u and v and assign to E and F.

        Note
        ----
        Even in curvilinear coordinates, velocity2r(fld, 1) returns (u, v) - and
        not (u/J, v/J) - since it calculates them from old fields (r/J, ru/J, rv/J)
        as E = ru/r and F = rv/r.
        """
        velocity2d(&self.vars, 1)

    cpdef void sf_apply(self) noexcept:
        """2d Selective Filter calculated using technique described in [1]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        """
        if self.flt:
            self._sf_x()
            self.fx_update()
            self._sf_y()
            self.fy_update()
            self.p_update()

    cpdef void sc_apply(self) noexcept:
        """2d Shock capture procedure calculated using technique described in [1]_.

        References
        ----------

        .. [1] C. Bogey, N. de Cacqueray, C. Bailly, "A shock-capturing methodology based on adaptative
            spatial filtering for high-order non-linear computations", Journal of Computational Physics,
            Volume 228, Issue 5, 2009, Pages 1447-1465.
        """
        if self.cpt:

            # Capture following x
            self._lf_x()
            self._sg_x()
            self._sc_x()
            self.cx_update()

            # Capture following y
            self.p_update()
            self._lf_y()
            self._sg_y()
            self._sc_y()
            self.cy_update()

            # Update pressure
            self.p_update()

    cdef void fx_update(self) noexcept:
        """Update field values. """
        apply_filter2d_x(&self.vars)

    cdef void fy_update(self) noexcept:
        """Update field values. """
        apply_filter2d_y(&self.vars)

    cdef void cx_update(self) noexcept:
        """Update field values. """
        apply_capture2d_x(&self.vars)

    cdef void cy_update(self) noexcept:
        """Update field values. """
        apply_capture2d_y(&self.vars)

    cdef void _sf_x(self) noexcept:
        """Compute filter following x. """
        selective_filter2d_x(&self.vars)

    cdef void _sf_y(self) noexcept:
        """Compute filter following y. """
        selective_filter2d_y(&self.vars)

    cdef void _lf_x(self) noexcept:
        """Laplacian filter following x."""
        laplacian_filter2d_x(&self.vars)

    cdef void _lf_y(self) noexcept:
        """Laplacian filter following y."""
        laplacian_filter2d_y(&self.vars)

    cdef void _sg_x(self) noexcept:
        """Shock detection following x."""
        sigma2d_x(&self.vars)

    cdef void _sg_y(self) noexcept:
        """Shock detection following y."""
        sigma2d_y(&self.vars)

    cdef void _sc_x(self) noexcept:
        """Filter following x."""
        shock_capture2d_x(&self.vars)

    cdef void _sc_y(self) noexcept:
        """Filter following y."""
        shock_capture2d_y(&self.vars)

    cdef void _dtk(self) noexcept:
        """Temperature gradient : (dTk/dx, dTk/dy) => (Ee, Fe). """
        dtk2d_x(&self.vars)
        dtk2d_y(&self.vars)

    cdef void _Sxx(self) noexcept:
        """Strain tensor.

            Eu = dE/dx = dvx/dx  ||  Ev = dE/dy = dvx/dy
            Fu = dF/dx = dvy/dx  ||  Fv = dF/dy = dvy/dy.
        """
        s11_2d_x(&self.vars)
        s11_2d_y(&self.vars)
        s22_2d_x(&self.vars)
        s22_2d_y(&self.vars)

    def __dealloc__(self):
        if self.dmns is not NULL:
            for i in range(self.dmns_n):
                if self.dmns[i].thread_info_eul.timings is not NULL:
                    free(self.dmns[i].thread_info_eul.timings)
                if self.dmns[i].thread_info_pup.timings is not NULL:
                    free(self.dmns[i].thread_info_pup.timings)
                if self.dmns[i].thread_info_cpy.timings is not NULL:
                    free(self.dmns[i].thread_info_cpy.timings)
            free(self.dmns)


@cython.final
cdef class cFdtd3d:

    def __init__(self, cfg, msh, ics):

        self.msh = msh
        self.cfg = cfg
        self.ics = ics

        self.p0 = cfg.tp.p0

        self.cpt = int(self.cfg.sol.cpt)
        self.flt = int(self.cfg.sol.flt)
        self.vsc = int(self.cfg.sol.vsc)
        self.vrt = int(self.cfg.sol.vrt)

        # Computational domain initialization
        self.grid_init()
        self.bc_init()
        self.opt_init()
        self.subdomains_init()

        # Variable initialization
        self.fields_init()
        self.tes_init()
        self.vars_init()
        self.cvars_init()
        self.buffer_init()

        eulerian_fluxes3d_init(&self.vars)
        viscous_fluxes3d_init(&self.vars)

    cdef void grid_init(self) noexcept:
        self.dt = self.cfg.dt
        self.nx, self.ny, self.nz = self.msh.shape
        self.nsize = self.nx * self.ny * self.nz
        self.init_spacial_steps()

        self.crv = 0 if self.msh.mesh_type.lower() == "cartesian" else 1

        if self.crv == 1:
            self.invJ = cinv3d(self.msh.J)
            self.dx_du = self.msh.dx_du
            self.dx_dv = self.msh.dx_dv
            self.dx_dw = self.msh.dx_dw
            self.dy_du = self.msh.dy_du
            self.dy_dv = self.msh.dy_dv
            self.dy_dw = self.msh.dy_dw
            self.dz_du = self.msh.dz_du
            self.dz_dv = self.msh.dz_dv
            self.dz_dw = self.msh.dz_dw
        else:
            self.invJ = _np.zeros((0, ) * len(self.msh.shape))
            self.dx_du = _np.zeros((0, ) * len(self.msh.shape))
            self.dx_dv = _np.zeros((0, ) * len(self.msh.shape))
            self.dx_dw = _np.zeros((0, ) * len(self.msh.shape))
            self.dy_du = _np.zeros((0, ) * len(self.msh.shape))
            self.dy_dv = _np.zeros((0, ) * len(self.msh.shape))
            self.dy_dw = _np.zeros((0, ) * len(self.msh.shape))
            self.dz_du = _np.zeros((0, ) * len(self.msh.shape))
            self.dz_dv = _np.zeros((0, ) * len(self.msh.shape))
            self.dz_dw = _np.zeros((0, ) * len(self.msh.shape))

        # Buffer zone
        self.bz_n = self.msh.bz_n
        self.bz_forder = self.msh.bz_filter_order

    cdef void init_spacial_steps(self) noexcept:

        self.flag_x = 0 if self.msh.flag_x == "s" else 1
        self.flag_y = 0 if self.msh.flag_y == "s" else 1
        self.flag_z = 0 if self.msh.flag_z == "s" else 1

        self.dtrk = 0

        self.odx = 1. / self.msh.dx
        self.ody = 1. / self.msh.dy
        self.odz = 1. / self.msh.dz

        self.odxdt = self.odx * self.dt
        self.odydt = self.ody * self.dt
        self.odzdt = self.odz * self.dt

        self.odxdtrk = 0.
        self.odydtrk = 0.
        self.odzdtrk = 0.

        if self.flag_x == 1:
            self.odx_v = odu(self.msh.x)
            self.odxdt_v = mult(self.odx_v, self.dt)
            self.odxdtrk_v = _np.zeros_like(self.msh.x)
        else:
            self.odx_v = _np.zeros(0)
            self.odxdt_v = _np.zeros(0)
            self.odxdtrk_v = _np.zeros(0)

        if self.flag_y == 1:
            self.ody_v = odu(self.msh.y)
            self.odydt_v = mult(self.ody_v, self.dt)
            self.odydtrk_v = _np.zeros_like(self.msh.y)
        else:
            self.ody_v = _np.zeros(0)
            self.odydt_v = _np.zeros(0)
            self.odydtrk_v = _np.zeros(0)

        if self.flag_z == 1:
            self.odz_v = odu(self.msh.z)
            self.odzdt_v = mult(self.odz_v, self.dt)
            self.odzdtrk_v = _np.zeros_like(self.msh.z)
        else:
            self.odz_v = _np.zeros(0)
            self.odzdt_v = _np.zeros(0)
            self.odzdtrk_v = _np.zeros(0)

    cdef void bc_init(self) noexcept:

        # Periodic BC (SG: 3 pts / SC : 5 pts)
        if 'P' in self.msh.bc[:2]:
            self.P11x = _np.array(list(range(self.nx - 5, self.nx)) + list(range(self.nx)) + list(range(5)), dtype=_np.uint32)
        else:
            self.P11x = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[:2] and self.cpt:
            self.P3x = _np.array(list(range(self.nx - 1, self.nx)) + list(range(self.nx)) + list(range(1)), dtype=_np.uint32)
            self.P5x = _np.array(list(range(self.nx - 2, self.nx)) + list(range(self.nx)) + list(range(2)), dtype=_np.uint32)
        else:
            self.P3x = _np.zeros(0, dtype=_np.uint32)
            self.P5x = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[2:4]:
            self.P11y = _np.array(list(range(self.ny - 5, self.ny)) + list(range(self.ny)) + list(range(5)), dtype=_np.uint32)
        else:
            self.P11y = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[2:4] and self.cpt:
            self.P3y = _np.array(list(range(self.ny - 1, self.ny)) + list(range(self.ny)) + list(range(1)), dtype=_np.uint32)
            self.P5y = _np.array(list(range(self.ny - 2, self.ny)) + list(range(self.ny)) + list(range(2)), dtype=_np.uint32)
        else:
            self.P3y = _np.zeros(0, dtype=_np.uint32)
            self.P5y = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[4:]:
            self.P11z = _np.array(list(range(self.nz - 5, self.nz)) + list(range(self.nz)) + list(range(5)), dtype=_np.uint32)
        else:
            self.P11z = _np.zeros(0, dtype=_np.uint32)

        if 'P' in self.msh.bc[4:] and self.cpt:
            self.P3z = _np.array(list(range(self.nz - 1, self.nz)) + list(range(self.nz)) + list(range(1)), dtype=_np.uint32)
            self.P5z = _np.array(list(range(self.nz - 2, self.nz)) + list(range(self.nz)) + list(range(2)), dtype=_np.uint32)
        else:
            self.P3z = _np.zeros(0, dtype=_np.uint32)
            self.P5z = _np.zeros(0, dtype=_np.uint32)

        # Wall and NR BC
        self.bc = []

        for face in self.msh.obstacles.faces:
            if not face.covered and not face.clamped:
                self.bc.append(Face3d(self, face))

        for face in self.msh.bounds.faces:
            self.bc.append(Face3d(self, face))

    cdef void subdomains_init(self) noexcept:

        self.dmns_n = len(self.msh.cdomains)
        self.dmns = <domain3d *> malloc(self.dmns_n * sizeof(domain3d))
        for i in range(self.dmns_n):
            self.dmns[i].n = &self.dmns_n
            self.dmns[i].ixmin = self.msh.cdomains[i].cx[0]
            self.dmns[i].ixmax = self.msh.cdomains[i].cx[1]
            self.dmns[i].iymin = self.msh.cdomains[i].cy[0]
            self.dmns[i].iymax = self.msh.cdomains[i].cy[1]
            self.dmns[i].izmin = self.msh.cdomains[i].cz[0]
            self.dmns[i].izmax = self.msh.cdomains[i].cz[1]
            self.dmns[i].size_d = _np.prod(self.msh.cdomains[i].size)
            set_thread_infos(&self.dmns[i].thread_info_eul, &self.vars.eul_lock)
            set_thread_infos(&self.dmns[i].thread_info_vsc, &self.vars.vsc_lock)
            set_thread_infos(&self.dmns[i].thread_info_rsd, &self.vars.rsd_lock)
            set_thread_infos(&self.dmns[i].thread_info_pup, &self.vars.pup_lock)
            set_thread_infos(&self.dmns[i].thread_info_vup, &self.vars.vup_lock)
            set_thread_infos(&self.dmns[i].thread_info_cpy, &self.vars.cpy_lock)
            set_thread_infos(&self.dmns[i].thread_info_tes, &self.vars.tes_lock)
            set_thread_infos(&self.dmns[i].thread_info_n2p, &self.vars.n2p_lock)

        self.dmns_x_n = len(self.msh.xdomains)
        self.dmns_x = <domain_ax3d *> malloc(self.dmns_x_n * sizeof(domain_ax3d))
        for i in range(self.dmns_x_n):
            self.dmns_x[i].n = &self.dmns_x_n
            self.dmns_x[i].fu_stime = &self.vars.fux_stime
            self.dmns_x[i].fu_gtime = &self.vars.fux_gtime
            self.dmns_x[i].sc_flag = 1
            self.dmns_x[i].ixmin = self.msh.xdomains[i].cx[0]
            self.dmns_x[i].ixmax = self.msh.xdomains[i].cx[1]
            self.dmns_x[i].iymin = self.msh.xdomains[i].cy[0]
            self.dmns_x[i].iymax = self.msh.xdomains[i].cy[1]
            self.dmns_x[i].izmin = self.msh.xdomains[i].cz[0]
            self.dmns_x[i].izmax = self.msh.xdomains[i].cz[1]
            self.dmns_x[i].dscm = self.msh.xdomains[i].scm_code + self.flag_x
            self.dmns_x[i].fscm = self.msh.xdomains[i].scm_code
            self.dmns_x[i].size_d = _np.prod(self.msh.xdomains[i].size)
            set_thread_infos(&self.dmns_x[i].thread_info_du, &self.vars.dux_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_lf, &self.vars.lfx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_sg, &self.vars.sgx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_sc, &self.vars.scx_lock)
            set_thread_infos(&self.dmns_x[i].thread_info_fu, &self.vars.fux_lock)

        self.dmns_y_n = len(self.msh.ydomains)
        self.dmns_y = <domain_ax3d *> malloc(self.dmns_y_n * sizeof(domain_ax3d))
        for i in range(self.dmns_y_n):
            self.dmns_y[i].n = &self.dmns_y_n
            self.dmns_y[i].fu_stime = &self.vars.fuy_stime
            self.dmns_y[i].fu_gtime = &self.vars.fuy_gtime
            self.dmns_y[i].sc_flag = 1
            self.dmns_y[i].ixmin = self.msh.ydomains[i].cx[0]
            self.dmns_y[i].ixmax = self.msh.ydomains[i].cx[1]
            self.dmns_y[i].iymin = self.msh.ydomains[i].cy[0]
            self.dmns_y[i].iymax = self.msh.ydomains[i].cy[1]
            self.dmns_y[i].izmin = self.msh.ydomains[i].cz[0]
            self.dmns_y[i].izmax = self.msh.ydomains[i].cz[1]
            self.dmns_y[i].dscm = self.msh.ydomains[i].scm_code + self.flag_y
            self.dmns_y[i].fscm = self.msh.ydomains[i].scm_code
            self.dmns_y[i].size_d = _np.prod(self.msh.ydomains[i].size)
            set_thread_infos(&self.dmns_y[i].thread_info_du, &self.vars.duy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_lf, &self.vars.lfy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_sg, &self.vars.sgy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_sc, &self.vars.scy_lock)
            set_thread_infos(&self.dmns_y[i].thread_info_fu, &self.vars.fuy_lock)

        self.dmns_z_n = len(self.msh.zdomains)
        self.dmns_z = <domain_ax3d *> malloc(self.dmns_z_n * sizeof(domain_ax3d))
        for i in range(self.dmns_z_n):
            self.dmns_z[i].n = &self.dmns_z_n
            self.dmns_z[i].fu_stime = &self.vars.fuz_stime
            self.dmns_z[i].fu_gtime = &self.vars.fuz_gtime
            self.dmns_z[i].sc_flag = 1
            self.dmns_z[i].ixmin = self.msh.zdomains[i].cx[0]
            self.dmns_z[i].ixmax = self.msh.zdomains[i].cx[1]
            self.dmns_z[i].iymin = self.msh.zdomains[i].cy[0]
            self.dmns_z[i].iymax = self.msh.zdomains[i].cy[1]
            self.dmns_z[i].izmin = self.msh.zdomains[i].cz[0]
            self.dmns_z[i].izmax = self.msh.zdomains[i].cz[1]
            self.dmns_z[i].dscm = self.msh.zdomains[i].scm_code + self.flag_z
            self.dmns_z[i].fscm = self.msh.zdomains[i].scm_code
            self.dmns_z[i].size_d = _np.prod(self.msh.zdomains[i].size)
            set_thread_infos(&self.dmns_z[i].thread_info_du, &self.vars.duz_lock)
            set_thread_infos(&self.dmns_z[i].thread_info_lf, &self.vars.lfz_lock)
            set_thread_infos(&self.dmns_z[i].thread_info_sg, &self.vars.sgz_lock)
            set_thread_infos(&self.dmns_z[i].thread_info_sc, &self.vars.scz_lock)
            set_thread_infos(&self.dmns_z[i].thread_info_fu, &self.vars.fuz_lock)

    cpdef void subdomains_show_c(self) noexcept:
        """Show table gathering the results of thread optimization for global domain. """
        cdef Py_ssize_t i = 0
        cdef domain3d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'calls']
        mask = [True, True if self.vars.vsc else False, True, True, True,
                True if self.flt or self.cpt else False,
                True if self.src_size else None,
                True if self.vars.crv else None]
        procs = list(compress(['eul', 'vsc', 'cpy', 'pup', 'vup', 'tes', 'n2p'], mask))
        globs = list(compress([self.vars.eul_glob, self.vars.vsc_glob, self.vars.cpy_glob,
                               self.vars.pup_glob, self.vars.vup_glob,
                               self.vars.tes_glob, self.vars.n2p_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.eul_gtime, self.vars.vsc_gtime, self.vars.cpy_gtime,
                                self.vars.pup_gtime, self.vars.vup_gtime,
                                self.vars.tes_gtime, self.vars.n2p_gtime], mask))
        stimes = list(compress([self.vars.eul_stime, self.vars.vsc_stime, self.vars.cpy_stime,
                                self.vars.pup_stime, self.vars.vup_stime,
                                self.vars.tes_stime, self.vars.n2p_stime], mask))
        calls = list(compress([self.vars.eul_call, self.vars.vsc_call, self.vars.cpy_call,
                               self.vars.pup_call, self.vars.vup_call,
                               self.vars.tes_call, self.vars.n2p_call], mask))
        locks = list(compress([self.vars.eul_lock, self.vars.vsc_lock, self.vars.cpy_lock,
                               self.vars.pup_lock, self.vars.vup_lock,
                               self.vars.tes_lock, self.vars.n2p_lock], mask))

        table = _Table(title='[bold bright_red]Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]Subdomain parameters (n={self.dmns_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_n):
            dmn = self.dmns[i]
            threads = compress([dmn.thread_info_eul.cpu, dmn.thread_info_vsc.cpu, dmn.thread_info_cpy.cpu,
                                dmn.thread_info_pup.cpu, dmn.thread_info_vup.cpu, dmn.thread_info_rsd.cpu,
                                dmn.thread_info_tes.cpu, dmn.thread_info_n2p.cpu], mask)
            calls = compress([dmn.thread_info_eul.calls, dmn.thread_info_vsc.calls, dmn.thread_info_cpy.calls,
                              dmn.thread_info_pup.calls, dmn.thread_info_vup.calls, dmn.thread_info_rsd.calls,
                              dmn.thread_info_tes.calls, dmn.thread_info_n2p.calls], mask)
            locks = compress([dmn.thread_info_eul.lock, dmn.thread_info_vsc.lock, dmn.thread_info_cpy.lock,
                              dmn.thread_info_pup.lock, dmn.thread_info_vup.lock, dmn.thread_info_rsd.lock,
                              dmn.thread_info_tes.lock, dmn.thread_info_n2p.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_eul)),
                                convert(get_timings(&dmn.thread_info_vsc)),
                                convert(get_timings(&dmn.thread_info_cpy)),
                                convert(get_timings(&dmn.thread_info_pup)),
                                convert(get_timings(&dmn.thread_info_vup)),
                                convert(get_timings(&dmn.thread_info_rsd)),
                                convert(get_timings(&dmn.thread_info_tes)),
                                convert(get_timings(&dmn.thread_info_n2p))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cpdef void subdomains_show_x(self) noexcept:
        """Show table gathering the results of thread optimization for x domains. """
        cdef Py_ssize_t i = 0
        cdef domain_ax3d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.flt or self.cpt else False]
        procs = list(compress(['du', 'lf', 'sg', 'sc', 'fu'], mask))
        globs = list(compress([self.vars.dux_glob, self.vars.lfx_glob, self.vars.sgx_glob,
                               self.vars.scx_glob, self.vars.fux_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.dux_gtime, self.vars.lfx_gtime, self.vars.sgx_gtime,
                                self.vars.scx_gtime, self.vars.fux_gtime], mask))
        stimes = list(compress([self.vars.dux_stime, self.vars.lfx_stime, self.vars.sgx_stime,
                                self.vars.scx_stime, self.vars.fux_stime], mask))
        calls =  list(compress([self.vars.dux_call, self.vars.lfx_call, self.vars.sgx_call,
                                self.vars.scx_call, self.vars.fux_call], mask))
        locks =  list(compress([self.vars.dux_lock, self.vars.lfx_lock, self.vars.sgx_lock,
                                self.vars.scx_lock, self.vars.fux_lock], mask))

        table = _Table(title='[bold bright_red]x-Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]x-Subdomain parameters (n={self.dmns_x_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_x_n):
            dmn = self.dmns_x[i]
            threads = compress([dmn.thread_info_du.cpu, dmn.thread_info_lf.cpu, dmn.thread_info_sg.cpu,
                                dmn.thread_info_sc.cpu, dmn.thread_info_fu.cpu], mask)
            calls =   compress([dmn.thread_info_du.calls, dmn.thread_info_lf.calls, dmn.thread_info_sg.calls,
                                dmn.thread_info_sc.calls, dmn.thread_info_fu.calls], mask)
            locks =   compress([dmn.thread_info_du.lock, dmn.thread_info_lf.lock, dmn.thread_info_sg.lock,
                                dmn.thread_info_sc.lock, dmn.thread_info_fu.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_du)),
                                convert(get_timings(&dmn.thread_info_lf)),
                                convert(get_timings(&dmn.thread_info_sg)),
                                convert(get_timings(&dmn.thread_info_sc)),
                                convert(get_timings(&dmn.thread_info_fu))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cpdef void subdomains_show_y(self) noexcept:
        """Show table gathering the results of thread optimization for global domain. """
        cdef Py_ssize_t i = 0
        cdef domain_ax3d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True,
                True if self.cfg.cpt else False,
                True if self.cfg.cpt else False,
                True if self.cfg.cpt else False,
                True if self.flt or self.cpt else False]
        procs = list(compress(['du', 'lf', 'sg', 'sc', 'fu'], mask))
        globs = list(compress([self.vars.duy_glob, self.vars.lfy_glob, self.vars.sgy_glob,
                               self.vars.scy_glob, self.vars.fuy_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.duy_gtime, self.vars.lfy_gtime, self.vars.sgy_gtime,
                                self.vars.scy_gtime, self.vars.fuy_gtime], mask))
        stimes = list(compress([self.vars.duy_stime, self.vars.lfy_stime, self.vars.sgy_stime,
                                self.vars.scy_stime, self.vars.fuy_stime], mask))
        calls =  list(compress([self.vars.duy_call, self.vars.lfy_call, self.vars.sgy_call,
                                self.vars.scy_call, self.vars.fuy_call], mask))
        locks =  list(compress([self.vars.duy_lock, self.vars.lfy_lock, self.vars.sgy_lock,
                                self.vars.scy_lock, self.vars.fuy_lock], mask))

        table = _Table(title='[bold bright_red]y-Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]y-Subdomain parameters (n={self.dmns_y_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_y_n):
            dmn = self.dmns_y[i]
            threads = compress([dmn.thread_info_du.cpu, dmn.thread_info_lf.cpu, dmn.thread_info_sg.cpu,
                                dmn.thread_info_sc.cpu, dmn.thread_info_fu.cpu], mask)
            calls =   compress([dmn.thread_info_du.calls, dmn.thread_info_lf.calls, dmn.thread_info_sg.calls,
                                dmn.thread_info_sc.calls, dmn.thread_info_fu.calls], mask)
            locks =   compress([dmn.thread_info_du.lock, dmn.thread_info_lf.lock, dmn.thread_info_sg.lock,
                                dmn.thread_info_sc.lock, dmn.thread_info_fu.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_du)),
                                convert(get_timings(&dmn.thread_info_lf)),
                                convert(get_timings(&dmn.thread_info_sg)),
                                convert(get_timings(&dmn.thread_info_sc)),
                                convert(get_timings(&dmn.thread_info_fu))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cpdef void subdomains_show_z(self) noexcept:
        """Show table gathering the results of thread optimization for global domain. """
        cdef Py_ssize_t i = 0
        cdef domain_ax3d dmn

        # Global domain table
        cols = ['Global', 'Procedure', 'Global time', 'Single time', 'Calls/Locks']
        mask = [True,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.cpt else False,
                True if self.flt or self.cpt else False]
        procs = list(compress(['du', 'lf', 'sg', 'sc', 'fu'], mask))
        globs = list(compress([self.vars.duz_glob, self.vars.lfz_glob, self.vars.sgz_glob,
                               self.vars.scz_glob, self.vars.fuz_glob], mask))
        glob_procs = list(compress(procs, globs))
        sing_procs = list(compress(procs, [not item for item in globs]))
        gtimes = list(compress([self.vars.duz_gtime, self.vars.lfz_gtime, self.vars.sgz_gtime,
                                self.vars.scz_gtime, self.vars.fuz_gtime], mask))
        stimes = list(compress([self.vars.duz_stime, self.vars.lfz_stime, self.vars.sgz_stime,
                                self.vars.scz_stime, self.vars.fuz_stime], mask))
        calls =  list(compress([self.vars.duz_call, self.vars.lfz_call, self.vars.sgz_call,
                                self.vars.scz_call, self.vars.fuz_call], mask))
        locks =  list(compress([self.vars.duz_lock, self.vars.lfz_lock, self.vars.sgz_lock,
                                self.vars.scz_lock, self.vars.fuz_lock], mask))

        table = _Table(title='[bold bright_red]z-Global/Single timings per run', box=_box.ROUNDED, expand=True)
        for col in cols:
            table.add_column(col, justify='center')
        for p, g, st, gt, nc, lk in zip(procs, globs, stimes, gtimes, calls, locks):
            table.add_row(f"{true if g==1 else false}", f"{p:16}", f"{gt:.2e}", f"{st:.2e}", f"{nc}/{lk}")
        console.print(table)

        # Subdomain table
        table = _Table(title=f'[bold brigth_red]z-Subdomain parameters (n={self.dmns_z_n})', box=_box.ROUNDED, show_lines=True, expand=True)
        for col in ['Size', 'x-span', 'y-span'] + procs:
            if col in glob_procs:
                table.add_column(col, style='bold bright_red', justify='center')
            elif col in sing_procs:
                table.add_column(col, style='bold bright_green', justify='center')
            else:
                table.add_column(col, justify='center')
        for i in range(self.dmns_z_n):
            dmn = self.dmns_z[i]
            threads = compress([dmn.thread_info_du.cpu, dmn.thread_info_lf.cpu,
                                dmn.thread_info_sg.cpu, dmn.thread_info_sc.cpu, dmn.thread_info_fu.cpu], mask)
            calls =   compress([dmn.thread_info_du.calls, dmn.thread_info_lf.calls,
                                dmn.thread_info_sg.calls, dmn.thread_info_sc.calls, dmn.thread_info_fu.calls], mask)
            locks =   compress([dmn.thread_info_du.lock, dmn.thread_info_lf.lock,
                                dmn.thread_info_sg.lock, dmn.thread_info_sc.lock, dmn.thread_info_fu.lock], mask)
            timings = compress([convert(get_timings(&dmn.thread_info_du)),
                                convert(get_timings(&dmn.thread_info_lf)),
                                convert(get_timings(&dmn.thread_info_sg)),
                                convert(get_timings(&dmn.thread_info_sc)),
                                convert(get_timings(&dmn.thread_info_fu))], mask)
            table.add_row(f"[bold bright_green]{dmn.size_d}",
                          f"[italic]{dmn.ixmin}-{dmn.ixmax}",
                          f"[italic]{dmn.iymin}-{dmn.iymax}",
                            *[f'{t} ({c}/{locked if l else unlocked})\n{tg}'
                            for t, c, l, tg in zip(threads, calls, locks, timings)])
        console.print(table)

    cdef void fields_init(self) noexcept:

        cdef double p0 = self.cfg.tp.p0
        cdef double rho0 = self.cfg.tp.rho0
        cdef double gm1 = self.cfg.tp.gamma - 1.

        self.p = _np.full((self.nx, self.ny, self.nz), p0)
        self.r = _np.full_like(self.p, rho0)
        self.ru = _np.zeros_like(self.p)
        self.rv = _np.zeros_like(self.p)
        self.rw = _np.zeros_like(self.p)
        self.re = _np.full_like(self.p, p0 / gm1)

        if self.ics.has_old_fields:
            self.fields_init_old()
        else:
            self.fields_init_new()

        # Vorticity
        if self.vrt:
            self.wx = _np.zeros_like(self.p)
            self.wy = _np.zeros_like(self.p)
            self.wz = _np.zeros_like(self.p)
        else:
            self.wx = _np.zeros((0, ) * len(self.msh.shape))
            self.wy = _np.zeros((0, ) * len(self.msh.shape))
            self.wz = _np.zeros((0, ) * len(self.msh.shape))

    cdef void fields_init_old(self) noexcept:

        cdef Py_ssize_t ix, iy, iz

        for ix in range(self.nx):
            for iy in range(self.ny):
                for iz in range(self.nz):
                    self.r[ix, iy, iz] = self.ics._r[ix, iy, iz]
                    self.ru[ix, iy, iz] = self.ics._ru[ix, iy, iz]
                    self.rv[ix, iy, iz] = self.ics._rv[ix, iy, iz]
                    self.rw[ix, iy, iz] = self.ics._rw[ix, iy, iz]
                    self.re[ix, iy, iz] = self.ics._re[ix, iy, iz]
        self.p_update()

    cdef void fields_init_new(self) noexcept:

        cdef domain3d dmn
        cdef Py_ssize_t c, ix, iy, iz
        cdef double[:, :, ::1] ci
        cdef double p0 = self.cfg.tp.p0
        cdef double c0_2 = self.cfg.tp.c0 * self.cfg.tp.c0
        cdef double gm1 = self.cfg.tp.gamma - 1.

        if self.ics.p is not None:
            ci = self.ics.p
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        for iz in range(dmn.izmin, dmn.izmax + 1):
                            self.p[ix, iy, iz] += ci[ix, iy, iz]

        # Initial pulses
        if len(self.cfg.src.ics) != 0:
            self.ics_init()

        # Density
        for c in range(self.dmns_n):
            dmn = self.dmns[c]
            for ix in range(dmn.ixmin, dmn.ixmax + 1):
                for iy in range(dmn.iymin, dmn.iymax + 1):
                    for iz in range(dmn.izmin, dmn.izmax + 1):
                        self.r[ix, iy, iz] += (self.p[ix, iy, iz] - p0) / c0_2

        # x-velocity
        if self.ics.vx is not None:
            ci = self.ics.vx
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        for iz in range(dmn.izmin, dmn.izmax + 1):
                            self.ru[ix, iy, iz] = ci[ix, iy, iz] * self.r[ix, iy, iz]

        # y-velocity
        if self.ics.vy is not None:
            ci = self.ics.vy
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        for iz in range(dmn.izmin, dmn.izmax + 1):
                            self.rv[ix, iy, iz] = ci[ix, iy, iz] * self.r[ix, iy, iz]

        # z-velocity
        if self.ics.vz is not None:
            ci = self.ics.vz
            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        for iz in range(dmn.izmin, dmn.izmax + 1):
                            self.rw[ix, iy, iz] = ci[ix, iy, iz] * self.r[ix, iy, iz]

        # Energy
        for c in range(self.dmns_n):
            dmn = self.dmns[c]
            for ix in range(dmn.ixmin, dmn.ixmax + 1):
                for iy in range(dmn.iymin, dmn.iymax + 1):
                    for iz in range(dmn.izmin, dmn.izmax + 1):
                        self.re[ix, iy, iz] = self.p[ix, iy, iz] / gm1 + \
                                        0.5 * (self.ru[ix, iy, iz] * self.ru[ix, iy, iz] +
                                               self.rv[ix, iy, iz] * self.rv[ix, iy, iz] +
                                               self.rw[ix, iy, iz] * self.rw[ix, iy, iz]) / self.r[ix, iy, iz]

        # Set to 0 at obstacle locations
        self.zero_obstacles()

    cdef void opt_init(self) noexcept:

        # Optimization stuff
        self.vars.rsd_lock = 0

        self.vars.eul_lock = 0
        self.vars.eul_call = 0
        self.vars.eul_glob = 0
        self.vars.eul_gtime = DBL_MAX
        self.vars.eul_stime = DBL_MAX

        self.vars.vsc_lock = 0
        self.vars.vsc_call = 0
        self.vars.vsc_glob = 0
        self.vars.vsc_gtime = DBL_MAX
        self.vars.vsc_stime = DBL_MAX

        self.vars.cpy_lock = 0
        self.vars.cpy_call = 0
        self.vars.cpy_glob = 0
        self.vars.cpy_gtime = DBL_MAX
        self.vars.cpy_stime = DBL_MAX

        self.vars.pup_lock = 0
        self.vars.pup_call = 0
        self.vars.pup_glob = 0
        self.vars.pup_gtime = DBL_MAX
        self.vars.pup_stime = DBL_MAX

        self.vars.vup_lock = 0
        self.vars.vup_call = 0
        self.vars.vup_glob = 0
        self.vars.vup_gtime = DBL_MAX
        self.vars.vup_stime = DBL_MAX

        self.vars.n2p_lock = 0
        self.vars.n2p_call = 0
        self.vars.n2p_glob = 0
        self.vars.n2p_gtime = DBL_MAX
        self.vars.n2p_stime = DBL_MAX

        self.vars.tes_lock = 0
        self.vars.tes_call = 0
        self.vars.tes_glob = 0
        self.vars.tes_gtime = DBL_MAX
        self.vars.tes_stime = DBL_MAX

        self.vars.dux_lock = 0
        self.vars.dux_call = 0
        self.vars.dux_glob = 0
        self.vars.dux_gtime = DBL_MAX
        self.vars.dux_stime = DBL_MAX

        self.vars.duy_lock = 0
        self.vars.duy_call = 0
        self.vars.duy_glob = 0
        self.vars.duy_gtime = DBL_MAX
        self.vars.duy_stime = DBL_MAX

        self.vars.duz_lock = 0
        self.vars.duz_call = 0
        self.vars.duz_glob = 0
        self.vars.duz_gtime = DBL_MAX
        self.vars.duz_stime = DBL_MAX

        self.vars.lfx_lock = 0
        self.vars.lfx_call = 0
        self.vars.lfx_glob = 0
        self.vars.lfx_gtime = DBL_MAX
        self.vars.lfx_stime = DBL_MAX

        self.vars.lfy_lock = 0
        self.vars.lfy_call = 0
        self.vars.lfy_glob = 0
        self.vars.lfy_gtime = DBL_MAX
        self.vars.lfy_stime = DBL_MAX

        self.vars.lfz_lock = 0
        self.vars.lfz_call = 0
        self.vars.lfz_glob = 0
        self.vars.lfz_gtime = DBL_MAX
        self.vars.lfz_stime = DBL_MAX

        self.vars.sgx_lock = 0
        self.vars.sgx_call = 0
        self.vars.sgx_glob = 0
        self.vars.sgx_gtime = DBL_MAX
        self.vars.sgx_stime = DBL_MAX

        self.vars.sgy_lock = 0
        self.vars.sgy_call = 0
        self.vars.sgy_glob = 0
        self.vars.sgy_gtime = DBL_MAX
        self.vars.sgy_stime = DBL_MAX

        self.vars.sgz_lock = 0
        self.vars.sgz_call = 0
        self.vars.sgz_glob = 0
        self.vars.sgz_gtime = DBL_MAX
        self.vars.sgz_stime = DBL_MAX

        self.vars.scx_lock = 0
        self.vars.scx_call = 0
        self.vars.scx_glob = 0
        self.vars.scx_gtime = DBL_MAX
        self.vars.scx_stime = DBL_MAX

        self.vars.scy_lock = 0
        self.vars.scy_call = 0
        self.vars.scy_glob = 0
        self.vars.scy_gtime = DBL_MAX
        self.vars.scy_stime = DBL_MAX

        self.vars.scz_lock = 0
        self.vars.scz_call = 0
        self.vars.scz_glob = 0
        self.vars.scz_gtime = DBL_MAX
        self.vars.scz_stime = DBL_MAX

        self.vars.fux_lock = 0
        self.vars.fux_call = 0
        self.vars.fux_glob = 0
        self.vars.fux_gtime = DBL_MAX
        self.vars.fux_stime = DBL_MAX

        self.vars.fuy_lock = 0
        self.vars.fuy_call = 0
        self.vars.fuy_glob = 0
        self.vars.fuy_gtime = DBL_MAX
        self.vars.fuy_stime = DBL_MAX

        self.vars.fuz_lock = 0
        self.vars.fuz_call = 0
        self.vars.fuz_glob = 0
        self.vars.fuz_gtime = DBL_MAX
        self.vars.fuz_stime = DBL_MAX

    cdef void vars_init(self) noexcept:
        self.E = _np.zeros_like(self.p)
        self.Eu = _np.zeros_like(self.p)
        self.Ev = _np.zeros_like(self.p)
        self.Ew = _np.zeros_like(self.p)
        self.Ee = _np.zeros_like(self.p)

        self.F = _np.zeros_like(self.p)
        self.Fu = _np.zeros_like(self.p)
        self.Fv = _np.zeros_like(self.p)
        self.Fw = _np.zeros_like(self.p)
        self.Fe = _np.zeros_like(self.p)

        self.G = _np.zeros_like(self.p)
        self.Gu = _np.zeros_like(self.p)
        self.Gv = _np.zeros_like(self.p)
        self.Gw = _np.zeros_like(self.p)
        self.Ge = _np.zeros_like(self.p)

        self.K = _np.zeros_like(self.p)
        self.Ku = _np.zeros_like(self.p)
        self.Kv = _np.zeros_like(self.p)
        self.Kw = _np.zeros_like(self.p)
        self.Ke = _np.zeros_like(self.p)

        # Temperature
        if self.vsc:
            self.Tk = _np.zeros_like(self.p)
        else: # because it's public
            self.Tk = _np.zeros((0, ) * len(self.msh.shape))

        # Stress tensor
        self.tau11 = _np.zeros_like(self.Tk)
        self.tau22 = _np.zeros_like(self.Tk)
        self.tau33 = _np.zeros_like(self.Tk)
        self.tau12 = _np.zeros_like(self.Tk)
        self.tau13 = _np.zeros_like(self.Tk)
        self.tau23 = _np.zeros_like(self.Tk)

    cdef void cvars_init(self) noexcept:
        # domains
        self.vars.nx = self.nx
        self.vars.ny = self.ny
        self.vars.nz = self.nz
        self.vars.size = self.nx * self.ny * self.nz
        self.vars.dmns = self.dmns
        self.vars.dmns_n = self.dmns_n
        self.vars.dmns_x = self.dmns_x
        self.vars.dmns_x_n = self.dmns_x_n
        self.vars.dmns_y = self.dmns_y
        self.vars.dmns_y_n = self.dmns_y_n
        self.vars.dmns_z = self.dmns_z
        self.vars.dmns_z_n = self.dmns_z_n

        # flags
        self.vars.crv = self.crv
        self.vars.vsc = self.vsc

        # Constants
        self.vars.p0 = self.cfg.tp.p0
        self.vars.mu0 = self.cfg.tp.mu0
        self.vars.Tref = self.cfg.tp.Tref
        self.vars.Ssu = self.cfg.tp.Ssu
        self.vars.SsuTref = self.cfg.tp.Tref + self.cfg.tp.Ssu
        self.vars.cppr = self.cfg.tp.Cp / self.cfg.tp.prandtl
        self.vars.cpmcv = self.cfg.tp.Cp - self.cfg.tp.Cv
        self.vars.gm1 = self.cfg.tp.gamma - 1.
        self.vars.gm1_over_c = self.vars.gm1 / (self.cfg.tp.c0 * self.cfg.tp.c0)
        self.vars.gm1_over_cpmcv = self.vars.gm1 / (self.cfg.tp.Cp - self.cfg.tp.Cv)
        self.vars.xnu_n = self.cfg.sol.xnu_n
        self.vars.xnu_0 = self.cfg.sol.xnu_0
        self.vars.rsd = 0

        # Steps
        self.vars.odx = &self.odx
        self.vars.ody = &self.ody
        self.vars.odz = &self.odz
        self.vars.odx_v = &self.odx_v[0]
        self.vars.ody_v = &self.ody_v[0]
        self.vars.odz_v = &self.odz_v[0]

        self.vars.odxdt = &self.odxdt
        self.vars.odydt = &self.odydt
        self.vars.odzdt = &self.odzdt
        self.vars.odxdt_v = &self.odxdt_v[0]
        self.vars.odydt_v = &self.odydt_v[0]
        self.vars.odzdt_v = &self.odzdt_v[0]

        self.vars.odxdtrk = &self.odxdtrk
        self.vars.odydtrk = &self.odydtrk
        self.vars.odzdtrk = &self.odzdtrk
        self.vars.odxdtrk_v = &self.odxdtrk_v[0]
        self.vars.odydtrk_v = &self.odydtrk_v[0]
        self.vars.odzdtrk_v = &self.odzdtrk_v[0]

        self.vars.P3x = &self.P3x[0]
        self.vars.P3y = &self.P3y[0]
        self.vars.P5x = &self.P5x[0]
        self.vars.P5y = &self.P5y[0]
        self.vars.P11x = &self.P11x[0]
        self.vars.P11y = &self.P11y[0]

        self.vars.r = &self.r[0, 0, 0]
        self.vars.ru = &self.ru[0, 0, 0]
        self.vars.rv = &self.rv[0, 0, 0]
        self.vars.rw = &self.rw[0, 0, 0]
        self.vars.re = &self.re[0, 0, 0]
        self.vars.p = &self.p[0, 0, 0]
        self.vars.Tk = &self.Tk[0, 0, 0]

        self.vars.K = &self.K[0, 0, 0]
        self.vars.Ku = &self.Ku[0, 0, 0]
        self.vars.Kv = &self.Kv[0, 0, 0]
        self.vars.Kw = &self.Kw[0, 0, 0]
        self.vars.Ke = &self.Ke[0, 0, 0]

        self.vars.E = &self.E[0, 0, 0]
        self.vars.Eu = &self.Eu[0, 0, 0]
        self.vars.Ev = &self.Ev[0, 0, 0]
        self.vars.Ew = &self.Ew[0, 0, 0]
        self.vars.Ee = &self.Ee[0, 0, 0]

        self.vars.F = &self.F[0, 0, 0]
        self.vars.Fu = &self.Fu[0, 0, 0]
        self.vars.Fv = &self.Fv[0, 0, 0]
        self.vars.Fw = &self.Fw[0, 0, 0]
        self.vars.Fe = &self.Fe[0, 0, 0]

        self.vars.G = &self.G[0, 0, 0]
        self.vars.Gu = &self.Gu[0, 0, 0]
        self.vars.Gv = &self.Gv[0, 0, 0]
        self.vars.Gw = &self.Gw[0, 0, 0]
        self.vars.Ge = &self.Ge[0, 0, 0]

        self.vars.invJ = &self.invJ[0, 0, 0]

        self.vars.dx_du = &self.dx_du[0, 0, 0]
        self.vars.dx_dv = &self.dx_dv[0, 0, 0]
        self.vars.dx_dw = &self.dx_dw[0, 0, 0]

        self.vars.dy_du = &self.dy_du[0, 0, 0]
        self.vars.dy_dv = &self.dy_dv[0, 0, 0]
        self.vars.dy_dw = &self.dy_dw[0, 0, 0]

        self.vars.dz_du = &self.dz_du[0, 0, 0]
        self.vars.dz_dv = &self.dz_dv[0, 0, 0]
        self.vars.dz_dw = &self.dz_dw[0, 0, 0]

        self.vars.tau11 = &self.tau11[0, 0, 0]
        self.vars.tau22 = &self.tau22[0, 0, 0]
        self.vars.tau33 = &self.tau33[0, 0, 0]
        self.vars.tau12 = &self.tau12[0, 0, 0]
        self.vars.tau13 = &self.tau13[0, 0, 0]
        self.vars.tau23 = &self.tau23[0, 0, 0]

        self.vars.wx = &self.wx[0, 0, 0]
        self.vars.wy = &self.wy[0, 0, 0]
        self.vars.wz = &self.wz[0, 0, 0]

    cdef void buffer_init(self) noexcept:

        cdef double s0 = 1.
        cdef Py_ssize_t i, ix, iy, iz
        cdef double Dx_l = self.msh.x[self.bz_n] - self.msh.x[0]
        cdef double Dx_r = self.msh.x[self.nx - 1 - self.bz_n] - self.msh.x[0]
        cdef double Dy_l = self.msh.y[self.bz_n] - self.msh.y[0]
        cdef double Dy_r = self.msh.y[self.ny - 1 - self.bz_n] - self.msh.y[0]
        cdef double Dz_l = self.msh.z[self.bz_n] - self.msh.z[0]
        cdef double Dz_r = self.msh.z[self.nz - 1 - self.bz_n] - self.msh.z[0]

        cdef double[::1] sx = _np.zeros(self.nx)
        cdef double[::1] sy = _np.zeros(self.ny)
        cdef double[::1] sz = _np.zeros(self.nz)

        self.sigma = _np.zeros((self.nx, self.ny, self.nz))

        for i in range(self.bz_n):

            if self.msh.bounds.faces[0].bc == 'A':
                sx[i] = s0 * abs((self.msh.x[i] - self.msh.x[self.bz_n]) / Dx_l) ** self.bz_forder
            if self.msh.bounds.faces[1].bc == 'A':
                sx[self.nx - 1 - i] = s0 * abs((self.msh.x[self.nx - 1 - i] - self.msh.x[self.nx - 1 - self.bz_n]) / Dx_r) ** self.bz_forder
            if self.msh.bounds.faces[2].bc == 'A':
                sy[i] = s0 * abs((self.msh.y[i] - self.msh.y[self.bz_n]) / Dy_l) ** self.bz_forder
            if self.msh.bounds.faces[3].bc == 'A':
                sy[self.ny - 1 - i] = s0 * abs((self.msh.y[self.ny - 1 - i] - self.msh.y[self.ny - 1 - self.bz_n]) / Dy_r) ** self.bz_forder
            if self.msh.bounds.faces[4].bc == 'A':
                sz[i] = s0 * abs((self.msh.z[i] - self.msh.z[self.bz_n]) / Dz_l) ** self.bz_forder
            if self.msh.bounds.faces[5].bc == 'A':
                sz[self.nz - 1 - i] = s0 * abs((self.msh.z[self.nz - 1 - i] - self.msh.z[self.nz - 1 - self.bz_n]) / Dz_r) ** self.bz_forder

        for ix in range(self.nx):
            for iy in range(self.ny):
                for iz in range(self.nz):
                    self.sigma[ix, iy, iz] = sx[ix] / (1 + sy[iy] + sz[iz]) + \
                                             sy[iy] / (1 + sx[ix] + sz[iz]) + \
                                             sz[iz] / (1 + sy[iy] + sz[iz])

        # Set sigma to 0 at obstacle locations
        for obs in self.msh.obstacles:
            for ix in range(obs.cn[0][0], obs.cn[0][1] + 1):
                for iy in range(obs.cn[1][0], obs.cn[1][1] + 1):
                    for iz in range(obs.cn[2][0], obs.cn[2][1] + 1):
                        self.sigma[ix, iy, iz] = 0

    cdef void ics_init(self) noexcept:
        """Super Gaussian pressure initial source."""

        cdef domain3d dmn
        cdef Py_ssize_t ix, iy, iz
        cdef double[:, :, ::1] profile

        for src in self.cfg.src.ics:
            # => use crv even in crt. Cause slower initialization => look at mesh.axis / mesh.paxis
            profile = super_gaussian3d(*self.msh.paxis, *src.origin, src.S0,
                                    src.kx, src.ky, src.kz, src.k,
                                    src.Bx, src.By, src.Bz, src.Rx)

            for c in range(self.dmns_n):
                dmn = self.dmns[c]
                for ix in range(dmn.ixmin, dmn.ixmax + 1):
                    for iy in range(dmn.iymin, dmn.iymax + 1):
                        for iz in range(dmn.izmin, dmn.izmax + 1):
                            self.p[ix, iy, iz] += profile[ix, iy, iz]

    cdef void tes_init(self) noexcept:

        cdef double[:, :, ::1] profile
        cdef double gm1 = self.cfg.tp.gamma - 1.

        self.src = []
        for s in self.cfg.src.tes:
            profile = super_gaussian3d(*self.msh.paxis, *s.origin,
                                       s.S0 / (s.I * gm1),
                                       s.kx, s.ky, s.kz, s.k,
                                       s.Bx, s.By, s.Bz, s.Rx)
            self.src.append(Monopole3d(profile, s.evolution))
        self.src_size = len(self.src)

    cdef void tes_update(self) noexcept:
        """Update sources by adding the evolution of each source to the global pressure field."""

        cdef Monopole3d s
        cdef Py_ssize_t it = self.cfg.sol.it
        cdef double alpha

        for s in self.src:
            alpha = s.evolution[it] * self.dtrk
            tes_update3d(&self.vars, &s.profile[0, 0, 0], alpha)

    cdef void rk_steps_update(self, double rk) noexcept:

        if self.flag_x == 0:
            self.odxdtrk = - self.odxdt * rk
        else:
            mult_inplace(self.odxdtrk_v, self.odxdt_v, - rk)

        if self.flag_y == 0:
            self.odydtrk = - self.odydt * rk
        else:
            mult_inplace(self.odydtrk_v, self.odydt_v, - rk)

        if self.flag_z == 0:
            self.odzdtrk = - self.odzdt * rk
        else:
            mult_inplace(self.odzdtrk_v, self.odzdt_v, - rk)

        if self.src_size:
            self.dtrk = self.dt * rk

    cdef void zero_obstacles(self) noexcept:
        """Set velocity to 0 in obstacles."""

        cdef Py_ssize_t ix, iy, iz

        for sub in self.msh.obstacles:
            for ix in sub.rx:
                for iy in sub.ry:
                    for iz in sub.rz:
                        self.ru[ix, iy, iz] = 0
                        self.rv[ix, iy, iz] = 0
                        self.rw[ix, iy, iz] = 0

    cdef void p_update(self) noexcept:
        pressure3d(&self.vars)

    cpdef void vrt_update(self) noexcept:
        if self.vrt:
            vorticity3d(&self.vars)

    cpdef double residual(self) noexcept:
        residual3d(&self.vars)
        return self.vars.rsd

    cdef void phys2num(self) noexcept:
        phys2num3d(&self.vars)

    cdef void num2phys(self) noexcept:
        num2phys3d(&self.vars)

    cpdef void log_ns(self) noexcept:
        if self.vsc:
            print('tau11 : ', _np.array(self.tau11).min(), _np.array(self.tau11).max())
            print('tau22 : ', _np.array(self.tau22).min(), _np.array(self.tau22).max())
            print('tau33 : ', _np.array(self.tau33).min(), _np.array(self.tau33).max())
            print('tau12 : ', _np.array(self.tau12).min(), _np.array(self.tau12).max())
            print('tau13 : ', _np.array(self.tau13).min(), _np.array(self.tau13).max())
            print('tau23 : ', _np.array(self.tau23).min(), _np.array(self.tau23).max())
            print('Tk    : ', _np.array(self.Tk).min() - self.cfg.tp.T0, _np.array(self.Tk).max() - self.cfg.tp.T0)

    cpdef void efluxes_integrate(self) noexcept:
        """3d Eulerian fluxes calculation using schemes described in [1]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        """

        cdef Py_ssize_t irk

        # Make copy of (r, ru, rv, rw, re) => (K, Ku, Kv, Kw, Ke)
        # or (r/J, ru/J, ...) in curvilinear rather than (r, ru, ...)
        if self.crv == 1:
            self.phys2num()

        self.copy()

        # Get back to physical vars to calculate fluxes
        if self.crv == 1:
            self.num2phys()

        for irk in range(1, 7):

            # Eulerian fluxes
            self.rk_steps_update(rk[irk])

            # Update E & F
            self.efluxes_update()

            # Derivate + integrate fluxes
            self.efluxes_integration()
            # self.derivate_legacy()

            # update sources
            if self.src_size:
                self.tes_update()

            # got (U/J) from cin() in curvilinear so get back to physical vars
            if self.crv == 1:
                self.num2phys()

            # Boundary conditions
            self.cout()

            # Compute p
            self.p_update()

    cdef void copy(self) noexcept:
        """Make a copy of old fields."""
        copy3d(&self.vars)

    cdef void cout(self) noexcept:
        """Boundaries. """
        cdef Face3d face

        for face in self.bc:
            face.apply_bc(self.cfg.sol.it)

    cdef void efluxes_update(self) noexcept:
        """Compute fluxes."""
        eulerian_fluxes3d(&self.vars)

    cdef void efluxes_integration(self) noexcept:
        """Derivate fluxes."""
        eulerian_derivatives3d_x(&self.vars)
        eulerian_derivatives3d_y(&self.vars)
        eulerian_derivatives3d_z(&self.vars)

    cpdef void vfluxes_integrate(self) noexcept:
        """3d Viscous fluxes calculation using schemes described in [1]_. Curvilinear viscous
        fluxes are calculated following [2]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        .. [2] Marsden, Olivier. « Calcul direct du rayonnement acoustique de profils par une
            approche curviligne d’ordre élevé », 2005.
        """
        if self.vsc:

            # Calculate u, v, and w and assign to E, F, and G
            self.v_update()

            # Strain tensor
            self._Sxx()

            # Temperature gradient
            self._dtk()

            # Viscous fluxes
            self.vfluxes_update()

            # Viscous fluxes derivation then integration in numerical coordinate (1/J)
            if self.crv == 1:
                self.phys2num()

            self.vfluxes_integration()

            if self.crv == 1:
                self.num2phys()

            # Update bc
            self.cout()

            # Update p
            self.p_update()

    cdef void v_update(self) noexcept:
        """Calculate (u, v, w) and assign to (E, F, G)."""
        velocity3d(&self.vars, 1)

    cdef void vfluxes_update(self) noexcept:
        """Update 3d viscous fluxes.

        Note
        ----
            * (u, v, w)                 => (E, F, G)
            * (dTk/dx, dTk/dy, dTk/dz)  => (Ee, Fe, Ge)
            * (dvx/dx, dvx/dy, dvx/dz)  => (Eu, Ev, Ew)
            * (dvy/dx, dvy/dy, dvy/dz)  => (Fu, Fv, Fw)
            * (dvz/dx, dvz/dy, dvz/dz)  => (Gu, Gv, Gw)
        """
        viscous_fluxes3d(&self.vars)

    cdef void vfluxes_integration(self) noexcept:
        """Viscous fluxes integration. """
        vfluxes_integration3d_x(&self.vars)
        vfluxes_integration3d_y(&self.vars)
        vfluxes_integration3d_z(&self.vars)

    cpdef void sf_apply(self) noexcept:
        """3d Selective Filter calculated using technique described in [1]_.

        References
        ----------

        .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
            flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
            Pages 194-214.
        """
        if self.flt:
            self._sf_x()
            self.fx_update()
            self._sf_y()
            self.fy_update()
            self._sf_z()
            self.fz_update()
            self.p_update()

    cdef void fx_update(self) noexcept:
        """Update field values. """
        apply_filter3d_x(&self.vars)

    cdef void fy_update(self) noexcept:
        """Update field values. """
        apply_filter3d_y(&self.vars)

    cdef void fz_update(self) noexcept:
        """Update field values. """
        apply_filter3d_z(&self.vars)

    cdef void cx_update(self) noexcept:
        """Update field values. """
        apply_capture3d_x(&self.vars)

    cdef void cy_update(self) noexcept:
        """Update field values. """
        apply_capture3d_y(&self.vars)

    cdef void cz_update(self) noexcept:
        """Update field values. """
        apply_capture3d_z(&self.vars)

    cpdef void sc_apply(self) noexcept:
        """3d Shock capture procedure calculated using technique described in [1]_.

        References
        ----------

        .. [1] C. Bogey, N. de Cacqueray, C. Bailly, "A shock-capturing methodology based on adaptative
            spatial filtering for high-order non-linear computations", Journal of Computational Physics,
            Volume 228, Issue 5, 2009, Pages 1447-1465.
        """
        if self.cpt:

            # Capture following x (with p updated)
            self._lf_x()
            self._sg_x()
            self._sc_x()
            self.cx_update()

            # Capture following y
            self.p_update()
            self._lf_y()
            self._sg_y()
            self._sc_y()
            self.cy_update()

            # Capture following z
            self.p_update()
            self._lf_z()
            self._sg_z()
            self._sc_z()
            self.cz_update()

            # Update pressure at the end
            self.p_update()

    cdef void _sf_x(self) noexcept:
        """Compute filter following x. """
        selective_filter3d_x(&self.vars)

    cdef void _sf_y(self) noexcept:
        """Compute filter following y. """
        selective_filter3d_y(&self.vars)

    cdef void _sf_z(self) noexcept:
        """Compute filter following z. """
        selective_filter3d_z(&self.vars)

    cdef void _lf_x(self) noexcept:
        """Shock detection following x."""
        laplacian_filter3d_x(&self.vars)

    cdef void _lf_y(self) noexcept:
        """Shock detection following y."""
        laplacian_filter3d_y(&self.vars)

    cdef void _lf_z(self) noexcept:
        """Shock detection following z."""
        laplacian_filter3d_z(&self.vars)

    cdef void _sc_x(self) noexcept:
        """Filter following x."""
        shock_capture3d_x(&self.vars)

    cdef void _sc_y(self) noexcept:
        """Filter following y."""
        shock_capture3d_y(&self.vars)

    cdef void _sc_z(self) noexcept:
        """Filter following z."""
        shock_capture3d_z(&self.vars)

    cdef void _sg_x(self) noexcept:
        """Shock detection following x."""
        sigma3d_x(&self.vars)

    cdef void _sg_y(self) noexcept:
        """Shock detection following y."""
        sigma3d_y(&self.vars)

    cdef void _sg_z(self) noexcept:
        """Shock detection following z."""
        sigma3d_z(&self.vars)

    cdef void _Sxx(self) noexcept:
        """Strain tensor.

        Note
        ----
            Eu = dE/dx = dvx/dx  ||  Ev = dE/dy = dvx/dy  ||  Ew = dE/dz = dvx/dz
            Fu = dF/dx = dvy/dx  ||  Fv = dF/dy = dvy/dy  ||  Fw = dF/dz = dvy/dz
            Gu = dG/dx = dvz/dx  ||  Gv = dG/dy = dvz/dy  ||  Gw = dG/dz = dvy/dz
        """
        s11_3d_x(&self.vars)
        s11_3d_y(&self.vars)
        s11_3d_z(&self.vars)
        s22_3d_x(&self.vars)
        s22_3d_y(&self.vars)
        s22_3d_z(&self.vars)
        s33_3d_x(&self.vars)
        s33_3d_y(&self.vars)
        s33_3d_z(&self.vars)

    cdef void _dtk(self) noexcept:
        """Temperature gradient (dTk/dx, dTk/dy, dTk/dz) => (Ee, Fe, Ge)."""
        dtk3d_x(&self.vars)
        dtk3d_y(&self.vars)
        dtk3d_z(&self.vars)

    def __dealloc__(self):
        if self.dmns is not NULL:
            for i in range(self.dmns_n):
                if self.dmns[i].thread_info_eul.timings is not NULL:
                    free(self.dmns[i].thread_info_eul.timings)
                if self.dmns[i].thread_info_pup.timings is not NULL:
                    free(self.dmns[i].thread_info_pup.timings)
                if self.dmns[i].thread_info_cpy.timings is not NULL:
                    free(self.dmns[i].thread_info_cpy.timings)
            free(self.dmns)


cpdef void p_update2d(double[:, ::1] p, double[:, ::1] r,
                     double[:, ::1] ru, double[:, ::1] rv, double[:, ::1] re,
                     double gamma, Py_ssize_t cpu = 1):

    cdef Py_ssize_t nx = p.shape[0]
    cdef Py_ssize_t ny = p.shape[1]

    global_pressure2d(&p[0, 0], &r[0, 0], &ru[0, 0], &rv[0, 0], &re[0, 0], gamma, nx, ny, cpu)


cpdef void p_update3d(double[:, :, ::1] p, double[:, :, ::1] r,
                     double[:, :, ::1] ru, double[:, :, ::1] rv,
                     double[:, :, ::1] rw, double[:, :, ::1] re,
                     double gamma, Py_ssize_t cpu = 1):

    cdef Py_ssize_t nx = p.shape[0]
    cdef Py_ssize_t ny = p.shape[1]
    cdef Py_ssize_t nz = p.shape[2]

    global_pressure3d(&p[0, 0, 0], &r[0, 0, 0], &ru[0, 0, 0],
                      &rv[0, 0, 0], &rw[0, 0, 0], &re[0, 0, 0],
                      gamma, nx, ny, nz, cpu)
