#include <stdio.h>
#include <omp.h>
#include <math.h>
#include "kernels_sc.h"
#include "coefficients.h"


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// LF kernels
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// LF 2d
////////////////////////////////////////////////////////////////////////////////

void lf2d_xc(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vf += offset;

    const double *restrict v1m = v - ny;
    const double *restrict v1p = v + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    vf[idy] = -0.25 * v1p[idy] + 0.5 * v[idy] - 0.25 * v1m[idy];
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        vf[idy] = -0.25 * v1p[idy] + 0.5 * v[idy] - 0.25 * v1m[idy];
                }
            }
        }
    }
}


void lf2d_yc(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vf += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v1p = v + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    vf[idy] = -0.25 * v1p[idy] + 0.5 * v[idy] - 0.25 * v1m[idy];
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        vf[idy] = -0.25 * v1p[idy] + 0.5 * v[idy] - 0.25 * v1m[idy];
                }
            }
        }
    }
}


void lf2d_xP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Px = P + 1;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {

                idx = ix * ny;

                v0 = v + *(Px + ix) * ny;
                v1p = v + *(Px + ix + 1) * ny;
                v1m = v + *(Px + ix - 1) * ny;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    vf[idy] = -0.25 * v1p[iy] + 0.5 * v0[iy] - 0.25 * v1m[iy];
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, v0, v1m, v1p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {

                    idx = ix * ny;

                    v0 = v + *(Px + ix) * ny;
                    v1p = v + *(Px + ix + 1) * ny;
                    v1m = v + *(Px + ix - 1) * ny;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        vf[idy] = -0.25 * v1p[iy] + 0.5 * v0[iy] - 0.25 * v1m[iy];
                }
            }
        }
    }
}


void lf2d_yP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict vix;
    const unsigned int *restrict Py = P + 1;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;
                vix = v + idx;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    vf[idy] = -0.25 * *(vix + *(Py + iy + 1)) + 0.5 * *(vix + *(Py + iy)) - 0.25 * *(vix + *(Py + iy - 1));
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, vix)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;
                    vix = v + idx;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        vf[idy] = -0.25 * *(vix + *(Py + iy + 1)) + 0.5 * *(vix + *(Py + iy)) - 0.25 * *(vix + *(Py + iy - 1));
                }
            }
        }
    }
}


void lf2d_xp(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + ny;
    const double *restrict v2 = v1 + ny;

    for (iy = 0; iy <= my; iy++){
        vf0[iy] = 0.25 * v0[iy] - 0.50 * v1[iy] + 0.25 * v2[iy];
    }
    lf2d_xc(vf, v, ny, ixmin + 1, ixmax, iymin, iymax, threads);
}


void lf2d_xm(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - ny;
    const double *restrict v2 = v1 - ny;

    for (iy = 0; iy <= my; iy++){
        vf0[iy] = 0.25 * v0[iy] - 0.50 * v1[iy] + 0.25 * v2[iy];
    }
    lf2d_xc(vf, v, ny, ixmin, ixmax - 1, iymin, iymax, threads);
}


void lf2d_yp(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;
    const double *restrict v2 = v1 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        vf0[idx] = 0.25 * v0[idx] - 0.50 * v1[idx] + 0.25 * v2[idx];
    }
    lf2d_yc(vf, v, ny, ixmin, ixmax, iymin + 1, iymax, threads);
}


void lf2d_ym(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict v2 = v1 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        vf0[idx] = 0.25 * v0[idx] - 0.50 * v1[idx] + 0.25 * v2[idx];
    }
    lf2d_yc(vf, v, ny, ixmin, ixmax, iymin, iymax - 1, threads);
}


////////////////////////////////////////////////////////////////////////////////
// LF 3d
////////////////////////////////////////////////////////////////////////////////

void lf3d_xc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

    const double *restrict v1m = v - nynz;
    const double *restrict v1p = v + nynz;

    switch(threads){
        for (ix=0; ix <= mx; ix++){
            idx = ix * nynz;

            for (iy=0; iy <= my; iy++){
                idy = idx + iy * nz;

                for (iz=0; iz <= mz; iz++){
                    idz = idy + iz;
                    vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
        {
            #pragma omp for nowait
            for (ix=0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy=0; iy <= my; iy++){
                    idy = idx + iy * nz;

                    for (iz=0; iz <= mz; iz++){
                        idz = idy + iz;
                        vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                    }
                }
            }
        }
    }
}


void lf3d_yc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

    const double *restrict v1m = v - nz;
    const double *restrict v1p = v + nz;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                    }
                }
            }
        }
    }
}


void lf3d_zc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v1p = v + 1;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        vf[idz] = -0.25 * v1p[idz] + 0.5 * v[idz] - 0.25 * v1m[idz];
                    }
                }
            }
        }
    }
}


void lf3d_xP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, idn;
    const unsigned int nynz = ny * nz;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Px = P + 1;

    switch(threads){
        case 1:
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;
            v0 = v + *(Px + ix) * nynz;
            v1p = v + *(Px + ix + 1) * nynz;
            v1m = v + *(Px + ix - 1) * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idx + idy + iz;
                    idn = idy + iz;
                    vf[idz] = -0.25 * v1p[idn] + 0.5 * v0[idn] - 0.25 * v1m[idn];
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, idn, v0, v1p, v1m)
            {
            #pragma omp for nowait
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;
                v0 = v + *(Px + ix) * nynz;
                v1p = v + *(Px + ix + 1) * nynz;
                v1m = v + *(Px + ix - 1) * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idx + idy + iz;
                        idn = idy + iz;
                        vf[idz] = -0.25 * v1p[idn] + 0.5 * v0[idn] - 0.25 * v1m[idn];
                    }
                }
            }
        }
    }
}


