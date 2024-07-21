#ifndef FIELDS
#define FIELDS
#include <time.h>
#include <float.h>   // For DBL_MAX constant
#include "cobjects.h"

////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////

inline double get_time(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) * 1e-9;
}


inline int argmin1d(double * arr, unsigned int size) {

    double min_value = DBL_MAX;  // Initialize min_value to maximum possible integer
    int min_index = -1;          // Initialize min_index to -1 (invalid index)
    unsigned int i;

    // Iterate through array to find minimum value and its index
    for (i = 0; i < size; i++) {
        if (*(arr + i) < min_value) {
            min_value = *(arr + i);
            min_index = i;
        }
    }
    return min_index;
}


inline void set_thread_number(ThreadInfo *info, double elapsed_time) {

    unsigned int idx;

    if (info->lock == 1){
        return;
    }

    if (elapsed_time < 10e-6) {
        info->lock = 1;
        *(info->glock) += 1;
        return;
    }

    if (info->calls < info->cycles){
        idx = info->calls / info->means;
        *(info->timings + idx) = fmin(*(info->timings + idx), elapsed_time);
        info->calls += 1;

        // stop optimization if time with cpu[n] is 2 times slower than with cpu[n-1]
        if (idx > 0){
            if (*(info->timings + idx) / *(info->timings + idx - 1) > 2.) {
                info->lock = 1;
                *(info->glock) += 1;
                idx = argmin1d(info->timings, idx);
            }
        }

    // wait 1 iteration before locking the thread count to get the best execution time possible
    // } else if (info->calls == info->cycles) {
    //     idx = argmin1d(info->timings, info->ncpus);
    //     info->calls += 1;
    } else {
        idx = argmin1d(info->timings, info->ncpus);
        info->lock = 1;
        *(info->glock) +=1;
    }
    info->cpu = *(info->cpus + idx);
}


inline unsigned int any_nonzero2d(const double *restrict m, unsigned int ny,
                                  unsigned int ixmin, unsigned int ixmax,
                                  unsigned int iymin, unsigned int iymax) {

    unsigned int ix, iy, rstart, rstop;
    const double zero = 0.0;

    // Parallelism is pointless.
    // Performance depends on the presence or absence of non zeros
    for (ix = ixmin; ix <= ixmax; ix++) {
        rstart = ix * ny + iymin;
        rstop = ix * ny + iymax;
        for (iy = rstart; iy <= rstop; iy++) {
            if (m[iy] != zero) {
                return 1;
            }
        }
    }
    return 0;
}


unsigned int any_nonzero2d_x(const double *restrict m, unsigned int ny,
                             const int scm,
                             unsigned int ixmin, unsigned int ixmax,
                             unsigned int iymin, unsigned int iymax) {

    unsigned int flag_xp = 1;
    unsigned int flag_xm = 1;

    switch(scm){
        case 11:
            flag_xm = any_nonzero2d(m, ny, ixmin-1, ixmin-1, iymin, iymax);
            flag_xp = any_nonzero2d(m, ny, ixmax+1, ixmax+1, iymin, iymax);
            return flag_xm == 1 || flag_xp == 1;
        case 5:
            return any_nonzero2d(m, ny, ixmax+1, ixmax+1, iymin, iymax);
        case -5:
            return any_nonzero2d(m, ny, ixmin-1, ixmin-1, iymin, iymax);
        default:
            return 1;
    }
}


unsigned int any_nonzero2d_y(const double *restrict m, unsigned int ny,
                             const int scm,
                             unsigned int ixmin, unsigned int ixmax,
                             unsigned int iymin, unsigned int iymax) {

    unsigned int flag_yp = 1;
    unsigned int flag_ym = 1;

    switch(scm){
        case 11:
            flag_ym = any_nonzero2d(m, ny, ixmin, ixmax, iymin-1, iymin-1);
            flag_yp = any_nonzero2d(m, ny, ixmin, ixmax, iymax+1, iymax+1);
            return flag_ym == 1 || flag_yp == 1;
        case 5:
            return any_nonzero2d(m, ny, ixmin, ixmax, iymax+1, iymax+1);
        case -5:
            return any_nonzero2d(m, ny, ixmin, ixmax, iymin-1, iymin-1);
        default:
            return 1;
    }
}


inline unsigned int any_nonzero3d(const double *restrict m, unsigned int ny, unsigned int nz,
                                  unsigned int ixmin, unsigned int ixmax,
                                  unsigned int iymin, unsigned int iymax,
                                  unsigned int izmin, unsigned int izmax) {

    unsigned int ix, iy, iz, idx, idy;
    unsigned int nynz = ny * nz;
    const double zero = 0.0;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                if (m[idy + iz] != zero) {
                    return 1;
                }
            }
        }
    }
    return 0;
}



