#include <stdio.h>
#include <omp.h>
#include "cobjects.h"
#include "cfields.h"
#include "cfilters.h"
#include "kernels_sf.h"
#include "kernels_sc.h"



////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Update filter
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d/3d apply filter
////////////////////////////////////////////////////////////////////////////////

void static inline fu2d_s(double *restrict r, double *restrict ru, double *restrict rv, double *restrict re,
                          const double *restrict K, const double *restrict Ku, const double *restrict Kv, const double *restrict Ke,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            *(r + idy) -= *(K + idy);
            *(ru + idy) -= *(Ku + idy);
            *(rv + idy) -= *(Kv + idy);
            *(re + idy) -= *(Ke + idy);
        }
    }
}


void static inline fu2d_p(double *restrict r, double *restrict ru, double *restrict rv, double *restrict re,
                          const double *restrict K, const double *restrict Ku, const double *restrict Kv, const double *restrict Ke,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int cpu){

    unsigned int ix, iy, idx, idy;

    #pragma omp parallel num_threads(cpu) private(ix, iy, idx, idy)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                *(r + idy) -= *(K + idy);
                *(ru + idy) -= *(Ku + idy);
                *(rv + idy) -= *(Kv + idy);
                *(re + idy) -= *(Ke + idy);
            }
        }
    }
}


void static inline fu3d_s(double *restrict r, double *restrict ru,
                          double *restrict rv, double *restrict rw,
                          double *restrict re,
                          const double *restrict K, const double *restrict Ku,
                          const double *restrict Kv, const double *restrict Kw,
                          const double *restrict Ke,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                *(r + idz) -= *(K + idz);
                *(ru + idz) -= *(Ku + idz);
                *(rv + idz) -= *(Kv + idz);
                *(rw + idz) -= *(Kw + idz);
                *(re + idz) -= *(Ke + idz);
            }
        }
    }
}