void lf3d_yP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Py = P + 1;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    v0 = v + idx +  *(Py + iy) * nz;
                    v1p = v + idx + *(Py + iy + 1) * nz;
                    v1m = v + idx + *(Py + iy - 1) * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        vf[idz] = -0.25 * v1p[iz] + 0.5 * v0[iz] - 0.25 * v1m[iz];
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, v0, v1p, v1m)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        v0 = v + idx +  *(Py + iy) * nz;
                        v1p = v + idx + *(Py + iy + 1) * nz;
                        v1m = v + idx + *(Py + iy - 1) * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            vf[idz] = -0.25 * v1p[iz] + 0.5 *  v0[iz] - 0.25 * v1m[iz];
                    }
                }
            }
        }
    }
}


void lf3d_zP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 1;
    const double *restrict viy;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    viy = v + idy;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        vf[idz] = -0.25 * *(viy + *(Pz + iz + 1)) + 0.5 * *(viy + *(Pz + iz)) - 0.25 * *(viy + *(Pz + iz - 1));
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, viy)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        viy = v + idy;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            vf[idz] = -0.25 * *(viy + *(Pz + iz + 1)) + 0.5 * *(viy + *(Pz + iz)) - 0.25 * *(viy + *(Pz + iz - 1));
                    }
                }
            }
        }
    }
}


void lf3d_xp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nynz;
    const double *restrict v2 = v1 + nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            vf0[idz] = 0.25 * v0[idz] - 0.5 * v1[idz] + 0.25 * v2[idz];
        }
    }
    lf3d_xc(vf, v, ny, nz, ixmin + 1, ixmax, iymin, iymax, izmin, izmax, threads);
}


void lf3d_xm(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nynz;
    const double *restrict v2 = v1 - nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            vf0[idz] = 0.25 * v0[idz] - 0.5 * v1[idz] + 0.25 * v2[idz];
        }
    }
    lf3d_xc(vf, v, ny, nz, ixmin, ixmax - 1, iymin, iymax, izmin, izmax, threads);
}


void lf3d_yp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nz;
    const double *restrict v2 = v1 + nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            vf0[idz] = 0.25 * v0[idz] - 0.5 * v1[idz] + 0.25 * v2[idz];
        }
    }
    lf3d_yc(vf, v, ny, nz, ixmin, ixmax, iymin + 1, iymax, izmin, izmax, threads);
}


void lf3d_ym(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nz;
    const double *restrict v2 = v1 - nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            vf0[idz] = 0.25 * v0[idz] - 0.5 * v1[idz] + 0.25 * v2[idz];
        }
    }
    lf3d_yc(vf, v, ny, nz, ixmin, ixmax, iymin, iymax - 1, izmin, izmax, threads);
}


void lf3d_zp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;
    const double *restrict v2 = v1 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            vf0[idy] = 0.25 * v0[idy] - 0.5 * v1[idy] + 0.25 * v2[idy];
        }
    }
    lf3d_zc(vf, v, ny, nz, ixmin, ixmax, iymin, iymax, izmin + 1, izmax, threads);
}


void lf3d_zm(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;

    double *restrict vf0 = vf + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict v2 = v1 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            vf0[idy] = 0.25 * v0[idy] - 0.5 * v1[idy] + 0.25 * v2[idy];
        }
    }
    lf3d_zc(vf, v, ny, nz, ixmin, ixmax, iymin, iymax, izmin, izmax - 1, threads);
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// SG kernels
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// SG 2d
////////////////////////////////////////////////////////////////////////////////


unsigned int sg2d_xc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double dvp, dvm, dm, r;

    v += offset;
    p += offset;
    sg += offset;

    const double *restrict v1m = v - ny;
    const double *restrict v1p = v + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    dvp = v[idy] - v1p[idy];
                    dvm = v[idy] - v1m[idy];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                    r = rth / dm;
                    sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idy];
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, idx, idy, dvp, dvm, dm, r)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        dvp = v[idy] - v1p[idy];
                        dvm = v[idy] - v1m[idy];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                        r = rth / dm;
                        sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idy];
                }
            }
        }
        return flag;
    }
}


unsigned int sg2d_yc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double dvp, dvm, dm, r;

    v += offset;
    p += offset;
    sg += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v1p = v + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    dvp = v[idy] - v1p[idy];
                    dvm = v[idy] - v1m[idy];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                    r = rth / dm;
                    sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idy];
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, idx, idy, dvp, dvm, dm, r)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        dvp = v[idy] - v1p[idy];
                        dvm = v[idy] - v1m[idy];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                        r = rth / dm;
                        sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idy];
                }
            }
        }
        return flag;
    }
}


unsigned int sg2d_xP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Px = P + 1;
    double dvp, dvm, dm, r;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {

                idx = ix * ny;

                v0 = v + ix * ny;
                v1p = v + *(Px + ix + 1) * ny;
                v1m = v + *(Px + ix - 1) * ny;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    dvp = v0[iy] - v1p[iy];
                    dvm = v0[iy] - v1m[iy];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                    r = rth / dm;
                    sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idy];
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, idx, idy, v0, v1m, v1p, dvp, dvm, dm, r)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {

                    idx = ix * ny;

                    v0 = v + ix * ny;
                    v1p = v + *(Px + ix + 1) * ny;
                    v1m = v + *(Px + ix - 1) * ny;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        dvp = v0[iy] - v1p[iy];
                        dvm = v0[iy] - v1m[iy];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                        r = rth / dm;
                        sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idy];
                }
            }
        }
        return flag;
    }
}


