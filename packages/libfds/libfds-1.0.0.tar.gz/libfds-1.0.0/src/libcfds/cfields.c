#include <stdio.h>
#include <math.h>
#include <omp.h>
#include <time.h>
#include "cobjects.h"
#include "cfields.h"
#include "kernels_diffraw.h"
#include "kernels_diffsub.h"



////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// PRESSURE
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d/3d Pressure computation for subdomains [checked]
////////////////////////////////////////////////////////////////////////////////


void static inline pressure2d_s(const double *restrict r, const double *restrict ru,
                                const double *restrict rv, const double *restrict re,
                                double *restrict p, const double gm1,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            *(p + idy) = (*(re + idy) - 0.5 * (*(ru + idy) * *(ru + idy) +
                                               *(rv + idy) * *(rv + idy)) / *(r + idy)) * gm1;
        }
    }
}


void static inline pressure2d_p(const double *restrict r, const double *restrict ru,
                                const double *restrict rv, const double *restrict re,
                                double *restrict p, const double gm1,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int threads){

    unsigned int ix, iy, idx, idy;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                *(p + idy) = (*(re + idy) - 0.5 * (*(ru + idy) * *(ru + idy) +
                                                   *(rv + idy) * *(rv + idy)) / *(r + idy)) * gm1;
            }
        }
    }
}


void static inline pressure3d_s(const double *restrict r, const double *restrict ru,
                                const double *restrict rv, const double *restrict rw,
                                const double *restrict re, double *restrict p,
                                const double gm1,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                *(p + idz) = (*(re + idz) - 0.5 * (*(ru + idz) * *(ru + idz) +
                                                   *(rv + idz) * *(rv + idz) +
                                                   *(rw + idz) * *(rw + idz)) / *(r + idz)) * gm1;
            }
        }
    }
}


void static inline pressure3d_p(const double *restrict r, const double *restrict ru,
                                const double *restrict rv, const double *restrict rw,
                                const double *restrict re, double *restrict p,
                                const double gm1,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    *(p + idz) = (*(re + idz) - 0.5 * (*(ru + idz) * *(ru + idz) +
                                                       *(rv + idz) * *(rv + idz) +
                                                       *(rw + idz) * *(rw + idz)) / *(r + idz)) * gm1;
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Pressure dispatcher [checked]
////////////////////////////////////////////////////////////////////////////////


void static inline pa_dispatch2d(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            pressure2d_s(fld->r, fld->ru, fld->rv, fld->re, fld->p, fld->gm1,
                         fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            pressure2d_p(fld->r, fld->ru, fld->rv, fld->re, fld->p, fld->gm1,
                         fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static pa_dispatch2d_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            pa_dispatch2d(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->pup_gtime = fmin(fld->pup_gtime, get_time(&start, &end));
}


void static pa_dispatch2d_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        pa_dispatch2d(fld, &dmns[c], dmns[c].thread_info_pup.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_pup, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->pup_stime = fmin(fld->pup_stime, get_time(&start_loop, &end_loop));
}


void pressure2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->pup_call >= max_gcalls){
        pa2d_func(fld);
    } else if (fld->pup_lock < fld->dmns_n){
        pa_dispatch2d_sing(fld);
    } else {
        pa_dispatch2d_glob(fld);
        fld->pup_call += 1;
        //printf("%d / %d / %lf / %lf\n", fld->pup_call, fld->pup_glob, fld->pup_gtime, fld->pup_stime);

        if (fld->pup_gtime > fld->pup_stime) {
            pa2d_func = pa_dispatch2d_sing;
            fld->pup_glob = 0;
        } else {
            pa2d_func = pa_dispatch2d_glob;
            fld->pup_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->pup_gtime > 1.5 * fld->pup_stime || fld->pup_stime > 1.5 * fld->pup_gtime) {
            fld->pup_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Pressure dispatcher [checked]
////////////////////////////////////////////////////////////////////////////////


void static inline pa_dispatch3d(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            pressure3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p, fld->gm1,
                         fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            pressure3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p, fld->gm1,
                         fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static pa_dispatch3d_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            pa_dispatch3d(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->pup_gtime = fmin(fld->pup_gtime, get_time(&start, &end));
}


void static pa_dispatch3d_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        pa_dispatch3d(fld, &dmns[c], dmns[c].thread_info_pup.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_pup, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->pup_stime = fmin(fld->pup_stime, get_time(&start_loop, &end_loop));
}


void pressure3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->pup_call >= max_gcalls){
        pa3d_func(fld);
    } else if (fld->pup_lock < fld->dmns_n){
        pa_dispatch3d_sing(fld);
    } else {
        pa_dispatch3d_glob(fld);
        fld->pup_call += 1;

        if (fld->pup_gtime > fld->pup_stime) {
            pa3d_func = pa_dispatch3d_sing;
            fld->pup_glob = 0;
        } else {
            pa3d_func = pa_dispatch3d_glob;
            fld->pup_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->pup_gtime > 1.5 * fld->pup_stime || fld->pup_stime > 1.5 * fld->pup_gtime) {
            fld->pup_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// Pressure computation for global domain [checked]
////////////////////////////////////////////////////////////////////////////////


void global_pressure2d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict re,
                       const double gamma,
                       const unsigned int nx, const unsigned int ny,
                       const unsigned int threads){

    unsigned int i;
    const unsigned int size = nx * ny;
    const unsigned int mp = threads > 1 && size > 90000;
    const double gm1 = gamma - 1;

    switch(mp){
        case 0:
            for (i = 0; i < size; i++) {
                *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                               *(rv + i) * *(rv + i)) / *(r + i)) * gm1;
                }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(i)
            {
                #pragma omp for nowait
                for (i = 0; i < size; i++) {
                    *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                                   *(rv + i) * *(rv + i)) / *(r + i)) * gm1;
            }
        }
    }
}


void global_pressure3d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict rw,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny, const unsigned int nz,
                       const unsigned int threads){

    unsigned int i;
    const unsigned int size = nx * ny * nz;
    const unsigned int mp = threads > 1 && size > 90000;
    const double gm1 = gamma - 1;

    switch(mp){
        case 0:
            for (i = 0; i < size; i++) {
                *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                               *(rv + i) * *(rv + i) +
                                               *(rw + i) * *(rw + i)) / *(r + i)) * gm1;
                }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(i)
            {
                #pragma omp for nowait
                for (i = 0; i < size; i++) {
                    *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                                   *(rv + i) * *(rv + i) +
                                                   *(rw + i) * *(rw + i)) / *(r + i)) * gm1;
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// VELOCITY
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d Velocity computation for subdomains [checked]
////////////////////////////////////////////////////////////////////////////////


void static inline velocity2d_s(const double *restrict r,
                                const double *restrict ru, const double *restrict rv,
                                double *restrict Eu, double *restrict Ev,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double invr;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            invr = 1. / r[idy];
            Eu[idy] = invr * ru[idy];
            Ev[idy] = invr * rv[idy];
        }
    }
}