unsigned int any_nonzero3d_x(const double *restrict m, unsigned int ny, unsigned int nz,
                                    const int scm,
                                    unsigned int ixmin, unsigned int ixmax,
                                    unsigned int iymin, unsigned int iymax,
                                    unsigned int izmin, unsigned int izmax) {

    unsigned int flag_xp = 1;
    unsigned int flag_xm = 1;

    switch(scm){
        case 11:
            flag_xm = any_nonzero3d(m, ny, nz, ixmin-1, ixmin-1, iymin, iymax, izmin, izmax);
            flag_xp = any_nonzero3d(m, ny, nz, ixmax+1, ixmax+1, iymin, iymax, izmin, izmax);
            return flag_xm || flag_xp;
        case 5:
            return any_nonzero3d(m, ny, nz, ixmax+1, ixmax+1, iymin, iymax, izmin, izmax);
        case -5:
            return any_nonzero3d(m, ny, nz, ixmin-1, ixmin-1, iymin, iymax, izmin, izmax);
        default:
            return 1;
    }
}


unsigned int any_nonzero3d_y(const double *restrict m, unsigned int ny, unsigned int nz,
                             const int scm,
                             unsigned int ixmin, unsigned int ixmax,
                             unsigned int iymin, unsigned int iymax,
                             unsigned int izmin, unsigned int izmax) {

    unsigned int flag_yp = 1;
    unsigned int flag_ym = 1;

    switch(scm){
        case 11:
            flag_ym = any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin-1, iymin-1, izmin, izmax);
            flag_yp = any_nonzero3d(m, ny, nz, ixmin, ixmax, iymax+1, iymax+1, izmin, izmax);
            return flag_ym || flag_yp;
        case 5:
            return any_nonzero3d(m, ny, nz, ixmin, ixmax, iymax+1, iymax+1, izmin, izmax);
        case -5:
            return any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin-1, iymin-1, izmin, izmax);
        default:
            return 1;
    }
}


unsigned int any_nonzero3d_z(const double *restrict m, unsigned int ny, unsigned int nz,
                             const int scm,
                             unsigned int ixmin, unsigned int ixmax,
                             unsigned int iymin, unsigned int iymax,
                             unsigned int izmin, unsigned int izmax) {

    unsigned int flag_zp = 1;
    unsigned int flag_zm = 1;

    switch(scm){
        case 11:
            flag_zm = any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin, iymax, izmin-1, izmin-1);
            flag_zp = any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin, iymax, izmax+1, izmax+1);
            return flag_zm || flag_zp;
        case 5:
            return any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin, iymax, izmax+1, izmax+1);
        case -5:
            return any_nonzero3d(m, ny, nz, ixmin, ixmax, iymin, iymax, izmin-1, izmin-1);
        default:
            return 1;
    }
}



void pressure2d(fields2d *fld);
void pressure3d(fields3d *fld);

void global_pressure2d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict re,
                       const double gamma,
                       const unsigned int nx, const unsigned int ny,
                       const unsigned int threads);
void global_pressure3d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict rw,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny, const unsigned int nz,
                       const unsigned int threads);

void velocity2d(fields2d *fld, unsigned int old);
void velocity3d(fields3d *fld, unsigned int old);

void global_velocity2d(double *restrict p,
                       const double *restrict r, const double *restrict ru, const double *restrict rv,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny,
                       const unsigned int threads);
void global_velocity3d(double *restrict p,
                       const double *restrict r, const double *restrict ru,
                       const double *restrict rv, const double *restrict rw,
                       const double *restrict re, const double gamma,
                       const unsigned int nx, const unsigned int ny, const unsigned int nz,
                       const unsigned int threads);

void vorticity2d(fields2d *fld);
void vorticity3d(fields3d *fld);

void copy2d(fields2d *fld);
void copy3d(fields3d *fld);

void tes_update2d(fields2d *fld, const double *restrict profile, const double alpha);
void tes_update3d(fields3d *fld, const double *restrict profile, const double alpha);

void phys2num2d(fields2d *fld);
void num2phys2d(fields2d *fld);

void phys2num3d(fields3d *fld);
void num2phys3d(fields3d *fld);

void residual2d(fields2d *fld);
void residual3d(fields3d *fld);


////////////////////////////////////////////////////////////////////////////////
// Pointers
////////////////////////////////////////////////////////////////////////////////

void (*pa2d_func)(fields2d *);
void (*vn2d_func)(fields2d *, unsigned int);
void (*cp2d_func)(fields2d *);  // Consider also __builtin_memcpy which can be faster than
void (*tes2d_func)(fields2d *, const double *restrict profile, const double alpha);
void (*n2p2d_func)(fields2d *);
void (*p2n2d_func)(fields2d *);

void (*pa3d_func)(fields3d *);
void (*vn3d_func)(fields3d *, unsigned int);
void (*cp3d_func)(fields3d *);
void (*tes3d_func)(fields3d *, const double *restrict profile, const double alpha);
void (*n2p3d_func)(fields3d *);
void (*p2n3d_func)(fields3d *);

#endif