unsigned int sg2d_yP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const double *restrict vix;
    const unsigned int *restrict Py = P + 1;
    double dvp, dvm, dm, r;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;
                vix = v + idx;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    dvp = *(vix + iy) - *(vix + *(Py + iy + 1));
                    dvm = *(vix + iy) - *(vix + *(Py + iy - 1));
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                    r = rth / dm;
                    sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idy];
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, idx, idy, vix, dvp, dvm, dm, r)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;
                    vix = v + idx;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        dvp = *(vix + iy) - *(vix + *(Py + iy + 1));
                        dvm = *(vix + iy) - *(vix + *(Py + iy - 1));
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idy] * p[idy]) + eps;
                        r = rth / dm;
                        sg[idy] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idy];
                }
            }
        }
        return flag;
    }
}


unsigned int sg2d_xp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int iy;
    unsigned int flag = 0;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + ny;
    const double *restrict p0 = p + offset;

    for (iy = 0; iy <= my; iy++){
        dv = v0[iy] - v1[iy];
        dm = dv * dv / (p0[iy] * p0[iy]) + eps;
        r = rth / dm;
        sg0[iy] = 0.5 * (1 - r + fabs(1 - r));
        flag |= !!sg0[iy];
    }
    flag |= sg2d_xc(sg, v, p, ny, ixmin + 1, ixmax, iymin, iymax, threads);
    return flag;
}


unsigned int sg2d_xm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int iy;
    unsigned int flag = 0;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - ny;
    const double *restrict p0 = p + offset;

    for (iy = 0; iy <= my; iy++){
        dv = v0[iy] - v1[iy];
        dm = dv * dv / (p0[iy] * p0[iy]) + eps;
        r = rth / dm;
        sg0[iy] = 0.5 * (1 - r + fabs(1 - r));
        flag |= !!sg0[iy];
    }
    flag |= sg2d_xc(sg, v, p, ny, ixmin, ixmax - 1, iymin, iymax, threads);
    return flag;
}


unsigned int sg2d_yp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, idx;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;
    const double *restrict p0 = p + offset;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        dv = v0[idx] - v1[idx];
        dm = dv * dv / (p0[idx] * p0[idx]) + eps;
        r = rth / dm;
        sg0[idx] = 0.5 * (1 - r + fabs(1 - r));
        flag |= !!sg0[idx];
    }
    flag |= sg2d_yc(sg, v, p, ny, ixmin, ixmax, iymin + 1, iymax, threads);
    return flag;
}


unsigned int sg2d_ym(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads) {

    unsigned int ix, idx;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict p0 = p + offset;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        dv = v0[idx] - v1[idx];
        dm = dv * dv / (p0[idx] * p0[idx]) + eps;
        r = rth / dm;
        sg0[idx] = 0.5 * (1 - r + fabs(1 - r));
        flag |= !!sg0[idx];
    }
    flag |= sg2d_yc(sg, v, p, ny, ixmin, ixmax, iymin, iymax - 1, threads);
    return flag;
}



////////////////////////////////////////////////////////////////////////////////
// SG 3d
////////////////////////////////////////////////////////////////////////////////