void static inline fu3d_p(double *restrict r, double *restrict ru,
                          double *restrict rv, double *restrict rw,
                          double *restrict re,
                          const double *restrict K, const double *restrict Ku,
                          const double *restrict Kv, const double *restrict Kw,
                          const double *restrict Ke,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int cpu){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;

    #pragma omp parallel num_threads(cpu) private(ix, iy, iz, idx, idy, idz)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    *(r + idz) -= *(K + idz);
                    *(ru + idz) -= *(Ku + idz);
                    *(rv + idz) -= *(Kv + idz);
                    *(rw + idz) -= *(Kw + idz);
                    *(re + idz) -= *(Ke + idz);
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d update dispatchers [base on "fu" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline fu2d_dispatch(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            fu2d_s(fld->r, fld->ru, fld->rv, fld->re,
                   fld->K, fld->Ku, fld->Kv, fld->Ke,
                   fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            fu2d_p(fld->r, fld->ru, fld->rv, fld->re,
                   fld->K, fld->Ku, fld->Kv, fld->Ke,
                   fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static fu2d_dispatch_glob(fields2d *fld, domain_ax2d *dmns){

    unsigned int c;
    const unsigned int size = *(dmns->n);
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            fu2d_dispatch(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    *(dmns[0].fu_gtime) = fmin(*(dmns[0].fu_gtime), get_time(&start, &end));
}


void static fu2d_dispatch_sing(fields2d *fld, domain_ax2d *dmns){

    unsigned int c;
    const unsigned int size = *(dmns->n);
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        fu2d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_fu, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    *(dmns[0].fu_stime) = fmin(*(dmns[0].fu_stime), get_time(&start_loop, &end_loop));
}


void apply_filter2d_x(fields2d *fld){

    domain_ax2d *dmns_x = fld->dmns_x;
    const unsigned int max_gcalls = 2;

    if (fld->fux_call >= max_gcalls){
        fu2d_x_func(fld, dmns_x);
    } else if (fld->fux_lock < fld->dmns_n){
        fu2d_dispatch_sing(fld, dmns_x);
    } else {
        fu2d_dispatch_glob(fld, dmns_x);
        fld->fux_call += 1;

        if (fld->fux_gtime > fld->fux_stime) {
            fu2d_x_func = fu2d_dispatch_sing;
            fld->fux_glob = 0;
        } else {
            fu2d_x_func = fu2d_dispatch_glob;
            fld->fux_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->fux_gtime > 1.5 * fld->fux_stime || fld->fux_stime > 1.5 * fld->fux_gtime) {
            fld->fux_call = max_gcalls;
        }
    }
}


void apply_filter2d_y(fields2d *fld){

    domain_ax2d *dmns_y = fld->dmns_y;
    const unsigned int max_gcalls = 2;

    if (fld->fuy_call >= max_gcalls){
        fu2d_y_func(fld, dmns_y);
    } else if (fld->fuy_lock < fld->dmns_n){
        fu2d_dispatch_sing(fld, dmns_y);
    } else {
        fu2d_dispatch_glob(fld, dmns_y);
        fld->fuy_call += 1;

        if (fld->fuy_gtime > fld->fuy_stime) {
            fu2d_y_func = fu2d_dispatch_sing;
            fld->fuy_glob = 0;
        } else {
            fu2d_y_func = fu2d_dispatch_glob;
            fld->fuy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->fuy_gtime > 1.5 * fld->fuy_stime || fld->fuy_stime > 1.5 * fld->fuy_gtime) {
            fld->fuy_call = max_gcalls;
        }
    }
}


void apply_capture2d_x(fields2d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->scy_call > max_gcalls) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                if (dmns[c].sc_flag == 1) {
                    fu2d_dispatch(fld, &dmns[c], 1);
                } else {
                    dmns[c].sc_flag = 1;
                }
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                fu2d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
            } else {
                dmns[c].sc_flag = 1;
            }
        }
    }
}


void apply_capture2d_y(fields2d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->scy_call > max_gcalls) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                if (dmns[c].sc_flag == 1) {
                    fu2d_dispatch(fld, &dmns[c], 1);
                } else {
                    dmns[c].sc_flag = 1;
                }
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                fu2d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
            } else{
                dmns[c].sc_flag = 1;
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d apply_filter dispatchers [base on "fu" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline fu3d_dispatch(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            fu3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re,
                   fld->K, fld->Ku, fld->Kv, fld->Kw, fld->Ke,
                   fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            fu3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re,
                   fld->K, fld->Ku, fld->Kv, fld->Kw, fld->Ke,
                   fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static fu3d_dispatch_glob(fields3d *fld, domain_ax3d *dmns){

    unsigned int c;
    const unsigned int size = *(dmns->n);
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            fu3d_dispatch(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    *(dmns[0].fu_gtime) = fmin(*(dmns[0].fu_gtime), get_time(&start, &end));
}


void static fu3d_dispatch_sing(fields3d *fld, domain_ax3d *dmns){

    unsigned int c;
    const unsigned int size = *(dmns->n);
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        fu3d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_fu, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    *(dmns[0].fu_stime) = fmin(*(dmns[0].fu_stime), get_time(&start_loop, &end_loop));
}


void apply_filter3d_x(fields3d *fld){

    domain_ax3d *dmns_x = fld->dmns_x;
    const unsigned int max_gcalls = 2;

    if (fld->fux_call >= max_gcalls){
        fu3d_x_func(fld, dmns_x);
    } else if (fld->fux_lock < fld->dmns_x_n){
        fu3d_dispatch_sing(fld, dmns_x);
    } else {
        fu3d_dispatch_glob(fld, dmns_x);
        fld->fux_call += 1;

        if (fld->fux_gtime > fld->fux_stime) {
            fu3d_x_func = fu3d_dispatch_sing;
            fld->fux_glob = 0;
        } else {
            fu3d_x_func = fu3d_dispatch_glob;
            fld->fux_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->fux_gtime > 1.5 * fld->fux_stime || fld->fux_stime > 1.5 * fld->fux_gtime) {
            fld->fux_call = max_gcalls;
        }
    }
}


void apply_filter3d_y(fields3d *fld){

    domain_ax3d *dmns_y = fld->dmns_y;
    const unsigned int max_gcalls = 2;

    if (fld->fuy_call >= max_gcalls){
        fu3d_y_func(fld, dmns_y);
    } else if (fld->fuy_lock < fld->dmns_y_n){
        fu3d_dispatch_sing(fld, dmns_y);
    } else {
        fu3d_dispatch_glob(fld, dmns_y);
        fld->fuy_call += 1;

        if (fld->fuy_gtime > fld->fuy_stime) {
            fu3d_y_func = fu3d_dispatch_sing;
            fld->fuy_glob = 0;
        } else {
            fu3d_y_func = fu3d_dispatch_glob;
            fld->fuy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->fuy_gtime > 1.5 * fld->fuy_stime || fld->fuy_stime > 1.5 * fld->fuy_gtime) {
            fld->fuy_call = max_gcalls;
        }
    }
}


void apply_filter3d_z(fields3d *fld){

    domain_ax3d *dmns_z = fld->dmns_z;
    const unsigned int max_gcalls = 2;

    if (fld->fuz_call >= max_gcalls){
        fu3d_z_func(fld, dmns_z);
    } else if (fld->fuz_lock < fld->dmns_z_n){
        fu3d_dispatch_sing(fld, dmns_z);
    } else {
        fu3d_dispatch_glob(fld, dmns_z);
        fld->fuz_call += 1;

        if (fld->fuz_gtime > fld->fuz_stime) {
            fu3d_z_func = fu3d_dispatch_sing;
            fld->fuz_glob = 0;
        } else {
            fu3d_z_func = fu3d_dispatch_glob;
            fld->fuz_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->fuz_gtime > 1.5 * fld->fuz_stime || fld->fuz_stime > 1.5 * fld->fuz_gtime) {
            fld->fuz_call = max_gcalls;
        }
    }
}


void apply_capture3d_x(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->scx_call > max_gcalls) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                if (dmns[c].sc_flag == 1) {
                    fu3d_dispatch(fld, &dmns[c], 1);
                } else {
                    dmns[c].sc_flag = 1;
                }
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                fu3d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
            } else {
                dmns[c].sc_flag = 1;
            }
        }
    }
}


void apply_capture3d_y(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->scy_call > max_gcalls) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                if (dmns[c].sc_flag == 1) {
                    fu3d_dispatch(fld, &dmns[c], 1);
                } else {
                    dmns[c].sc_flag = 1;
                }
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                fu3d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
            } else {
                dmns[c].sc_flag = 1;
            }
        }
    }
}