void static inline velocity2d_p(const double *restrict r,
                                const double *restrict ru, const double *restrict rv,
                                double *restrict Eu, double *restrict Ev,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double invr;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, invr)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                invr = 1. / r[idy];
                Eu[idy] = invr * ru[idy];
                Ev[idy] = invr * rv[idy];
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Velocity computation for subdomains [checked]
////////////////////////////////////////////////////////////////////////////////


void static inline velocity3d_s(const double *restrict r,
                                const double *restrict ru, const double *restrict rv, const double *restrict rw,
                                double *restrict Eu, double *restrict Ev, double *restrict Ew,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                invr = 1. / r[idz];
                Eu[idz] = invr * ru[idz];
                Ev[idz] = invr * rv[idz];
                Ew[idz] = invr * rw[idz];
            }
        }
    }
}


void static inline velocity3d_p(const double *restrict r,
                                const double *restrict ru, const double *restrict rv, const double *restrict rw,
                                double *restrict Eu, double *restrict Ev, double *restrict Ew,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, invr)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    invr = 1. / r[idz];
                    Eu[idz] = invr * ru[idz];
                    Ev[idz] = invr * rv[idz];
                    Ew[idz] = invr * rw[idz];
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Velocity dispatcher
////////////////////////////////////////////////////////////////////////////////


void static inline vn_dispatch2d(fields2d *fld, domain2d *dmns, const unsigned int old, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            if (old == 0) {
                velocity2d_s(fld->r, fld->ru, fld->rv, fld->Eu, fld->Ev,
                             fld->ny, ixmin, ixmax, iymin, iymax);
            } else {
                // Note : for crv, Ku = ru / J and K = r / J, so ru = Ku/K
                velocity2d_s(fld->K, fld->Ku, fld->Kv, fld->E, fld->F,
                             fld->ny, ixmin, ixmax, iymin, iymax);
            }
            break;
        default:
            if (old == 0) {
            velocity2d_p(fld->r, fld->ru, fld->rv, fld->Eu, fld->Ev,
                         fld->ny, ixmin, ixmax, iymin, iymax, threads);
            } else {
            velocity2d_p(fld->K, fld->Ku, fld->Kv, fld->E, fld->F,
                         fld->ny, ixmin, ixmax, iymin, iymax, threads);
            }
    }
}