unsigned int sg3d_xc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dvm, dvp, dm, r;

    v += offset;
    p += offset;
    sg += offset;

    const double *restrict v1m = v - nynz;
    const double *restrict v1p = v + nynz;

    switch(threads){
        for (ix=0; ix <= mx; ix++){
            idx = ix * nynz;

            for (iy=0; iy <= my; iy++){
                idy = idx + iy * nz;

                for (iz=0; iz <= mz; iz++){
                    idz = idy + iz;
                    dvp = v[idz] - v1p[idz];
                    dvm = v[idz] - v1m[idz];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                    r = rth / dm;
                    sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idz];
                }
            }
        }
        return flag;
    default:
        #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, dvm, dvp, dm, r)
        {
            #pragma omp for nowait
            for (ix=0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy=0; iy <= my; iy++){
                    idy = idx + iy * nz;

                    for (iz=0; iz <= mz; iz++){
                        idz = idy + iz;
                        dvp = v[idz] - v1p[idz];
                        dvm = v[idz] - v1m[idz];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_yc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dvm, dvp, dm, r;

    v += offset;
    p += offset;
    sg += offset;

    const double *restrict v1m = v - nz;
    const double *restrict v1p = v + nz;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    dvp = v[idz] - v1p[idz];
                    dvm = v[idz] - v1m[idz];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                    r = rth / dm;
                    sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idz];
                }
            }
        }
        return flag;
    default:
        #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, dvm, dvp, dm, r)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        dvp = v[idz] - v1p[idz];
                        dvm = v[idz] - v1m[idz];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_zc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dvm, dvp, dm, r;

    v += offset;
    p += offset;
    sg += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v1p = v + 1;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    dvp = v[idz] - v1p[idz];
                    dvm = v[idz] - v1m[idz];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                    r = rth / dm;
                    sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idz];
                }
            }
        }
        return flag;
    default:
        #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, dvm, dvp, dm, r)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        dvp = v[idz] - v1p[idz];
                        dvm = v[idz] - v1m[idz];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_xP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, idn;
    unsigned int flag = 0;
    const unsigned int nynz = ny * nz;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Px = P + 1;
    double dvm, dvp, dm, r;

    switch(threads){
        case 1:
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;
            v0 = v + *(Px + ix) * nynz;
            v1p = v + *(Px + ix + 1) * nynz;
            v1m = v + *(Px + ix - 1) * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idx + idy + iz;
                    idn = idy + iz;
                    dvp = v0[idn] - v1p[idn];
                    dvm = v0[idn] - v1m[idn];
                    dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                    r = rth / dm;
                    sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                    flag |= !!sg[idz];
                }
            }
        }
        return flag;
    default:
        #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, idn, v0, v1p, v1m, dvm, dvp, dm, r)
            {
            #pragma omp for nowait
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;
                v0 = v + *(Px + ix) * nynz;
                v1p = v + *(Px + ix + 1) * nynz;
                v1m = v + *(Px + ix - 1) * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idx + idy + iz;
                        idn = idy + iz;
                        dvp = v0[idn] - v1p[idn];
                        dvm = v0[idn] - v1m[idn];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_yP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int flag = 0;
    const unsigned int nynz = ny * nz;
    const double *restrict v0, *restrict v1m, *restrict v1p;
    const unsigned int *restrict Py = P + 1;
    double dvm, dvp, dm, r;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    v0 = v + idx +  *(Py + iy) * nz;
                    v1p = v + idx + *(Py + iy + 1) * nz;
                    v1m = v + idx + *(Py + iy - 1) * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        dvp = v0[iz] - v1p[iz];
                        dvm = v0[iz] - v1m[iz];
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, v0, v1p, v1m, dvm, dvp, dm, r)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        v0 = v + idx +  *(Py + iy) * nz;
                        v1p = v + idx + *(Py + iy + 1) * nz;
                        v1m = v + idx + *(Py + iy - 1) * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            dvp = v0[iz] - v1p[iz];
                            dvm = v0[iz] - v1m[iz];
                            dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                            r = rth / dm;
                            sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                            flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_zP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int flag = 0;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 1;
    const double *restrict viy;
    double dvm, dvp, dm, r;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    viy = v + idy;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        dvp = *(viy + iz) - *(viy + *(Pz + iz + 1));
                        dvm = *(viy + iz) - *(viy + *(Pz + iz - 1));
                        dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                        r = rth / dm;
                        sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                        flag |= !!sg[idz];
                    }
                }
            }
            return flag;
        default:
            #pragma omp parallel num_threads(threads) reduction(|:flag) private(ix, iy, iz, idx, idy, idz, viy, dvm, dvp, dm, r)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        viy = v + idy;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            dvp = *(viy + iz) - *(viy + *(Pz + iz + 1));
                            dvm = *(viy + iz) - *(viy + *(Pz + iz - 1));
                            dm = 0.5 * (dvp * dvp + dvm * dvm) / (p[idz] * p[idz]) + eps;
                            r = rth / dm;
                            sg[idz] = 0.5 * (1 - r + fabs(1 - r));
                            flag |= !!sg[idz];
                    }
                }
            }
        }
        return flag;
    }
}


unsigned int sg3d_xp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    unsigned int flag = 0;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nynz;
    const double *restrict p0 = p + offset;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            dv = v0[idz] - v1[idz];
            dm = dv * dv / (p0[idz] * p0[idz]) + eps;
            r = rth / dm;
            sg0[idz] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idz];
        }
    }
    flag |= sg3d_xc(sg, v, p, ny, nz, ixmin + 1, ixmax, iymin, iymax, izmin, izmax, threads);
    return flag;
}


unsigned int sg3d_xm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    unsigned int flag = 0;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nynz;
    const double *restrict p0 = p + offset;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            dv = v0[idz] - v1[idz];
            dm = dv * dv / (p0[idz] * p0[idz]) + eps;
            r = rth / dm;
            sg0[idz] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idz];
        }
    }
    flag |= sg3d_xc(sg, v, p, ny, nz, ixmin, ixmax - 1, iymin, iymax, izmin, izmax, threads);
    return flag;
}


unsigned int sg3d_yp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nz;
    const double *restrict p0 = p + offset;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            dv = v0[idz] - v1[idz];
            dm = dv * dv / (p0[idz] * p0[idz]) + eps;
            r = rth / dm;
            sg0[idz] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idz];
        }
    }
    flag |= sg3d_yc(sg, v, p, ny, nz, ixmin, ixmax, iymin + 1, iymax, izmin, izmax, threads);
    return flag;
}


unsigned int sg3d_ym(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nz;
    const double *restrict p0 = p + offset;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            dv = v0[idz] - v1[idz];
            dm = dv * dv / (p0[idz] * p0[idz]) + eps;
            r = rth / dm;
            sg0[idz] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idz];
        }
    }
    flag |= sg3d_yc(sg, v, p, ny, nz, ixmin, ixmax, iymin, iymax - 1, izmin, izmax, threads);
    return flag;
}


unsigned int sg3d_zp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict p0 = p + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            dv = v0[idy] - v1[idy];
            dm = dv * dv / (p0[idy] * p0[idy]) + eps;
            r = rth / dm;
            sg0[idy] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idy];
        }
    }
    flag |= sg3d_zc(sg, v, p, ny, nz, ixmin, ixmax, iymin, iymax, izmin + 1, izmax, threads);
    return flag;
}