void apply_capture3d_z(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->scz_call > max_gcalls) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                if (dmns[c].sc_flag == 1) {
                    fu3d_dispatch(fld, &dmns[c], 1);
                } else {
                    dmns[c].sc_flag = 1;
                }
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                fu3d_dispatch(fld, &dmns[c], dmns[c].thread_info_fu.cpu);
            } else {
                dmns[c].sc_flag = 1;
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Selective Filter dispatchers
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d Selective Filter x dispatchers [base on "dux" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline sf2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sf2d_xc(fld->K, fld->r, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xc(fld->Ku, fld->ru, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xc(fld->Kv, fld->rv, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xc(fld->Ke, fld->re, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            sf2d_xP(fld->K, fld->r, fld->xnu_n, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xP(fld->Ku, fld->ru, fld->xnu_n, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xP(fld->Kv, fld->rv, fld->xnu_n, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xP(fld->Ke, fld->re, fld->xnu_n, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            sf2d_xp(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xp(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xp(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xp(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            sf2d_xm(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xm(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xm(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_xm(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void selective_filter2d_x(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                sf2d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            sf2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Selective Filter y dispatchers [base on "duy" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline sf2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sf2d_yc(fld->K, fld->r, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yc(fld->Ku, fld->ru, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yc(fld->Kv, fld->rv, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yc(fld->Ke, fld->re, fld->xnu_n, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            sf2d_yP(fld->K, fld->r, fld->xnu_n, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yP(fld->Ku, fld->ru, fld->xnu_n, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yP(fld->Kv, fld->rv, fld->xnu_n, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yP(fld->Ke, fld->re, fld->xnu_n, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            sf2d_yp(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yp(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yp(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_yp(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            sf2d_ym(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_ym(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_ym(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sf2d_ym(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void selective_filter2d_y(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                sf2d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            sf2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Selective Filter x dispatchers [base on "dux" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline sf3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sf3d_xc(fld->K, fld->r, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xc(fld->Ku, fld->ru, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xc(fld->Kv, fld->rv, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xc(fld->Kw, fld->rw, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xc(fld->Ke, fld->re, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sf3d_xP(fld->K, fld->r, fld->xnu_n, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xP(fld->Ku, fld->ru, fld->xnu_n, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xP(fld->Kv, fld->rv, fld->xnu_n, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xP(fld->Kw, fld->rw, fld->xnu_n, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xP(fld->Ke, fld->re, fld->xnu_n, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sf3d_xp(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xp(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xp(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xp(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xp(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sf3d_xm(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xm(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xm(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xm(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_xm(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void selective_filter3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                sf3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            sf3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Selective Filter y dispatchers [base on "duy" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline sf3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sf3d_yc(fld->K, fld->r, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yc(fld->Ku, fld->ru, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yc(fld->Kv, fld->rv, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yc(fld->Kw, fld->rw, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yc(fld->Ke, fld->re, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sf3d_yP(fld->K, fld->r, fld->xnu_n, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yP(fld->Ku, fld->ru, fld->xnu_n, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yP(fld->Kv, fld->rv, fld->xnu_n, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yP(fld->Kw, fld->rw, fld->xnu_n, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yP(fld->Ke, fld->re, fld->xnu_n, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sf3d_yp(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yp(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yp(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yp(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_yp(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sf3d_ym(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_ym(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_ym(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_ym(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_ym(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void selective_filter3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                sf3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            sf3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Selective Filter z dispatchers [base on "duz" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline sf3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sf3d_zc(fld->K, fld->r, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zc(fld->Ku, fld->ru, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zc(fld->Kv, fld->rv, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zc(fld->Kw, fld->rw, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zc(fld->Ke, fld->re, fld->xnu_n, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sf3d_zP(fld->K, fld->r, fld->xnu_n, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zP(fld->Ku, fld->ru, fld->xnu_n, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zP(fld->Kv, fld->rv, fld->xnu_n, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zP(fld->Kw, fld->rw, fld->xnu_n, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zP(fld->Ke, fld->re, fld->xnu_n, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sf3d_zp(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zp(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zp(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zp(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zp(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sf3d_zm(fld->K, fld->r, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zm(fld->Ku, fld->ru, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zm(fld->Kv, fld->rv, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zm(fld->Kw, fld->rw, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sf3d_zm(fld->Ke, fld->re, fld->xnu_n, fld->xnu_0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void selective_filter3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                sf3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            sf3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Laplacian Filter dispatchers
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d Laplacian Filter x dispatchers [base on "lfx" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline lf2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            lf2d_xc(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            lf2d_xP(fld->E, fld->p, fld->P3x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            lf2d_xp(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            lf2d_xm(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static lf2d_x_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        lf2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_lf.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_lf, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->lfx_stime = fmin(fld->lfx_stime, get_time(&start_loop, &end_loop));
}


void static lf2d_x_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            lf2d_x_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->lfx_gtime = fmin(fld->lfx_gtime, get_time(&start, &end));
}


void laplacian_filter2d_x(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->lfx_call >= max_gcalls){
        lf2d_x_func(fld);
    } else if (fld->lfx_lock < fld->dmns_n){
        lf2d_x_sing(fld);
    } else {
        lf2d_x_glob(fld);
        fld->lfx_call += 1;

        if (fld->lfx_gtime > fld->lfx_stime) {
            lf2d_x_func = lf2d_x_sing;
            fld->lfx_glob = 0;
        } else {
            lf2d_x_func = lf2d_x_glob;
            fld->lfx_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->lfx_gtime > 1.5 * fld->lfx_stime || fld->lfx_stime > 1.5 * fld->lfx_gtime) {
            fld->lfx_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Laplacian Filter y dispatchers [base on "lfy" threads]
////////////////////////////////////////////////////////////////////////////////


void static inline lf2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            lf2d_yc(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            lf2d_yP(fld->E, fld->p, fld->P3y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            lf2d_yp(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            lf2d_ym(fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static lf2d_y_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        lf2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_lf.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_lf, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->lfy_stime = fmin(fld->lfy_stime, get_time(&start_loop, &end_loop));
}


void static lf2d_y_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            lf2d_y_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->lfy_gtime = fmin(fld->lfy_gtime, get_time(&start, &end));
}


void laplacian_filter2d_y(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->lfy_call >= max_gcalls){
        lf2d_y_func(fld);
    } else if (fld->lfy_lock < fld->dmns_n){
        lf2d_y_sing(fld);
    } else {
        lf2d_y_glob(fld);
        fld->lfy_call += 1;

        if (fld->lfy_gtime > fld->lfy_stime) {
            lf2d_y_func = lf2d_y_sing;
            fld->lfy_glob = 0;
        } else {
            lf2d_y_func = lf2d_y_glob;
            fld->lfy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->lfy_gtime > 1.5 * fld->lfy_stime || fld->lfy_stime > 1.5 * fld->lfy_gtime) {
            fld->lfy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Laplacian Filter x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline lf3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            lf3d_xc(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            lf3d_xP(fld->E, fld->p, fld->P3x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            lf3d_xp(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            lf3d_xm(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static lf3d_x_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        lf3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_lf.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_lf, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->lfx_stime = fmin(fld->lfx_stime, get_time(&start_loop, &end_loop));
}


void static lf3d_x_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            lf3d_x_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->lfx_gtime = fmin(fld->lfx_gtime, get_time(&start, &end));
}


void laplacian_filter3d_x(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->lfx_call >= max_gcalls){
        lf3d_x_func(fld);
    } else if (fld->lfx_lock < fld->dmns_n){
        lf3d_x_sing(fld);
    } else {
        lf3d_x_glob(fld);
        fld->lfx_call += 1;

        if (fld->lfx_gtime > fld->lfx_stime) {
            lf3d_x_func = lf3d_x_sing;
            fld->lfx_glob = 0;
        } else {
            lf3d_x_func = lf3d_x_glob;
            fld->lfx_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->lfx_gtime > 1.5 * fld->lfx_stime || fld->lfx_stime > 1.5 * fld->lfx_gtime) {
            fld->lfx_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Laplacian Filter y dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline lf3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            lf3d_yc(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            lf3d_yP(fld->E, fld->p, fld->P3y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            lf3d_yp(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            lf3d_ym(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static lf3d_y_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        lf3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_lf.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_lf, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->lfy_stime = fmin(fld->lfy_stime, get_time(&start_loop, &end_loop));
}


void static lf3d_y_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            lf3d_y_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->lfy_gtime = fmin(fld->lfy_gtime, get_time(&start, &end));
}


void laplacian_filter3d_y(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->lfy_call >= max_gcalls){
        lf3d_y_func(fld);
    } else if (fld->lfy_lock < fld->dmns_n){
        lf3d_y_sing(fld);
    } else {
        lf3d_y_glob(fld);
        fld->lfy_call += 1;

        if (fld->lfy_gtime > fld->lfy_stime) {
            lf3d_y_func = lf3d_y_sing;
            fld->lfy_glob = 0;
        } else {
            lf3d_y_func = lf3d_y_glob;
            fld->lfy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->lfy_gtime > 1.5 * fld->lfy_stime || fld->lfy_stime > 1.5 * fld->lfy_gtime) {
            fld->lfy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Laplacian Filter z dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline lf3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            lf3d_zc(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            lf3d_zP(fld->E, fld->p, fld->P3z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            lf3d_zp(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            lf3d_zm(fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static lf3d_z_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        lf3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_lf.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_lf, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->lfz_stime = fmin(fld->lfz_stime, get_time(&start_loop, &end_loop));
}


void static lf3d_z_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            lf3d_z_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->lfz_gtime = fmin(fld->lfz_gtime, get_time(&start, &end));
}


void laplacian_filter3d_z(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->lfz_call >= max_gcalls){
        lf3d_z_func(fld);
    } else if (fld->lfz_lock < fld->dmns_n){
        lf3d_z_sing(fld);
    } else {
        lf3d_z_glob(fld);
        fld->lfz_call += 1;

        if (fld->lfz_gtime > fld->lfz_stime) {
            lf3d_z_func = lf3d_z_sing;
            fld->lfz_glob = 0;
        } else {
            lf3d_z_func = lf3d_z_glob;
            fld->lfz_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->lfz_gtime > 1.5 * fld->lfz_stime || fld->lfz_stime > 1.5 * fld->lfz_gtime) {
            fld->lfz_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Shock Capture dispatchers
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d Shock Capture x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sc2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sc2d_xc(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xc(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xc(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xc(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            sc2d_xP(fld->K, fld->r, fld->F, fld->P5x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xP(fld->Ku, fld->ru, fld->F, fld->P5x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xP(fld->Kv, fld->rv, fld->F, fld->P5x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xP(fld->Ke, fld->re, fld->F, fld->P5x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            sc2d_xp(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xp(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xp(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xp(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            sc2d_xm(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xm(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xm(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_xm(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static sc2d_x_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        if (dmns[c].sc_flag == 1) {
            clock_gettime(CLOCK_MONOTONIC, &start);
            sc2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_sc.cpu);
            clock_gettime(CLOCK_MONOTONIC, &end);
            set_thread_number(&dmns[c].thread_info_sc, get_time(&start, &end));
        } else {
            dmns[c].sc_flag = 0;
        }
    }
}


void static sc2d_x_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                sc2d_x_dispatcher(fld, &dmns[c], 1);
            } else {
                dmns[c].sc_flag = 0;
            }
        }
    }
}


void shock_capture2d_x(fields2d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    fld->scx_call = 0;
    for (c = 0; c < size; c++) {
        dmns[c].sc_flag |= any_nonzero2d_x(fld->F, fld->ny, dmns[c].fscm,
                                           dmns[c].ixmin, dmns[c].ixmax,
                                           dmns[c].iymin, dmns[c].iymax);
        if (dmns[c].sc_flag == 1) fld->scx_call++;
    }

    if (fld->scx_call >= max_gcalls){
        sc2d_x_glob(fld);
    } else {
        sc2d_x_sing(fld);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Shock Capture y dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sc2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sc2d_yc(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yc(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yc(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yc(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            sc2d_yP(fld->K, fld->r, fld->F, fld->P5y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yP(fld->Ku, fld->ru, fld->F, fld->P5y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yP(fld->Kv, fld->rv, fld->F, fld->P5y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yP(fld->Ke, fld->re, fld->F, fld->P5y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            sc2d_yp(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yp(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yp(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_yp(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            sc2d_ym(fld->K, fld->r, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_ym(fld->Ku, fld->ru, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_ym(fld->Kv, fld->rv, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            sc2d_ym(fld->Ke, fld->re, fld->F, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static sc2d_y_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        if (dmns[c].sc_flag == 1) {
            clock_gettime(CLOCK_MONOTONIC, &start);
            sc2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_sc.cpu);
            clock_gettime(CLOCK_MONOTONIC, &end);
            set_thread_number(&dmns[c].thread_info_sc, get_time(&start, &end));
        } else {
            dmns[c].sc_flag = 0;
        }
    }
}


void static sc2d_y_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                sc2d_y_dispatcher(fld, &dmns[c], 1);
            } else {
                dmns[c].sc_flag = 0;
            }
        }
    }
}


void shock_capture2d_y(fields2d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    fld->scy_call = 0;
    for (c = 0; c < size; c++) {
        dmns[c].sc_flag |= any_nonzero2d_y(fld->F, fld->ny, dmns[c].fscm,
                                           dmns[c].ixmin, dmns[c].ixmax,
                                           dmns[c].iymin, dmns[c].iymax);
        if (dmns[c].sc_flag == 1) fld->scy_call++;
    }

    if (fld->scy_call >= max_gcalls){
        sc2d_y_glob(fld);
    } else {
        sc2d_y_sing(fld);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Shock Capture x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sc3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sc3d_xc(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xc(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xc(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xc(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xc(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sc3d_xP(fld->K, fld->r, fld->F, fld->P5x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xP(fld->Ku, fld->ru, fld->F, fld->P5x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xP(fld->Kv, fld->rv, fld->F, fld->P5x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xP(fld->Kw, fld->rw, fld->F, fld->P5x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xP(fld->Ke, fld->re, fld->F, fld->P5x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sc3d_xp(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xp(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xp(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xp(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xp(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sc3d_xm(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xm(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xm(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xm(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_xm(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static sc3d_x_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        if (dmns[c].sc_flag == 1) {
            clock_gettime(CLOCK_MONOTONIC, &start);
            sc3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_sc.cpu);
            clock_gettime(CLOCK_MONOTONIC, &end);
            set_thread_number(&dmns[c].thread_info_sc, get_time(&start, &end));
        } else {
            dmns[c].sc_flag = 0;
        }
    }
}


void static sc3d_x_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                sc3d_x_dispatcher(fld, &dmns[c], 1);
            } else {
            dmns[c].sc_flag = 0;
            }
        }
    }
}


void shock_capture3d_x(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    fld->scx_call = 0;
    for (c = 0; c < size; c++) {
        dmns[c].sc_flag |= any_nonzero3d_x(fld->F, fld->ny, fld->nz, dmns[c].fscm,
                                           dmns[c].ixmin, dmns[c].ixmax,
                                           dmns[c].iymin, dmns[c].iymax,
                                           dmns[c].izmin, dmns[c].izmax);
        if (dmns[c].sc_flag == 1) fld->scx_call++;
    }

    if (fld->scx_call >= max_gcalls){
        sc3d_x_glob(fld);
    } else {
        sc3d_x_sing(fld);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Shock Capture y dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sc3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sc3d_yc(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yc(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yc(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yc(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yc(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sc3d_yP(fld->K, fld->r, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yP(fld->Ku, fld->ru, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yP(fld->Kv, fld->rv, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yP(fld->Kw, fld->rw, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yP(fld->Ke, fld->re, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sc3d_yp(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yp(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yp(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yp(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_yp(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sc3d_ym(fld->K, fld->r, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_ym(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_ym(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_ym(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_ym(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static sc3d_y_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        if (dmns[c].sc_flag == 1) {
            clock_gettime(CLOCK_MONOTONIC, &start);
            sc3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_sc.cpu);
            clock_gettime(CLOCK_MONOTONIC, &end);
            set_thread_number(&dmns[c].thread_info_sc, get_time(&start, &end));
        } else {
            dmns[c].sc_flag = 0;
        }
    }
}


void static sc3d_y_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                sc3d_y_dispatcher(fld, &dmns[c], 1);
            } else {
                dmns[c].sc_flag = 0;
            }
        }
    }
}


void shock_capture3d_y(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    fld->scy_call = 0;
    for (c = 0; c < size; c++) {
        dmns[c].sc_flag |= any_nonzero3d_y(fld->F, fld->ny, fld->nz, dmns[c].fscm,
                                           dmns[c].ixmin, dmns[c].ixmax,
                                           dmns[c].iymin, dmns[c].iymax,
                                           dmns[c].izmin, dmns[c].izmax);
        if (dmns[c].sc_flag == 1) fld->scy_call++;
    }

    if (fld->scy_call >= max_gcalls){
        sc3d_y_glob(fld);
    } else {
        sc3d_y_sing(fld);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d SC z dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sc3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;

    switch(scm){
        case 11:
            sc3d_zc(fld->K,  fld->r,  fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zc(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zc(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zc(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zc(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            sc3d_zP(fld->K,  fld->r,  fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zP(fld->Ku, fld->ru, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zP(fld->Kv, fld->rv, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zP(fld->Kw, fld->rw, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zP(fld->Ke, fld->re, fld->F, fld->P5y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            sc3d_zp(fld->K,  fld->r,  fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zp(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zp(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zp(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zp(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            sc3d_zm(fld->K,  fld->r,  fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zm(fld->Ku, fld->ru, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zm(fld->Kv, fld->rv, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zm(fld->Kw, fld->rw, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            sc3d_zm(fld->Ke, fld->re, fld->F, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static sc3d_z_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        if (dmns[c].sc_flag == 1) {
            clock_gettime(CLOCK_MONOTONIC, &start);
            sc3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_sc.cpu);
            clock_gettime(CLOCK_MONOTONIC, &end);
            set_thread_number(&dmns[c].thread_info_sc, get_time(&start, &end));
        } else {
            dmns[c].sc_flag = 0;
        }
    }
}


void static sc3d_z_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            if (dmns[c].sc_flag == 1) {
                sc3d_z_dispatcher(fld, &dmns[c], 1);
            } else {
                dmns[c].sc_flag = 0;
            }
        }
    }
}


void shock_capture3d_z(fields3d *fld){

    const unsigned int max_gcalls = 500;
    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    fld->scz_call = 0;
    for (c = 0; c < size; c++) {
        dmns[c].sc_flag |= any_nonzero3d_z(fld->F, fld->ny, fld->nz, dmns[c].fscm,
                                           dmns[c].ixmin, dmns[c].ixmax,
                                           dmns[c].iymin, dmns[c].iymax,
                                           dmns[c].izmin, dmns[c].izmax);
        if (dmns[c].sc_flag == 1) fld->scz_call++;
    }

    if (fld->scz_call >= max_gcalls){
        sc3d_z_glob(fld);
    } else {
        sc3d_z_sing(fld);
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// SIGMA dispatchers
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d SIGMA x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sg2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;
    unsigned int flag = 1;

    switch(scm){
        case 11:
            flag = sg2d_xc(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            flag = sg2d_xP(fld->F, fld->E, fld->p, fld->P3x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            flag = sg2d_xp(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            flag = sg2d_xm(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
    dmns->sc_flag = flag;
}


void static sg2d_x_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        sg2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_sg.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_sg, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->sgx_stime = fmin(fld->sgx_stime, get_time(&start_loop, &end_loop));
}


void static sg2d_x_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            sg2d_x_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->sgx_gtime = fmin(fld->sgx_gtime, get_time(&start, &end));
}


void sigma2d_x(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->sgx_call >= max_gcalls){
        sg2d_x_func(fld);
    } else if (fld->sgx_lock < fld->dmns_n){
        sg2d_x_sing(fld);
    } else {
        sg2d_x_glob(fld);
        fld->sgx_call += 1;

        if (fld->sgx_gtime > fld->sgx_stime) {
            sg2d_x_func = sg2d_x_sing;
            fld->sgx_glob = 0;
        } else {
            sg2d_x_func = sg2d_x_glob;
            fld->sgx_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->sgx_gtime > 1.5 * fld->sgx_stime || fld->sgx_stime > 1.5 * fld->sgx_gtime) {
            fld->sgx_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d SIGMA y dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sg2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->fscm;
    unsigned int flag = 1;

    switch(scm){
        case 11:
            flag = sg2d_yc(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            flag = sg2d_yP(fld->F, fld->E, fld->p, fld->P3y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            flag = sg2d_yp(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            flag = sg2d_ym(fld->F, fld->E, fld->p, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
    dmns->sc_flag = flag;
}


void static sg2d_y_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        sg2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_sg.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_sg, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->sgy_stime = fmin(fld->sgy_stime, get_time(&start_loop, &end_loop));
}


void static sg2d_y_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            sg2d_y_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->sgy_gtime = fmin(fld->sgy_gtime, get_time(&start, &end));
}


void sigma2d_y(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->sgy_call >= max_gcalls){
        sg2d_y_func(fld);
    } else if (fld->sgy_lock < fld->dmns_n){
        sg2d_y_sing(fld);
    } else {
        sg2d_y_glob(fld);
        fld->sgy_call += 1;

        if (fld->sgy_gtime > fld->sgy_stime) {
            sg2d_y_func = sg2d_y_sing;
            fld->sgy_glob = 0;
        } else {
            sg2d_y_func = sg2d_y_glob;
            fld->sgy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->sgy_gtime > 1.5 * fld->sgy_stime || fld->sgy_stime > 1.5 * fld->sgy_gtime) {
            fld->sgy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d SIGMA x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sg3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;
    unsigned int flag = 1;

    switch(scm){
        case 11:
            flag = sg3d_xc(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            flag = sg3d_xP(fld->F, fld->E, fld->p, fld->P3x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            flag = sg3d_xp(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            flag = sg3d_xm(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
    dmns->sc_flag = flag;
}


void static sg3d_x_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        sg3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_sg.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_sg, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->sgx_stime = fmin(fld->sgx_stime, get_time(&start_loop, &end_loop));
}


void static sg3d_x_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            sg3d_x_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->sgx_gtime = fmin(fld->sgx_gtime, get_time(&start, &end));
}


void sigma3d_x(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->sgx_call >= max_gcalls){
        sg3d_x_func(fld);
    } else if (fld->sgx_lock < fld->dmns_n){
        sg3d_x_sing(fld);
    } else {
        sg3d_x_glob(fld);
        fld->sgx_call += 1;

        if (fld->sgx_gtime > fld->sgx_stime) {
            sg3d_x_func = sg3d_x_sing;
            fld->sgx_glob = 0;
        } else {
            sg3d_x_func = sg3d_x_glob;
            fld->sgx_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->sgx_gtime > 1.5 * fld->sgx_stime || fld->sgx_stime > 1.5 * fld->sgx_gtime) {
            fld->sgx_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d SIGMA y dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sg3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;
    unsigned int flag = 1;

    switch(scm){
        case 11:
            flag = sg3d_yc(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            flag = sg3d_yP(fld->F, fld->E, fld->p, fld->P3y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            flag = sg3d_yp(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            flag = sg3d_ym(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
    dmns->sc_flag = flag;
}


void static sg3d_y_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        sg3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_sg.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_sg, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->sgy_stime = fmin(fld->sgy_stime, get_time(&start_loop, &end_loop));
}


void static sg3d_y_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            sg3d_y_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->sgy_gtime = fmin(fld->sgy_gtime, get_time(&start, &end));
}


void sigma3d_y(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->sgy_call >= max_gcalls){
        sg3d_y_func(fld);
    } else if (fld->sgy_lock < fld->dmns_n){
        sg3d_y_sing(fld);
    } else {
        sg3d_y_glob(fld);
        fld->sgy_call += 1;

        if (fld->sgy_gtime > fld->sgy_stime) {
            sg3d_y_func = sg3d_y_sing;
            fld->sgy_glob = 0;
        } else {
            sg3d_y_func = sg3d_y_glob;
            fld->sgy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->sgy_gtime > 1.5 * fld->sgy_stime || fld->sgy_stime > 1.5 * fld->sgy_gtime) {
            fld->sgy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d SIGMA z dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline sg3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->fscm;
    unsigned int flag = 1;

    switch(scm){
        case 11:
            flag = sg3d_zc(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            flag = sg3d_zP(fld->F, fld->E, fld->p, fld->P3y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            flag = sg3d_zp(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            flag = sg3d_zm(fld->F, fld->E, fld->p, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
    dmns->sc_flag = flag;
}


void static sg3d_z_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        sg3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_sg.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_sg, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->sgz_stime = fmin(fld->sgz_stime, get_time(&start_loop, &end_loop));
}


void static sg3d_z_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            sg3d_z_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->sgz_gtime = fmin(fld->sgz_gtime, get_time(&start, &end));
}


void sigma3d_z(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->sgz_call >= max_gcalls){
        sg3d_z_func(fld);
    } else if (fld->sgz_lock < fld->dmns_n){
        sg3d_z_sing(fld);
    } else {
        sg3d_z_glob(fld);
        fld->sgz_call += 1;

        if (fld->sgz_gtime > fld->sgz_stime) {
            sg3d_z_func = sg3d_z_sing;
            fld->sgz_glob = 0;
        } else {
            sg3d_z_func = sg3d_z_glob;
            fld->sgz_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->sgz_gtime > 1.5 * fld->sgz_stime || fld->sgz_stime > 1.5 * fld->sgz_gtime) {
            fld->sgz_call = max_gcalls;
        }
    }
}



////////////////////////////////////////////////////////////////////////////////
// Global SF
////////////////////////////////////////////////////////////////////////////////


void static inline update_glob2d(double *restrict vf, double *restrict v,
                                 const unsigned int nx, const unsigned int ny,
                                 const unsigned int threads){

    unsigned int ix, iy, idx, idy;

    switch(threads){
        case 1:
            for (ix = 0; ix < nx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy < ny; iy++) {
                    idy = idx + iy;
                    *(v + idy) -= *(vf + idy);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
            {
                #pragma omp for nowait
                for (ix = 0; ix < nx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy < ny; iy++) {
                        idy = idx + iy;
                        *(v + idy) -= *(vf + idy);
                    }
                }
            }
    }
}


void static inline update_glob3d(double *restrict vf, double *restrict v,
                                 const unsigned int nx, const unsigned int ny, const unsigned int nz,
                                 const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;

    switch(threads){
        case 1:
            for (ix = 0; ix < nx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy < ny; iy++) {
                    idy = idx + iy;

                    for (iz = 0; iz < nz; iz++) {
                        idz = idy + iz;
                        *(v + idz) -= *(vf + idz);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
            {
                #pragma omp for nowait
                for (ix = 0; ix < nx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy < ny; iy++) {
                        idy = idx + iy;

                        for (iz = 0; iz < nz; iz++) {
                            idz = idy + iz;
                            *(v + idz) -= *(vf + idz);
                        }
                    }
                }
            }
    }
}


void sf2d_x(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int threads){

    sf2d_xc(vf, v, xnu_n, ny,        5, nx - 6,      0, ny - 1, threads);
    sf2d_xp(vf, v, xnu_n, xnu_0, ny, 0, 4,           0, ny - 1, 1);
    sf2d_xm(vf, v, xnu_n, xnu_0, ny, nx - 5, nx - 1, 0, ny - 1, 1);
    update_glob2d(vf, v, nx, ny, threads);
}


void sf2d_y(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int threads){

    sf2d_yc(vf, v, xnu_n, ny,        0, nx - 1, 5, ny - 6, threads);
    sf2d_yp(vf, v, xnu_n, xnu_0, ny, 0, nx - 1, 0, 4, 1);
    sf2d_ym(vf, v, xnu_n, xnu_0, ny, 0, nx - 1, ny - 5, nx - 1, 1);
    update_glob2d(vf, v, nx, ny, threads);
}


void sf3d_x(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads){

    sf3d_xc(vf, v, xnu_n,        ny, nz, 5, nx - 6,      0, ny - 1, 0, nz - 1, threads);
    sf3d_xp(vf, v, xnu_n, xnu_0, ny, nz, 0, 4,           0, ny - 1, 0, nz - 1, 1);
    sf3d_xm(vf, v, xnu_n, xnu_0, ny, nz, nx - 5, nx - 1, 0, ny - 1, 0, nz - 1, 1);
    update_glob3d(vf, v, nx, ny, nz, threads);
}


void sf3d_y(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads){

    sf3d_yc(vf, v, xnu_n,        ny, nz, 0, nx - 1, 5, ny - 6,      0, nz - 1, threads);
    sf3d_yp(vf, v, xnu_n, xnu_0, ny, nz, 0, nx - 1, 0, 4,           0, nz - 1, 1);
    sf3d_ym(vf, v, xnu_n, xnu_0, ny, nz, 0, nx - 1, ny - 5, ny - 1, 0, nz - 1, 1);
    update_glob3d(vf, v, nx, ny, nz, threads);
}

void sf3d_z(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned threads){

    sf3d_zc(vf, v, xnu_n,        ny, nz, 0, nx - 1, 0, ny - 1, 5, nz - 6, threads);
    sf3d_zp(vf, v, xnu_n, xnu_0, ny, nz, 0, nx - 1, 0, ny - 1, 0, 4, 1);
    sf3d_zm(vf, v, xnu_n, xnu_0, ny, nz, 0, nx - 1, 0, ny - 1, nz - 5, nz - 1, 1);
    update_glob3d(vf, v, nx, ny, nz, threads);
}


////////////////////////////////////////////////////////////////////////////////
// Global LF
////////////////////////////////////////////////////////////////////////////////


void lf2d_x(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int threads){

    lf2d_xc(vf, v, ny, 1, nx - 2, 0, ny - 1, threads);
    lf2d_xp(vf, v, ny, 0, 1, 0, ny - 1, 1);
    lf2d_xm(vf, v, ny, nx-2, nx-1, 0, ny - 1, 1);
}


void lf2d_y(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int threads){

    lf2d_yc(vf, v, ny, 0, nx - 1, 1, ny - 2, threads);
    lf2d_yp(vf, v, ny, 0, nx - 1, 0, 1, 1);
    lf2d_ym(vf, v, ny, 0, nx - 1, ny-2, nx-1, 1);
}


void lf3d_x(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads){

    lf3d_xc(vf, v, ny, nz, 1, nx - 2,      0, ny - 1, 0, nz - 1, threads);
    lf3d_xp(vf, v, ny, nz, 0, 1,           0, ny - 1, 0, nz - 1, 1);
    lf3d_xm(vf, v, ny, nz, nx - 2, nx - 1, 0, ny - 1, 0, nz - 1, 1);
}


void lf3d_y(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads){

    lf3d_yc(vf, v, ny, nz, 0, nx - 1, 1, ny - 2,      0, nz - 1, threads);
    lf3d_yp(vf, v, ny, nz, 0, nx - 1, 0, 1,           0, nz - 1, 1);
    lf3d_ym(vf, v, ny, nz, 0, nx - 1, ny - 2, nz - 1, 0, nz - 1, 1);
}

void lf3d_z(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned threads){

    lf3d_yc(vf, v, ny, nz, 0, nx - 1, 0, ny - 1, 1, nz - 2, threads);
    lf3d_yp(vf, v, ny, nz, 0, nx - 1, 0, ny - 1, 0, 1, 1);
    lf3d_ym(vf, v, ny, nz, 0, nx - 1, 0, ny - 1, nz - 2, nz - 1, 1);
}