void static vn_dispatch2d_glob(fields2d *fld, const unsigned int old){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            vn_dispatch2d(fld, &dmns[c], old, 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->vup_gtime = fmin(fld->vup_gtime, get_time(&start, &end));
}


void static vn_dispatch2d_sing(fields2d *fld, const unsigned int old){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        vn_dispatch2d(fld, &dmns[c], old, dmns[c].thread_info_vup.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_vup, get_time(&start, &end));

    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->vup_stime = fmin(fld->vup_stime, get_time(&start_loop, &end_loop));
}


// vn2d is also used in another unit (vfluxes). So for now, there is no optimization
// for one among vn2d used by vrt/vfluxes... otherwise it leas dot segfault sinces 
// vn2d_func is not defined in one of the two translation units.
// The solution seems to compile all .c file at the same time.
void (*vn2d_func)(fields2d *, const unsigned int) = vn_dispatch2d_sing;


void velocity2d(fields2d *fld, const unsigned int old){

    const unsigned int max_gcalls = 2;

    if (fld->vup_call >= max_gcalls){
        vn2d_func(fld, old);
    } else if (fld->vup_lock < fld->dmns_n){
        vn_dispatch2d_sing(fld, old);
    } else {
        vn_dispatch2d_glob(fld, old);
        fld->vup_call += 1;
        if (fld->vup_gtime > fld->vup_stime) {
            vn2d_func = vn_dispatch2d_sing;
            fld->vup_glob = 0;
        } else {
            vn2d_func = vn_dispatch2d_glob;
            fld->vup_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->vup_gtime > 1.5 * fld->vup_stime || fld->vup_stime > 1.5 * fld->vup_gtime) {
            fld->vup_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Velocity dispatcher
////////////////////////////////////////////////////////////////////////////////


void static inline vn_dispatch3d(fields3d *fld, domain3d *dmns, const unsigned int old, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            if (old == 0){
                velocity3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->Eu, fld->Ev, fld->Ew,
                             fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            } else{
                // Note : for crv, Ku = ru / J and K = r / J, so ru = Ku/K
                velocity3d_s(fld->K, fld->Ku, fld->Kv, fld->Kw, fld->E, fld->F, fld->G,
                             fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            }
            break;
        default:
            if (old == 0){
                velocity3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->Eu, fld->Ev, fld->Ew,
                             fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            } else{
                velocity3d_p(fld->K, fld->Ku, fld->Kv, fld->Kw, fld->E, fld->F, fld->G,
                             fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            }
    }
}


void static vn_dispatch3d_glob(fields3d *fld, unsigned int old){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            vn_dispatch3d(fld, &dmns[c], old, 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->vup_gtime = fmin(fld->vup_gtime, get_time(&start, &end));
}


void static vn_dispatch3d_sing(fields3d *fld, unsigned int old){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        vn_dispatch3d(fld, &dmns[c], old, dmns[c].thread_info_vup.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_vup, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->vup_stime = fmin(fld->vup_stime, get_time(&start_loop, &end_loop));
}


void velocity3d(fields3d *fld, unsigned int old){

    const unsigned int max_gcalls = 2;

    if (fld->vup_call >= max_gcalls){
        vn3d_func(fld, old);
    } else if (fld->vup_lock < fld->dmns_n){
        vn_dispatch3d_sing(fld, old);
    } else {
        vn_dispatch3d_glob(fld, old);
        fld->vup_call += 1;
        if (fld->vup_gtime > fld->vup_stime) {
            vn3d_func = vn_dispatch3d_sing;
            fld->vup_glob = 0;
        } else {
            vn3d_func = vn_dispatch3d_glob;
            fld->vup_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->vup_gtime > 1.5 * fld->vup_stime || fld->vup_stime > 1.5 * fld->vup_gtime) {
            fld->vup_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// Velocity computation for global domain
////////////////////////////////////////////////////////////////////////////////


void global_velocity2d(double *restrict p,
                       const double *restrict r, const double *restrict ru, const double *restrict rv,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny,
                       const unsigned int threads){

    unsigned int i;
    const unsigned int size = nx * ny;
    const unsigned int mp = threads > 1 && size > 90000;
    const double gm1 = gamma - 1;

    switch(mp){
        case 0:
            for (i = 0; i < size; i++) {
                *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                               *(rv + i) * *(rv + i)) / *(r + i)) * gm1;
                }
        break;
        default:
            #pragma omp parallel num_threads(threads) private(i)
            {
                #pragma omp for nowait
                for (i = 0; i < size; i++) {
                    *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                                   *(rv + i) * *(rv + i)) / *(r + i)) * gm1;
                }
            }
    }
}


void global_velocity3d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict rw,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny, const unsigned int nz,
                       const unsigned int threads){

    unsigned int i;
    const unsigned int size = nx * ny * nz;
    const unsigned int mp = threads > 1 && size > 90000;
    const double gm1 = gamma - 1;

    switch(mp){
        case 0:
            for (i = 0; i < size; i++) {
                *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                               *(rv + i) * *(rv + i) +
                                               *(rw + i) * *(rw + i)) / *(r + i)) * gm1;
                }
        break;
        default:
            #pragma omp parallel num_threads(threads) private(i)
            {
                #pragma omp for nowait
                for (i = 0; i < size; i++) {
                    *(p + i) = (*(re + i) - 0.5 * (*(ru + i) * *(ru + i) +
                                                   *(rv + i) * *(rv + i) +
                                                   *(rw + i) * *(rw + i)) / *(r + i)) * gm1;
                }
            }
    }
}



////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Vorticity
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// 2d vorticity z dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline vrt2d_z_yx_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2xc_s(fld->wz, fld->Ev, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2xc_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2xP_s(fld->wz, fld->Ev, *fld->odx, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2xP_v(fld->wz, fld->Ev, fld->odx_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2xp_s(fld->wz, fld->Ev, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2xp_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2xm_s(fld->wz, fld->Ev, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2xm_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static inline vrt2d_z_xy_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2sub_yc_s(fld->wz, fld->Eu, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2sub_yc_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2sub_yP_s(fld->wz, fld->Eu, *fld->ody, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2sub_yP_v(fld->wz, fld->Eu, fld->ody_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2sub_yp_s(fld->wz, fld->Eu, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2sub_yp_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2sub_ym_s(fld->wz, fld->Eu, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2sub_ym_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static inline vrt2d_z_yx(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt2d_z_yx_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt2d_z_yx_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


void static inline vrt2d_z_xy(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt2d_z_xy_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt2d_z_xy_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d vorticity (wz, )
////////////////////////////////////////////////////////////////////////////////


void vorticity2d(fields2d *fld){
    // update velocity (Eu, Ev)
    velocity2d(fld, 0);

    // wz
    vrt2d_z_yx(fld);
    vrt2d_z_xy(fld);
}


////////////////////////////////////////////////////////////////////////////////
// 3d vorticity z dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline vrt3d_z_yx_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3xc_s(fld->wz, fld->Ev, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3xc_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3xP_s(fld->wz, fld->Ev, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3xP_v(fld->wz, fld->Ev, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3xp_s(fld->wz, fld->Ev, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3xp_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3xm_s(fld->wz, fld->Ev, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3xm_v(fld->wz, fld->Ev, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vrt3d_z_xy_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3sub_yc_s(fld->wz, fld->Eu, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3sub_yc_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3sub_yP_s(fld->wz, fld->Eu, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3sub_yP_v(fld->wz, fld->Eu, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3sub_yp_s(fld->wz, fld->Eu, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3sub_yp_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3sub_ym_s(fld->wz, fld->Eu, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3sub_ym_v(fld->wz, fld->Eu, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static vrt3d_z_yx(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_z_yx_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_z_yx_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


void static vrt3d_z_xy(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_z_xy_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_z_xy_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d vorticity y dispatchers
////////////////////////////////////////////////////////////////////////////////

void static inline vrt3d_y_xz_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3zc_s(fld->wy, fld->Eu, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3zc_v(fld->wy, fld->Eu, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3zP_s(fld->wy, fld->Eu, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3zP_v(fld->wy, fld->Eu, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3zp_s(fld->wy, fld->Eu, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3zp_v(fld->wy, fld->Eu, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3zm_s(fld->wy, fld->Eu, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3zm_v(fld->wy, fld->Eu, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vrt3d_y_zx_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3sub_xc_s(fld->wy, fld->Ew, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3sub_xc_v(fld->wy, fld->Ew, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3sub_xP_s(fld->wy, fld->Ew, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3sub_xP_v(fld->wy, fld->Ew, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3sub_xp_s(fld->wy, fld->Ew, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3sub_xp_v(fld->wy, fld->Ew, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3sub_xm_s(fld->wy, fld->Ew, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3sub_xm_v(fld->wy, fld->Ew, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static vrt3d_y_xz(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_y_xz_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_y_xz_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


void static vrt3d_y_zx(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_y_zx_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_y_zx_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d vorticity x dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline vrt3d_x_zy_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3yc_s(fld->wx, fld->Ew, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3yc_v(fld->wx, fld->Ew, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3yP_s(fld->wx, fld->Ew, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3yP_v(fld->wx, fld->Ew, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3yp_s(fld->wx, fld->Ew, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3yp_v(fld->wx, fld->Ew, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3ym_s(fld->wx, fld->Ew, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3ym_v(fld->wx, fld->Ew, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vrt3d_x_yz_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3sub_zc_s(fld->wx, fld->Ev, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3sub_zc_v(fld->wx, fld->Ev, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3sub_zP_s(fld->wx, fld->Ev, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3sub_zP_v(fld->wx, fld->Ev, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3sub_zp_s(fld->wx, fld->Ev, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3sub_zp_v(fld->wx, fld->Ev, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3sub_zm_s(fld->wx, fld->Ev, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3sub_zm_v(fld->wx, fld->Ev, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static vrt3d_x_zy(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_x_zy_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_x_zy_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


void static vrt3d_x_yz(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vrt3d_x_yz_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vrt3d_x_yz_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d vorticity (wx, wy, wz)
////////////////////////////////////////////////////////////////////////////////


void vorticity3d(fields3d *fld){
    // update velocity (Eu, Ev, Ew)
    velocity3d(fld, 0);

    // wx
    vrt3d_x_zy(fld);
    vrt3d_x_yz(fld);

    // wy
    vrt3d_y_xz(fld);
    vrt3d_y_zx(fld);

    // wz
    vrt3d_z_yx(fld);
    vrt3d_z_xy(fld);
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// COPY
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// 2d copy computation for subdomains
////////////////////////////////////////////////////////////////////////////////


void static inline copy2d_s(const double *restrict r, const double *restrict ru,
                            const double *restrict rv,const double *restrict re,
                            double *restrict K, double *restrict Ku,
                            double *restrict Kv, double *restrict Ke,
                            double *restrict Tk, double gm1_over_cpmcv,
                            const unsigned int ny,
                            const unsigned int ixmin, const unsigned int ixmax,
                            const unsigned int iymin, const unsigned int iymax,
                            const unsigned int vsc){

    unsigned int ix, iy, idx, idy;
    double ru2 = 0;
    double rv2 = 0;
    double invr = 0;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            *(K + idy) = *(r + idy);
            *(Ku + idy) = *(ru + idy);
            *(Kv + idy) = *(rv + idy);
            *(Ke + idy) = *(re + idy);
            if (vsc == 1){
                // compute Tk (1/J cancel if crv)
                invr = 1. / *(r + idy);
                ru2 = *(ru + idy) * *(ru + idy);
                rv2 = *(rv + idy) * *(rv + idy);
                *(Tk + idy) = gm1_over_cpmcv * (*(re + idy) - 0.5 * invr * (ru2 + rv2)) * invr;
            }
        }
    }
}


void static inline copy2d_p(const double *restrict r, const double *restrict ru,
                            const double *restrict rv,const double *restrict re,
                            double *restrict K, double *restrict Ku,
                            double *restrict Kv, double *restrict Ke,
                            double *restrict Tk, double gm1_over_cpmcv,
                            const unsigned int ny,
                            const unsigned int ixmin, const unsigned int ixmax,
                            const unsigned int iymin, const unsigned int iymax,
                            const unsigned int vsc, const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double ru2 = 0;
    double rv2 = 0;
    double invr = 0;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, invr, ru2, rv2)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                *(K + idy) = *(r + idy);
                *(Ku + idy) = *(ru + idy);
                *(Kv + idy) = *(rv + idy);
                *(Ke + idy) = *(re + idy);
                if (vsc == 1){
                    // compute Tk (1/J cancel if crv)
                    invr = 1. / *(r + idy);
                    ru2 = *(ru + idy) * *(ru + idy);
                    rv2 = *(rv + idy) * *(rv + idy);
                    *(Tk + idy) = gm1_over_cpmcv * (*(re + idy) - 0.5 * invr * (ru2 + rv2)) * invr;
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d copy for subdomains
////////////////////////////////////////////////////////////////////////////////


void static inline copy3d_s(const double *restrict r, const double *restrict ru,
                            const double *restrict rv, const double *restrict rw,
                            const double *restrict re,
                            double *restrict K, double *restrict Ku,
                            double *restrict Kv, double *restrict Kw,
                            double *restrict Ke,
                            double *restrict Tk, double gm1_over_cpmcv,
                            const unsigned int ny, const unsigned int nz,
                            const unsigned int ixmin, const unsigned int ixmax,
                            const unsigned int iymin, const unsigned int iymax,
                            const unsigned int izmin, const unsigned int izmax,
                            const unsigned int vsc){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double ru2 = 0;
    double rv2 = 0;
    double rw2 = 0;
    double invr = 0;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                *(K + idz) = *(r + idz);
                *(Ku + idz) = *(ru + idz);
                *(Kv + idz) = *(rv + idz);
                *(Kw + idz) = *(rw + idz);
                *(Ke + idz) = *(re + idz);
                if (vsc == 1){
                    // compute Tk (1/J cancel if crv)
                    invr = 1. / *(r + idz);
                    ru2 = *(ru + idz) * *(ru + idz);
                    rv2 = *(rv + idz) * *(rv + idz);
                    rw2 = *(rw + idz) * *(rw + idz);
                    *(Tk + idz) = gm1_over_cpmcv * (*(re + idz) - 0.5 * invr * (ru2 + rv2 + rw2)) * invr;
                }
            }
        }
    }
}


void static inline copy3d_p(const double *restrict r, const double *restrict ru,
                            const double *restrict rv, const double *restrict rw,
                            const double *restrict re,
                            double *restrict K, double *restrict Ku,
                            double *restrict Kv, double *restrict Kw,
                            double *restrict Ke,
                            double *restrict Tk, double gm1_over_cpmcv,
                            const unsigned int ny, const unsigned int nz,
                            const unsigned int ixmin, const unsigned int ixmax,
                            const unsigned int iymin, const unsigned int iymax,
                            const unsigned int izmin, const unsigned int izmax,
                            const unsigned int vsc, const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double ru2 = 0;
    double rv2 = 0;
    double rw2 = 0;
    double invr = 0;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, invr, ru2, rv2, rw2)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    *(K + idz) = *(r + idz);
                    *(Ku + idz) = *(ru + idz);
                    *(Kv + idz) = *(rv + idz);
                    *(Kw + idz) = *(rw + idz);
                    *(Ke + idz) = *(re + idz);
                    if (vsc == 1){
                        // compute Tk (1/J cancel if crv)
                        invr = 1. / *(r + idz);
                        ru2 = *(ru + idz) * *(ru + idz);
                        rv2 = *(rv + idz) * *(rv + idz);
                        rw2 = *(rw + idz) * *(rw + idz);
                        *(Tk + idz) = gm1_over_cpmcv * (*(re + idz) - 0.5 * invr * (ru2 + rv2 + rw2)) * invr;
                    }
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d copy dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline cp_dispatch2d(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            copy2d_s(fld->r, fld->ru, fld->rv, fld->re,
                     fld->K, fld->Ku, fld->Kv, fld->Ke,
                     fld->Tk, fld->gm1_over_cpmcv,
                     fld->ny, ixmin, ixmax, iymin, iymax, fld->vsc);
            break;
        default:
            copy2d_p(fld->r, fld->ru, fld->rv, fld->re,
                     fld->K, fld->Ku, fld->Kv, fld->Ke,
                     fld->Tk, fld->gm1_over_cpmcv,
                     fld->ny, ixmin, ixmax, iymin, iymax, fld->vsc, threads);
    }
}


void static cp_dispatch2d_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            cp_dispatch2d(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->cpy_gtime = fmin(fld->cpy_gtime, get_time(&start, &end));
}


void static cp_dispatch2d_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        cp_dispatch2d(fld, &dmns[c], dmns[c].thread_info_cpy.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_cpy, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->cpy_stime = fmin(fld->cpy_stime, get_time(&start_loop, &end_loop));
}


void copy2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->cpy_call >= max_gcalls){
        cp2d_func(fld);
    } else if (fld->cpy_lock < fld->dmns_n){
        cp_dispatch2d_sing(fld);
    } else {
        cp_dispatch2d_glob(fld);
        fld->cpy_call += 1;

        if (fld->cpy_gtime > fld->cpy_stime) {
            cp2d_func = cp_dispatch2d_sing;
            fld->cpy_glob = 0;
        } else {
            cp2d_func = cp_dispatch2d_glob;
            fld->cpy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->cpy_gtime > 1.5 * fld->cpy_stime || fld->cpy_stime > 1.5 * fld->cpy_gtime) {
            fld->cpy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d copy dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline cp_dispatch3d(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            copy3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re,
                     fld->K, fld->Ku, fld->Kv, fld->Kw, fld->Ke,
                     fld->Tk, fld->gm1_over_cpmcv,
                     fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax,
                     fld->vsc);
            break;
        default:
            copy3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re,
                     fld->K, fld->Ku, fld->Kv, fld->Kw, fld->Ke,
                     fld->Tk, fld->gm1_over_cpmcv,
                     fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax,
                     fld->vsc, threads);
    }
}


void static cp_dispatch3d_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            cp_dispatch3d(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->cpy_gtime = fmin(fld->cpy_gtime, get_time(&start, &end));
}


void static cp_dispatch3d_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        cp_dispatch3d(fld, &dmns[c], dmns[c].thread_info_cpy.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_cpy, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->cpy_stime = fmin(fld->cpy_stime, get_time(&start_loop, &end_loop));
}


void copy3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->cpy_call >= max_gcalls){
        cp3d_func(fld);
    } else if (fld->cpy_lock < fld->dmns_n){
        cp_dispatch3d_sing(fld);
    } else {
        cp_dispatch3d_glob(fld);
        fld->cpy_call += 1;

        if (fld->cpy_gtime > fld->cpy_stime) {
            cp3d_func = cp_dispatch3d_sing;
            fld->cpy_glob = 0;
        } else {
            cp3d_func = cp_dispatch3d_glob;
            fld->cpy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->cpy_gtime > 1.5 * fld->cpy_stime || fld->cpy_stime > 1.5 * fld->cpy_gtime) {
            fld->cpy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// TES update
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// 2d tes update
////////////////////////////////////////////////////////////////////////////////

void static inline tes2d_s(double *restrict r, double *restrict re, const double *restrict profile,
                           const double alpha, const double gm1_over_c,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double e;

    for (ix = ixmin; ix <= ixmax; ix++) {

        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {

            idy = idx + iy;

            e = alpha * *(profile + idy);
            *(re + idy) += e;
            *(r + idy) += e * gm1_over_c;
        }
    }
}


void static inline tes2d_p(double *restrict r, double *restrict re, const double *restrict profile,
                           const double alpha, const double gm1_over_c,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double e;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, e)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {

            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {

                idy = idx + iy;

                e = alpha * *(profile + idy);
                *(re + idy) += e;
                *(r + idy) += e * gm1_over_c;
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d tes dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline tes_dispatch2d(fields2d *fld, domain2d *dmns,
                                  const double *restrict profile, const double alpha, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            tes2d_s(fld->r, fld->re, profile, alpha, fld->gm1_over_c,
                    fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            tes2d_p(fld->r, fld->re, profile, alpha, fld->gm1_over_c,
                    fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static tes_update2d_glob(fields2d *fld, const double *restrict profile, const double alpha){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            tes_dispatch2d(fld, &dmns[c], profile, alpha, 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->tes_gtime = fmin(fld->tes_gtime, get_time(&start, &end));
}


void static tes_update2d_sing(fields2d *fld, const double *restrict profile, const double alpha){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        tes_dispatch2d(fld, &dmns[c], profile, alpha, dmns[c].thread_info_tes.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_tes, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->tes_stime = fmin(fld->tes_stime, get_time(&start_loop, &end_loop));
}


void tes_update2d(fields2d *fld, const double *restrict profile, const double alpha){

    const unsigned int max_gcalls = 2;

    if (fld->tes_call >= max_gcalls){
        tes2d_func(fld, profile, alpha);
    } else if (fld->tes_lock < fld->dmns_n){
        tes_update2d_sing(fld, profile, alpha);
    } else {
        tes_update2d_glob(fld, profile, alpha);
        fld->tes_call += 1;

        if (fld->tes_gtime > fld->tes_stime) {
            tes2d_func = tes_update2d_sing;
            fld->tes_glob = 0;
        } else {
            tes2d_func = tes_update2d_glob;
            fld->tes_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->tes_gtime > 1.5 * fld->tes_stime || fld->tes_stime > 1.5 * fld->tes_gtime) {
            fld->tes_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d tes update
////////////////////////////////////////////////////////////////////////////////


void static inline tes3d_s(double *restrict r, double *restrict re, const double *restrict profile,
                           const double alpha, const double gm1_over_c,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double e;

    for (ix = ixmin; ix <= ixmax; ix++) {

        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {

            idy = idx + iy;

            for (iz = izmin; iz <= izmax; iz++) {

                idz = idy + iz;

                e = alpha * *(profile + idz);
                *(re + idz) += e;
                *(r + idz) += e * gm1_over_c;
            }
        }
    }
}


void static inline tes3d_p(double *restrict r, double *restrict re, const double *restrict profile,
                           const double alpha, const double gm1_over_c,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax,
                           const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double e;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, e)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {

            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {

                idy = idx + iy;

                for (iz = izmin; iz <= izmax; iz++) {

                    idz = idy + iz;

                    e = alpha * *(profile + idz);
                    *(re + idz) += e;
                    *(r + idz) += e * gm1_over_c;
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d tes dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline tes_dispatch3d(fields3d *fld, domain3d *dmns, 
                                  const double *restrict profile, const double alpha, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            tes3d_s(fld->r, fld->re, profile, alpha, fld->gm1_over_c,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            tes3d_p(fld->r, fld->re, profile, alpha, fld->gm1_over_c,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static tes_update3d_glob(fields3d *fld, const double *restrict profile, const double alpha){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            tes_dispatch3d(fld, &dmns[c], profile, alpha, 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->tes_gtime = fmin(fld->tes_gtime, get_time(&start, &end));
}


void static tes_update3d_sing(fields3d *fld, const double *restrict profile, const double alpha){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        tes_dispatch3d(fld, &dmns[c], profile, alpha, dmns[c].thread_info_tes.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_tes, get_time(&start, &end));

    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->tes_stime = fmin(fld->tes_stime, get_time(&start_loop, &end_loop));
}


void tes_update3d(fields3d *fld, const double *restrict profile, const double alpha){

    const unsigned int max_gcalls = 2;

    if (fld->tes_call >= max_gcalls){
        tes3d_func(fld, profile, alpha);
    } else if (fld->tes_lock < fld->dmns_n){
        tes_update3d_sing(fld, profile, alpha);
    } else {
        tes_update3d_glob(fld, profile, alpha);
        fld->tes_call += 1;

        if (fld->tes_gtime > fld->tes_stime) {
            tes3d_func = tes_update3d_sing;
            fld->tes_glob = 0;
        } else {
            tes3d_func = tes_update3d_glob;
            fld->tes_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->tes_gtime > 1.5 * fld->tes_stime || fld->tes_stime > 1.5 * fld->tes_gtime) {
            fld->tes_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// num2phy
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// 2d num2phys/phys2num [only test n2p for opt]
////////////////////////////////////////////////////////////////////////////////

void static inline n2p2d_s(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double J;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            J = 1. / *(invJ + idy);
            *(r + idy) *= J;
            *(ru + idy) *= J;
            *(rv + idy) *= J;
            *(re + idy) *= J;
        }
    }
}


void static inline n2p2d_p(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double J;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, J)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                J = 1. / *(invJ + idy);
                *(r + idy) *= J;
                *(ru + idy) *= J;
                *(rv + idy) *= J;
                *(re + idy) *= J;
            }
        }
    }
}


void static inline p2n2d_s(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            *(r + idy) *= *(invJ + idy);
            *(ru + idy) *= *(invJ + idy);
            *(rv + idy) *= *(invJ + idy);
            *(re + idy) *= *(invJ + idy);
        }
    }
}


void static inline p2n2d_p(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int threads){

    unsigned int ix, iy, idx, idy;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                *(r + idy) *= *(invJ + idy);
                *(ru + idy) *= *(invJ + idy);
                *(rv + idy) *= *(invJ + idy);
                *(re + idy) *= *(invJ + idy);
            }
        }
    }
}


void static n2p2d_dispatch(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            n2p2d_s(fld->r, fld->ru, fld->rv, fld->re, fld->invJ,
                    fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            n2p2d_p(fld->r, fld->ru, fld->rv, fld->re, fld->invJ,
                    fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}



void static p2n2d_dispatch(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            p2n2d_s(fld->r, fld->ru, fld->rv, fld->re, fld->invJ,
                    fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            p2n2d_p(fld->r, fld->ru, fld->rv, fld->re, fld->invJ,
                    fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d num2phys/phys2num dispatchers
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// 3d num2phys/phys2num
////////////////////////////////////////////////////////////////////////////////


void static inline n2p3d_s(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict rw, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double J;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                J = 1. / *(invJ + idz);
                *(r + idz) *= J;
                *(ru + idz) *= J;
                *(rv + idz) *= J;
                *(rw + idz) *= J;
                *(re + idz) *= J;
            }
        }
    }
}


void static inline n2p3d_p(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict rw, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax,
                           const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    double J;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, J)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    J = 1. / *(invJ + idz);
                    *(r + idz) *= J;
                    *(ru + idz) *= J;
                    *(rv + idz) *= J;
                    *(rw + idz) *= J;
                    *(re + idz) *= J;
                }
            }
        }
    }
}


void static inline p2n3d_s(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict rw, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                *(r + idz) *= *(invJ + idz);
                *(ru + idz) *= *(invJ + idz);
                *(rv + idz) *= *(invJ + idz);
                *(rw + idz) *= *(invJ + idz);
                *(re + idz) *= *(invJ + idz);
            }
        }
    }
}


void static inline p2n3d_p(double *restrict r, double *restrict ru,
                           double *restrict rv, double *restrict rw, double *restrict re,
                           const double *restrict invJ,
                           const unsigned int ny, const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax,
                           const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    *(r + idz) *= *(invJ + idz);
                    *(ru + idz) *= *(invJ + idz);
                    *(rv + idz) *= *(invJ + idz);
                    *(rw + idz) *= *(invJ + idz);
                    *(re + idz) *= *(invJ + idz);
                }
            }
        }
    }
}



void static n2p3d_dispatch(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            n2p3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->invJ,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            n2p3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->invJ,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}



void static p2n3d_dispatch(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            p2n3d_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->invJ,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            p2n3d_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->invJ,
                    fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d num2phys/phys2num dispatchers
////////////////////////////////////////////////////////////////////////////////


void static p2n2d_update_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            p2n2d_dispatch(fld, &dmns[c], 1);
        }
    }
}


void static p2n2d_update_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;

    for (c = 0; c < size; c++) {
        p2n2d_dispatch(fld, &dmns[c], dmns[c].thread_info_n2p.cpu);
    }
}


void static n2p2d_update_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            n2p2d_dispatch(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->n2p_gtime = fmin(fld->n2p_gtime, get_time(&start, &end));
}


void static n2p2d_update_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        n2p2d_dispatch(fld, &dmns[c], dmns[c].thread_info_n2p.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_n2p, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->n2p_stime = fmin(fld->n2p_stime, get_time(&start_loop, &end_loop));
}


void static inline set_n2p2d(fields2d *fld){

    if (fld->n2p_gtime > fld->n2p_stime) {
        n2p2d_func = n2p2d_update_sing;
        p2n2d_func = p2n2d_update_sing;
        fld->n2p_glob = 0;
    } else {
        n2p2d_func = n2p2d_update_glob;
        p2n2d_func = p2n2d_update_glob;
        fld->n2p_glob = 1;
    }
}


void phys2num2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->n2p_call >= max_gcalls){
        p2n2d_func(fld);
    } else {
        p2n2d_update_sing(fld);
    }
}


void num2phys2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->n2p_call >= max_gcalls){
        n2p2d_func(fld);
    } else if (fld->n2p_lock < fld->dmns_n){
        n2p2d_update_sing(fld);
    } else {
        n2p2d_update_glob(fld);
        set_n2p2d(fld);
        fld->n2p_call += 1;

        // stop testing global dispatch if difference is too high.
        if (fld->n2p_gtime > 1.5 * fld->n2p_stime || fld->n2p_stime > 1.5 * fld->n2p_gtime) {
            fld->n2p_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d num2phys/phys2num dispatchers
////////////////////////////////////////////////////////////////////////////////


void static p2n3d_update_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;

    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            p2n3d_dispatch(fld, &dmns[c], 1);
        }
    }
}


void static p2n3d_update_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;

    for (c = 0; c < size; c++) {
        p2n3d_dispatch(fld, &dmns[c], dmns[c].thread_info_n2p.cpu);
    }
}


void static n2p3d_update_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            n2p3d_dispatch(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->n2p_gtime = fmin(fld->n2p_gtime, get_time(&start, &end));
}


void static n2p3d_update_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        n2p3d_dispatch(fld, &dmns[c], dmns[c].thread_info_n2p.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_n2p, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->n2p_stime = fmin(fld->n2p_stime, get_time(&start_loop, &end_loop));
}


void static inline set_n2p3d(fields3d *fld){

    if (fld->n2p_gtime > fld->n2p_stime) {
        n2p3d_func = n2p3d_update_sing;
        p2n3d_func = p2n3d_update_sing;
        fld->n2p_glob = 0;
    } else {
        n2p3d_func = n2p3d_update_glob;
        p2n3d_func = p2n3d_update_glob;
        fld->n2p_glob = 1;
    }
}


void phys2num3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->n2p_call >= max_gcalls){
        p2n3d_func(fld);
    } else {
        p2n3d_update_sing(fld);
    }
}


void num2phys3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->n2p_call >= max_gcalls){
        n2p3d_func(fld);
    } else if (fld->n2p_lock < fld->dmns_n){
        n2p3d_update_sing(fld);
    } else {
        n2p3d_update_glob(fld);
        set_n2p3d(fld);
        fld->n2p_call += 1;

        // stop testing global dispatch if difference is too high.
        if (fld->n2p_gtime > 1.5 * fld->n2p_stime || fld->n2p_stime > 1.5 * fld->n2p_gtime) {
            fld->n2p_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Residuals
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// 2d residuals
////////////////////////////////////////////////////////////////////////////////

void static inline res2d_s(double *res, const double *restrict p, const double p0, const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double pa;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            pa = *(p + idy) - p0;
            *res += pa * pa;
        }
    }
}


void static inline res2d_p(double *res, const double *restrict p, const double p0, const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double pa;
    double res_tmp = 0;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, pa) 
    {
        #pragma omp for nowait reduction(+:res_tmp)
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                pa = *(p + idy) - p0;
                res_tmp += pa * pa;
            }
        }
    }
    *res += res_tmp;
}


void residual2d(fields2d *fld){

    unsigned int c, ixmin, ixmax, iymin, iymax, threads;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        ixmin = dmns[c].ixmin;
        ixmax = dmns[c].ixmax;
        iymin = dmns[c].iymin;
        iymax = dmns[c].iymax;
        threads = dmns[c].thread_info_rsd.cpu;

        clock_gettime(CLOCK_MONOTONIC, &start);
        switch(threads){
            case 1:
                res2d_s(&(fld->rsd), fld->p, fld->p0, fld->ny, ixmin, ixmax, iymin, iymax);
                break;
            default:
                res2d_p(&(fld->rsd), fld->p, fld->p0, fld->ny, ixmin, ixmax, iymin, iymax, threads);
        }
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_rsd, get_time(&start, &end));
    }
    fld->rsd = sqrt(fld->rsd / fld->size);
}


////////////////////////////////////////////////////////////////////////////////
// 3d residuals
////////////////////////////////////////////////////////////////////////////////

void static inline res3d_s(double *res, const double *restrict p, const double p0, 
                           const unsigned int ny,const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double pa;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                pa = *(p + idz) - p0;
                *res += pa * pa;
            }
        }
    }
}


void static inline res3d_p(double *res, const double *restrict p, const double p0, 
                           const unsigned int ny,const unsigned int nz,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int izmin, const unsigned int izmax,
                           const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double pa;
    double res_tmp = 0;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, pa)
    {
        #pragma omp for nowait reduction(+:res_tmp)
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    pa = *(p + idz) - p0;
                    *res += pa * pa;
                }
            }
        }
    }
    *res += res_tmp;
}


void residual3d(fields3d *fld){

    unsigned int c, ixmin, ixmax, iymin, iymax, izmin, izmax, threads;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    for (c = 0; c < size; c++) {
        ixmin = dmns[c].ixmin;
        ixmax = dmns[c].ixmax;
        iymin = dmns[c].iymin;
        iymax = dmns[c].iymax;
        izmin = dmns[c].izmin;
        izmax = dmns[c].izmax;
        threads = dmns[c].thread_info_rsd.cpu;

        clock_gettime(CLOCK_MONOTONIC, &start);
        switch(threads){
            case 1:
                res3d_s(&(fld->rsd), fld->p, fld->p0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax);
                break;
            default:
                res3d_p(&(fld->rsd), fld->p, fld->p0, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
        }
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_rsd, get_time(&start, &end));
    }
    fld->rsd = sqrt(fld->rsd / fld->size);
}