unsigned int sg3d_zm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    unsigned int flag = 0;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;
    double dv, dm, r;

    double *restrict sg0 = sg + offset;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict p0 = p + offset;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            dv = v0[idy] - v1[idy];
            dm = dv * dv / (p0[idy] * p0[idy]) + eps;
            r = rth / dm;
            sg0[idy] = 0.5 * (1 - r + fabs(1 - r));
            flag |= !!sg0[idy];
        }
    }
    flag |= sg3d_zc(sg, v, p, ny, nz, ixmin, ixmax, iymin, iymax, izmin, izmax - 1, threads);
    return flag;
}


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// SC kernels
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// SC 2d [checked and faster]
////////////////////////////////////////////////////////////////////////////////


void sc2d_xc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double dpu, dmu;

    vf += offset;
    v += offset;
    sg += offset;

    const double *restrict v1m = v - ny;
    const double *restrict v2m = v1m - ny;
    const double *restrict v1p = v + ny;
    const double *restrict v2p = v1p + ny;

    const double *restrict sg1m = sg - ny;
    const double *restrict sg1p = sg + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    dpu = (c_sc[3] * v1m[idy] + c_sc[0] * v[idy] +
                           c_sc[1] * v1p[idy] + c_sc[2] * v2p[idy]);
                    dmu = (c_sc[3] * v2m[idy] + c_sc[0] * v1m[idy] +
                           c_sc[1] * v[idy]   + c_sc[2] * v1p[idy]);
                    vf[idy] = (0.5 * (sg1p[idy] + sg[idy]) * dpu -
                               0.5 * (sg[idy]   + sg1m[idy]) * dmu);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        dpu = (c_sc[3] * v1m[idy] + c_sc[0] * v[idy] +
                               c_sc[1] * v1p[idy] + c_sc[2] * v2p[idy]);
                        dmu = (c_sc[3] * v2m[idy] + c_sc[0] * v1m[idy] +
                               c_sc[1] * v[idy]   + c_sc[2] * v1p[idy]);
                        vf[idy] = (0.5 * (sg1p[idy] + sg[idy]) * dpu -
                                   0.5 * (sg[idy]   + sg1m[idy]) * dmu);
                }
            }
        }
    }
}


void sc2d_yc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double dpu, dmu;

    vf += offset;
    v += offset;
    sg += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v2m = v1m - 1;
    const double *restrict v1p = v + 1;
    const double *restrict v2p = v1p + 1;

    const double *restrict sg1m = sg - 1;
    const double *restrict sg1p = sg + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    dpu = (c_sc[3] * v1m[idy] + c_sc[0] * v[idy] +
                           c_sc[1] * v1p[idy] + c_sc[2] * v2p[idy]);
                    dmu = (c_sc[3] * v2m[idy] + c_sc[0] * v1m[idy] +
                           c_sc[1] * v[idy]   + c_sc[2] * v1p[idy]);
                    vf[idy] = (0.5 * (sg1p[idy] + sg[idy]) * dpu -
                               0.5 * (sg[idy]   + sg1m[idy]) * dmu);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy;
                        dpu = (c_sc[3] * v1m[idy] + c_sc[0] * v[idy] +
                               c_sc[1] * v1p[idy] + c_sc[2] * v2p[idy]);
                        dmu = (c_sc[3] * v2m[idy] + c_sc[0] * v1m[idy] +
                               c_sc[1] * v[idy]   + c_sc[2] * v1p[idy]);
                        vf[idy] = (0.5 * (sg1p[idy] + sg[idy]) * dpu -
                                   0.5 * (sg[idy]   + sg1m[idy]) * dmu);
                }
            }
        }
    }
}


void sc2d_xP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int *restrict Px = P + 2;
    double dpu, dmu;

    const double *restrict v1m, *restrict v2m;
    const double *restrict v1p,  *restrict v2p;
    const double *restrict sg1p,  *restrict sg1m;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;

                v1p = v + *(Px + ix + 1) * ny;
                v2p = v + *(Px + ix + 2) * ny;
                v1m = v + *(Px + ix - 1) * ny;
                v2m = v + *(Px + ix - 2) * ny;

                sg1p = sg + *(Px + ix + 1) * ny;
                sg1m = sg + *(Px + ix - 1) * ny;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    dpu = (c_sc[3] * v1m[iy] + c_sc[0] * v[idy] +
                           c_sc[1] * v1p[iy] + c_sc[2] * v2p[iy]);
                    dmu = (c_sc[3] * v2m[iy] + c_sc[0] * v1m[iy] +
                           c_sc[1] * v[idy]   + c_sc[2] * v1p[iy]);
                    vf[idy] = (0.5 * (sg1p[iy] + sg[idy]) * dpu -
                               0.5 * (sg[idy]  + sg1m[iy]) * dmu);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, v1m, v2m, v1p, v2p, sg1m, sg1p, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;

                    v1p = v + *(Px + ix + 1) * ny;
                    v2p = v + *(Px + ix + 2) * ny;
                    v1m = v + *(Px + ix - 1) * ny;
                    v2m = v + *(Px + ix - 2) * ny;

                    sg1p = sg + *(Px + ix + 1) * ny;
                    sg1m = sg + *(Px + ix - 1) * ny;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        dpu = (c_sc[3] * v1m[iy] + c_sc[0] * v[idy] +
                               c_sc[1] * v1p[iy] + c_sc[2] * v2p[iy]);
                        dmu = (c_sc[3] * v2m[iy] + c_sc[0] * v1m[iy] +
                               c_sc[1] * v[idy]   + c_sc[2] * v1p[iy]);
                        vf[idy] = (0.5 * (sg1p[iy] + sg[idy]) * dpu -
                                   0.5 * (sg[idy]  + sg1m[iy]) * dmu);
                }
            }
        }
    }
}


void sc2d_yP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy, id1p, id2p, id1m, id2m;
    const unsigned int *restrict Py = P + 2;
    double dpu, dmu;

    const double *restrict vix;
    const double *restrict sgix;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;
                vix = v + idx;
                sgix = sg + idx;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    id1p = *(Py + iy + 1);
                    id2p = *(Py + iy + 2);
                    id1m = *(Py + iy - 1);
                    id2m = *(Py + iy - 2);

                    dpu = (c_sc[3] * vix[id1m] + c_sc[0] * vix[iy] +
                           c_sc[1] * vix[id1p] + c_sc[2] * vix[id2p]);
                    dmu = (c_sc[3] * vix[id2m] + c_sc[0] * vix[id1m] +
                           c_sc[1] * vix[iy]   + c_sc[2] * vix[id1p]);
                    vf[idy] = (0.5 * (sgix[id1p] + sgix[iy]) * dpu -
                               0.5 * (sgix[iy]    + sgix[id1m]) * dmu);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, vix, sgix, id1p, id2p, id1m, id2m, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;
                    vix = v + idx;
                    sgix = sg + idx;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        id1p = *(Py + iy + 1);
                        id2p = *(Py + iy + 2);
                        id1m = *(Py + iy - 1);
                        id2m = *(Py + iy - 2);

                        dpu = (c_sc[3] * vix[id1m] + c_sc[0] * vix[iy] +
                               c_sc[1] * vix[id1p] + c_sc[2] * vix[id2p]);
                        dmu = (c_sc[3] * vix[id2m] + c_sc[0] * vix[id1m] +
                               c_sc[1] * vix[iy]   + c_sc[2] * vix[id1p]);
                        vf[idy] = (0.5 * (sgix[id1p] + sgix[iy]) * dpu -
                                   0.5 * (sgix[iy]    + sgix[id1m]) * dmu);
                }
            }
        }
    }
}


void sc2d_xp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 + ny;

    const double *restrict sg1 = sg + offset + ny;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + ny;
    const double *restrict v2 = v1 + ny;

    for (iy = 0; iy <= my; iy++){
        vf0[iy] = 0;
        vf1[iy] = sg1[iy] * (-0.25 * v0[iy]
                             +0.50 * v1[iy]
                             -0.25 * v2[iy]);
    }
    sc2d_xc(vf, v, sg, ny, ixmin + 2, ixmax, iymin, iymax, threads);
}


void sc2d_xm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 - ny;

    const double *restrict sg1 = sg + offset - ny;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - ny;
    const double *restrict v2 = v1 - ny;

    for (iy = 0; iy <= my; iy++){
        vf0[iy] = 0;
        vf1[iy] = sg1[iy] * (-0.25 * v2[iy]
                             +0.50 * v1[iy]
                             -0.25 * v0[iy]);
    }
    sc2d_xc(vf, v, sg, ny, ixmin, ixmax - 2, iymin, iymax, threads);
}


void sc2d_yp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf + offset + 1;

    const double *restrict sg1 = sg + offset + 1;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;
    const double *restrict v2 = v1 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        vf0[idx] = 0;
        vf1[idx] = sg1[idx] * (-0.25 * v0[idx]
                               +0.50 * v1[idx]
                               -0.25 * v2[idx]);
    }
    sc2d_yc(vf, v, sg, ny, ixmin, ixmax, iymin + 2, iymax, threads);
}


void sc2d_ym(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf + offset - 1;

    const double *restrict sg1 = sg + offset - 1;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict v2 = v1 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        vf0[idx] = 0;
        vf1[idx] = sg1[idx] * (-0.25 * v2[idx]
                               +0.50 * v1[idx]
                               -0.25 * v0[idx]);
    }
    sc2d_yc(vf, v, sg, ny, ixmin, ixmax, iymin, iymax - 2, threads);
}


////////////////////////////////////////////////////////////////////////////////
// SC 3d [checked and faster]
////////////////////////////////////////////////////////////////////////////////

void sc3d_xc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dmu, dpu;

    vf += offset;
    v += offset;
    sg += offset;

    const double *restrict v1m = v - nynz;
    const double *restrict v2m = v1m - nynz;
    const double *restrict v1p = v + nynz;
    const double *restrict v2p = v1p + nynz;

    const double *restrict sg1m = sg - nynz;
    const double *restrict sg1p = sg + nynz;

    switch(threads){
        for (ix=0; ix <= mx; ix++){
            idx = ix * nynz;

            for (iy=0; iy <= my; iy++){
                idy = idx + iy * nz;

                for (iz=0; iz <= mz; iz++){
                    idz = idy + iz;
                    dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                           c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                    dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                           c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                    vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                               0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dpu, dmu)
        {
            #pragma omp for nowait
            for (ix=0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy=0; iy <= my; iy++){
                    idy = idx + iy * nz;

                    for (iz=0; iz <= mz; iz++){
                        idz = idy + iz;
                        dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                               c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                        dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                               c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                        vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_yc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dmu, dpu;

    vf += offset;
    v += offset;
    sg += offset;

    const double *restrict v1m = v - nz;
    const double *restrict v2m = v1m - nz;
    const double *restrict v1p = v + nz;
    const double *restrict v2p = v1p + nz;

    const double *restrict sg1m = sg - nz;
    const double *restrict sg1p = sg + nz;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                           c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                    dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                           c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                    vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                               0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dpu, dmu)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                               c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                        dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                               c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                        vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_zc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double dmu, dpu;

    vf += offset;
    v += offset;
    sg += offset;

    const double *restrict v1m = v - 1;
    const double *restrict v2m = v1m - 1;
    const double *restrict v1p = v + 1;
    const double *restrict v2p = v1p + 1;

    const double *restrict sg1m = sg - 1;
    const double *restrict sg1p = sg + 1;

    switch(threads){
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                           c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                    dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                           c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                    vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                               0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dpu, dmu)
        {
            #pragma omp for nowait
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        dpu = (c_sc[3] * v1m[idz] + c_sc[0] * v[idz] +
                               c_sc[1] * v1p[idz] + c_sc[2] * v2p[idz]);
                        dmu = (c_sc[3] * v2m[idz] + c_sc[0] * v1m[idz] +
                               c_sc[1] * v[idz]   + c_sc[2] * v1p[idz]);
                        vf[idz] = (0.5 * (sg1p[idz] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]   + sg1m[idz]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_xP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, idn;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Px = P + 2;
    double dmu, dpu;

    const double *restrict v1m, *restrict v2m;
    const double *restrict v1p, *restrict v2p;
    const double *restrict sg1p, *restrict sg1m;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                v1p = v + *(Px + ix + 1) * nynz;
                v2p = v + *(Px + ix + 2) * nynz;
                v1m = v + *(Px + ix - 1) * nynz;
                v2m = v + *(Px + ix - 2) * nynz;

                sg1p = sg + *(Px + ix + 1) * nynz;
                sg1m = sg + *(Px + ix - 1) * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idx + idy + iz;
                        idn = idy + iz;
                        dpu = (c_sc[3] * v1m[idn] + c_sc[0] * v[idz] +
                               c_sc[1] * v1p[idn] + c_sc[2] * v2p[idn]);
                        dmu = (c_sc[3] * v2m[idn] + c_sc[0] * v1m[idn] +
                               c_sc[1] * v[idz]   + c_sc[2] * v1p[idn]);
                        vf[idz] = (0.5 * (sg1p[idn] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]  + sg1m[idn]) * dmu);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
                   idx, idy, idz, idn, v1m, v2m, v1p, v2p, sg1m, sg1p, dpu, dmu)
                {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    v1p = v + *(Px + ix + 1) * nynz;
                    v2p = v + *(Px + ix + 2) * nynz;
                    v1m = v + *(Px + ix - 1) * nynz;
                    v2m = v + *(Px + ix - 2) * nynz;
                    sg1p = sg + *(Px + ix + 1) * nynz;
                    sg1m = sg + *(Px + ix - 1) * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = iy * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idx + idy + iz;
                            idn = idy + iz;
                            dpu = (c_sc[3] * v1m[idn] + c_sc[0] * v[idz] +
                                   c_sc[1] * v1p[idn] + c_sc[2] * v2p[idn]);
                            dmu = (c_sc[3] * v2m[idn] + c_sc[0] * v1m[idn] +
                                   c_sc[1] * v[idz]   + c_sc[2] * v1p[idn]);
                            vf[idz] = (0.5 * (sg1p[idn] + sg[idz]) * dpu -
                                       0.5 * (sg[idz]  + sg1m[idn]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_yP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Py = P + 2;
    double dpu, dmu;

    const double *restrict v1m, *restrict v2m;
    const double *restrict v1p, *restrict v2p;
    const double *restrict sg1p, *restrict sg1m;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    v1p = v + idx + *(Py + iy + 1) * nz;
                    v2p = v + idx + *(Py + iy + 2) * nz;
                    v1m = v + idx + *(Py + iy - 1) * nz;
                    v2m = v + idx + *(Py + iy - 2) * nz;
                    sg1p = sg + idx + *(Py + iy + 1) * nz;
                    sg1m = sg + idx + *(Py + iy - 1) * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        dpu = (c_sc[3] * v1m[iz] + c_sc[0] * v[idz] +
                               c_sc[1] * v1p[iz] + c_sc[2] * v2p[iz]);
                        dmu = (c_sc[3] * v2m[iz] + c_sc[0] * v1m[iz] +
                               c_sc[1] * v[idz]  + c_sc[2] * v1p[iz]);
                        vf[idz] = (0.5 * (sg1p[iz] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]  + sg1m[iz]) * dmu);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
                        idx, idy, idz, v1m, v2m, v1p, v2p, sg1m, sg1p, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;

                        v1p = v + idx + *(Py + iy + 1) * nz;
                        v2p = v + idx + *(Py + iy + 2) * nz;
                        v1m = v + idx + *(Py + iy - 1) * nz;
                        v2m = v + idx + *(Py + iy - 2) * nz;
                        sg1p = sg + idx + *(Py + iy + 1) * nz;
                        sg1m = sg + idx + *(Py + iy - 1) * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            dpu = (c_sc[3] * v1m[iz] + c_sc[0] * v[idz] +
                                   c_sc[1] * v1p[iz] + c_sc[2] * v2p[iz]);
                            dmu = (c_sc[3] * v2m[iz] + c_sc[0] * v1m[iz] +
                                   c_sc[1] * v[idz]  + c_sc[2] * v1p[iz]);
                            vf[idz] = (0.5 * (sg1p[iz] + sg[idz]) * dpu -
                                       0.5 * (sg[idz]  + sg1m[iz]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_zP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, id1p, id2p, id1m, id2m;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 2;
    double dpu, dmu;

    const double *restrict viy;
    const double *restrict sgiy;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    viy = v + idy;
                    sgiy = sg + idy;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        id1p = *(Pz + iz + 1);
                        id2p = *(Pz + iz + 2);
                        id1m = *(Pz + iz - 1);
                        id2m = *(Pz + iz - 2);

                        dpu = (c_sc[3] * viy[id1m] + c_sc[0] * v[idz] +
                               c_sc[1] * viy[id1p] + c_sc[2] * viy[id2p]);
                        dmu = (c_sc[3] * viy[id2m] + c_sc[0] * viy[id1m] +
                               c_sc[1] * v[idz]    + c_sc[2] * viy[id1p]);
                        vf[idz] = (0.5 * (sgiy[id1p] + sg[idz]) * dpu -
                                   0.5 * (sg[idz]  + sgiy[id1m]) * dmu);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
                    idx, idy, idz, id1p, id2p, id1m, id2m, viy, sgiy, dpu, dmu)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        viy = v + idy;
                        sgiy = sg + idy;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            id1p = *(Pz + iz + 1);
                            id2p = *(Pz + iz + 2);
                            id1m = *(Pz + iz - 1);
                            id2m = *(Pz + iz - 2);

                            dpu = (c_sc[3] * viy[id1m] + c_sc[0] * v[idz] +
                                   c_sc[1] * viy[id1p] + c_sc[2] * viy[id2p]);
                            dmu = (c_sc[3] * viy[id2m] + c_sc[0] * viy[id1m] +
                                   c_sc[1] * v[idz]    + c_sc[2] * viy[id1p]);
                            vf[idz] = (0.5 * (sgiy[id1p] + sg[idz]) * dpu -
                                       0.5 * (sg[idz]  + sgiy[id1m]) * dmu);
                    }
                }
            }
        }
    }
}


void sc3d_xp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 + nynz;

    const double *restrict sg1 = sg + offset + nynz;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nynz;
    const double *restrict v2 = v1 + nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            vf0[idz] = 0;
            vf1[idz] = sg1[idz] * (-0.25 * v0[idz]
                                   +0.50 * v1[idz]
                                   -0.25 * v2[idz]);
        }
    }
    sc3d_xc(vf, v, sg, ny, nz, ixmin + 2, ixmax, iymin, iymax, izmin, izmax, threads);
}


void sc3d_xm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 - nynz;

    const double *restrict sg1 = sg + offset - nynz;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nynz;
    const double *restrict v2 = v1 - nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            vf0[idz] = 0.;
            vf1[idz] = sg1[idz] * (-0.25 * v2[idz]
                                   +0.50 * v1[idz]
                                   -0.25 * v0[idz]);
        }
    }
    sc3d_xc(vf, v, sg, ny, nz, ixmin, ixmax - 2, iymin, iymax, izmin, izmax, threads);
}


void sc3d_yp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 + nz;

    const double *restrict sg1 = sg + offset + nz;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + nz;
    const double *restrict v2 = v1 + nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            vf0[idz] = 0;
            vf1[idz] = sg1[idz] * (-0.25 * v0[idz]
                                   +0.50 * v1[idz]
                                   -0.25 * v2[idz]);
        }
    }
    sc3d_yc(vf, v, sg, ny, nz, ixmin, ixmax, iymin + 2, iymax, izmin, izmax, threads);
}


void sc3d_ym(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 - nz;

    const double *restrict sg1 = sg + offset - nz;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - nz;
    const double *restrict v2 = v1 - nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            vf0[idz] = 0;
            vf1[idz] = sg1[idz] * (-0.25 * v2[idz]
                                   +0.50 * v1[idz]
                                   -0.25 * v0[idz]);
        }
    }
    sc3d_yc(vf, v, sg, ny, nz, ixmin, ixmax, iymin, iymax - 2, izmin, izmax, threads);
}


void sc3d_zp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 + 1;

    const double *restrict sg1 = sg + offset + 1;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 + 1;
    const double *restrict v2 = v1 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            vf0[idy] = 0.;
            vf1[idy] = sg1[idy] * (-0.25 * v0[idy]
                                   +0.50 * v1[idy]
                                   -0.25 * v2[idy]);
        }
    }
    sc3d_zc(vf, v, sg, ny, nz, ixmin, ixmax, iymin, iymax, izmin + 2, izmax, threads);
}


void sc3d_zm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;

    double *restrict vf0 = vf + offset;
    double *restrict vf1 = vf0 - 1;

    const double *restrict sg1 = sg + offset - 1;
    const double *restrict v0 = v + offset;
    const double *restrict v1 = v0 - 1;
    const double *restrict v2 = v1 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            vf0[idy] = 0.;
            vf1[idy] = sg1[idy] * (-0.25 * v2[idy]
                                   +0.50 * v1[idy]
                                   -0.25 * v0[idy]);
        }
    }
    sc3d_zc(vf, v, sg, ny, nz, ixmin, ixmax, iymin, iymax, izmin, izmax - 2, threads);
}

