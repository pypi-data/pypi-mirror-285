#include <stdio.h>
#include <omp.h>
#include <time.h>
#include "kernels_diffraw.h"
#include "coefficients.h"


/*----------------------------*/
/* Global 1d differentiation */
/*--------------------------*/


void d1_s(double *restrict dvdx, const double *restrict v, const double odx, const unsigned int n) {

    unsigned int idx;
    const double *restrict v0;
    const double *restrict v1, *restrict v2, *restrict v3, *restrict v4, *restrict v5;
    const double *restrict v6, *restrict v7, *restrict v8, *restrict v9, *restrict v10;

    for (unsigned int ix=5; ix < n - 5; ix++){

        v0 = v + ix;

        *(dvdx + ix) = (a11c[1] * (*(v0 + 1) - *(v0 - 1)) +
                        a11c[2] * (*(v0 + 2) - *(v0 - 2)) +
                        a11c[3] * (*(v0 + 3) - *(v0 - 3)) +
                        a11c[4] * (*(v0 + 4) - *(v0 - 4)) +
                        a11c[5] * (*(v0 + 5) - *(v0 - 5))) * odx;
    }

    v1 = v + 1;
    v2 = v1 + 1;
    v3 = v2 + 1;
    v4 = v3 + 1;
    v5 = v4 + 1;
    v6 = v5 + 1;
    v7 = v6 + 1;
    v8 = v7 + 1;
    v9 = v8 + 1;
    v10 = v9 + 1;

    for (unsigned int ix=0; ix < 5; ix++){
        *(dvdx + ix) = (a11d[ix][0] * *v +
                        a11d[ix][1] * *v1 +
                        a11d[ix][2] * *v2 +
                        a11d[ix][3] * *v3 +
                        a11d[ix][4] * *v4 +
                        a11d[ix][5] * *v5 +
                        a11d[ix][6] * *v6 +
                        a11d[ix][7] * *v7 +
                        a11d[ix][8] * *v8 +
                        a11d[ix][9] * *v9 +
                        a11d[ix][10] * *v10) * odx;
    }

    v0 = v + n - 1;
    v1 = v0 - 1;
    v2 = v1 - 1;
    v3 = v2 - 1;
    v4 = v3 - 1;
    v5 = v4 - 1;
    v6 = v5 - 1;
    v7 = v6 - 1;
    v8 = v7 - 1;
    v9 = v8 - 1;
    v10 = v9 - 1;

    for (unsigned int ix=n - 5; ix < n; ix++){

        idx = n - ix - 1;

        *(dvdx + ix) = - (a11d[idx][0] * *v0 +
                          a11d[idx][1] * *v1 +
                          a11d[idx][2] * *v2 +
                          a11d[idx][3] * *v3 +
                          a11d[idx][4] * *v4 +
                          a11d[idx][5] * *v5 +
                          a11d[idx][6] * *v6 +
                          a11d[idx][7] * *v7 +
                          a11d[idx][8] * *v8 +
                          a11d[idx][9] * *v9 +
                          a11d[idx][10] * *v10) * odx;
    }
}


/*-------*/
/* Test */
/*-----*/


void d2xc_s_naive(double *restrict dvdx, const double *restrict v, const double odx,
                  const unsigned int ny,
                  const unsigned int ixmin, const unsigned int ixmax,
                  const unsigned int iymin, const unsigned int iymax,
                  const unsigned int threads) {

    (void)(threads);
    unsigned int ix, iy;

    for (ix=ixmin; ix < ixmax + 1; ix++){
        for (iy=iymin; iy < iymax + 1; iy++){
            dvdx[ix * ny + iy] = (a11c[1] * (v[(ix+1) * ny + iy] - v[(ix-1) * ny + iy]) +
                                  a11c[2] * (v[(ix+2) * ny + iy] - v[(ix-2) * ny + iy]) +
                                  a11c[3] * (v[(ix+3) * ny + iy] - v[(ix-3) * ny + iy]) +
                                  a11c[4] * (v[(ix+4) * ny + iy] - v[(ix-4) * ny + iy]) +
                                  a11c[5] * (v[(ix+5) * ny + iy] - v[(ix-5) * ny + iy])) * odx;
        }
    }
}


void d2yc_s_naive(double *restrict dvdx, const double *restrict v, const double odx,
                  const unsigned int ny,
                  const unsigned int ixmin, const unsigned int ixmax,
                  const unsigned int iymin, const unsigned int iymax,
                  const unsigned int threads) {

    (void)(threads);
    unsigned int ix, iy;

    for (ix=ixmin; ix < ixmax + 1; ix++){
        for (iy=iymin; iy < iymax + 1; iy++){
            dvdx[ix * ny + iy] = (a11c[1] * (v[ix * ny + iy + 1] - v[ix * ny + iy - 1]) +
                                  a11c[2] * (v[ix * ny + iy + 2] - v[ix * ny + iy - 2]) +
                                  a11c[3] * (v[ix * ny + iy + 3] - v[ix * ny + iy - 3]) +
                                  a11c[4] * (v[ix * ny + iy + 4] - v[ix * ny + iy - 4]) +
                                  a11c[5] * (v[ix * ny + iy + 5] - v[ix * ny + iy - 5])) * odx;
        }
    }
}


/*-------------------------------*/
/* Performance tests */
/*-----------------------------*/


void d2xc_tiled(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, row_start, row_end;

    const double *restrict v_1m = v - ny;
    const double *restrict v_2m = v_1m - ny;
    const double *restrict v_3m = v_2m - ny;
    const double *restrict v_4m = v_3m - ny;
    const double *restrict v_5m = v_4m - ny;

    const double *restrict v_1p = v + ny;
    const double *restrict v_2p = v_1p + ny;
    const double *restrict v_3p = v_2p + ny;
    const double *restrict v_4p = v_3p + ny;
    const double *restrict v_5p = v_4p + ny;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                row_start = ix * ny + iymin;
                row_end = ix * ny + iymax;
                for (iy = row_start; iy <= row_end; iy++) {
                    *(dvdx + iy) = (a11c[1] * (*(v_1p + iy) - *(v_1m + iy)) +
                                    a11c[2] * (*(v_2p + iy) - *(v_2m + iy)) +
                                    a11c[3] * (*(v_3p + iy) - *(v_3m + iy)) +
                                    a11c[4] * (*(v_4p + iy) - *(v_4m + iy)) +
                                    a11c[5] * (*(v_5p + iy) - *(v_5m + iy))) * odx;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, row_start, row_end)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    row_start = ix * ny + iymin;
                    row_end = ix * ny + iymax;
                    for (iy = row_start; iy <= row_end; iy++) {
                        *(dvdx + iy) = (a11c[1] * (*(v_1p + iy) - *(v_1m + iy)) +
                                        a11c[2] * (*(v_2p + iy) - *(v_2m + iy)) +
                                        a11c[3] * (*(v_3p + iy) - *(v_3m + iy)) +
                                        a11c[4] * (*(v_4p + iy) - *(v_4m + iy)) +
                                        a11c[5] * (*(v_5p + iy) - *(v_5m + iy))) * odx;
                }
            }
        }
    }
}



void d2yc_tiled(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dvdy += offset;

    const double *restrict v_1m = v - 1;
    const double *restrict v_2m = v_1m - 1;
    const double *restrict v_3m = v_2m - 1;
    const double *restrict v_4m = v_3m - 1;
    const double *restrict v_5m = v_4m - 1;

    const double *restrict v_1p = v + 1;
    const double *restrict v_2p = v_1p + 1;
    const double *restrict v_3p = v_2p + 1;
    const double *restrict v_4p = v_3p + 1;
    const double *restrict v_5p = v_4p + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {

                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {

                    idy = idx + iy;
                    *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                     a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                     a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                     a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                     a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * ody;
                }
            }
            break;

        default:

            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy)
                {
                #pragma omp for collapse(2) nowait
                for (ix = 0; ix <= mx; ix++) {

                    idx = ix * ny;

                    for (iy = 0; iy <= my; iy++) {

                        idy = idx + iy;
                        *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                         a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                         a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                         a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                         a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * ody;
                }
            }
        }
    }
}




/*-------------------------------*/
/* Subdomain 2d differentiation */
/*-----------------------------*/


void d2xc_s(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dvdx += offset;

    const double *restrict v_1m = v - ny;
    const double *restrict v_2m = v_1m - ny;
    const double *restrict v_3m = v_2m - ny;
    const double *restrict v_4m = v_3m - ny;
    const double *restrict v_5m = v_4m - ny;

    const double *restrict v_1p = v + ny;
    const double *restrict v_2p = v_1p + ny;
    const double *restrict v_3p = v_2p + ny;
    const double *restrict v_4p = v_3p + ny;
    const double *restrict v_5p = v_4p + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    *(dvdx + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                     a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                     a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                     a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                     a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odx;
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
                        *(dvdx + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                         a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                         a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                         a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                         a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odx;
                }
            }
        }
    }
}


void d2xc_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dvdx += offset;
    odx += ixmin;

    const double *restrict v_1m = v - ny;
    const double *restrict v_2m = v_1m - ny;
    const double *restrict v_3m = v_2m - ny;
    const double *restrict v_4m = v_3m - ny;
    const double *restrict v_5m = v_4m - ny;

    const double *restrict v_1p = v + ny;
    const double *restrict v_2p = v_1p + ny;
    const double *restrict v_3p = v_2p + ny;
    const double *restrict v_4p = v_3p + ny;
    const double *restrict v_5p = v_4p + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    *(dvdx + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                     a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                     a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                     a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                     a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odx + ix);
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
                        *(dvdx + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                         a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                         a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                         a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                         a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odx + ix);
                }
            }
        }
    }
}


void d2yc_s(double *restrict dvdy, const double *restrict v, const double ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dvdy += offset;

    const double *restrict v_1m = v - 1;
    const double *restrict v_2m = v_1m - 1;
    const double *restrict v_3m = v_2m - 1;
    const double *restrict v_4m = v_3m - 1;
    const double *restrict v_5m = v_4m - 1;

    const double *restrict v_1p = v + 1;
    const double *restrict v_2p = v_1p + 1;
    const double *restrict v_3p = v_2p + 1;
    const double *restrict v_4p = v_3p + 1;
    const double *restrict v_5p = v_4p + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {

                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {

                    idy = idx + iy;
                    *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                     a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                     a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                     a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                     a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * ody;
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
                        *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                         a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                         a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                         a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                         a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * ody;
                }
            }
        }
    }
}


void d2yc_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dvdy += offset;
    ody += iymin;

    const double *restrict v_1m = v - 1;
    const double *restrict v_2m = v_1m - 1;
    const double *restrict v_3m = v_2m - 1;
    const double *restrict v_4m = v_3m - 1;
    const double *restrict v_5m = v_4m - 1;

    const double *restrict v_1p = v + 1;
    const double *restrict v_2p = v_1p + 1;
    const double *restrict v_3p = v_2p + 1;
    const double *restrict v_4p = v_3p + 1;
    const double *restrict v_5p = v_4p + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy;
                    *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                     a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                     a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                     a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                     a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(ody + iy);
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
                        *(dvdy + idy) = (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                         a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                         a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                         a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                         a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(ody + iy);
                }
            }
        }
    }
}


void d2xP_s(double *restrict dv, const double *restrict v,
            const double odn, const unsigned int *restrict P,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;

                v1p = v + *(Px + ix + 1) * ny;
                v2p = v + *(Px + ix + 2) * ny;
                v3p = v + *(Px + ix + 3) * ny;
                v4p = v + *(Px + ix + 4) * ny;
                v5p = v + *(Px + ix + 5) * ny;

                v1m = v + *(Px + ix - 1) * ny;
                v2m = v + *(Px + ix - 2) * ny;
                v3m = v + *(Px + ix - 3) * ny;
                v4m = v + *(Px + ix - 4) * ny;
                v5m = v + *(Px + ix - 5) * ny;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    *(dv + idy) = (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                    a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                    a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                    a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                    a11c[5] * (*(v5p + iy) - *(v5m + iy))) * odn;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;

                    v1p = v + *(Px + ix + 1) * ny;
                    v2p = v + *(Px + ix + 2) * ny;
                    v3p = v + *(Px + ix + 3) * ny;
                    v4p = v + *(Px + ix + 4) * ny;
                    v5p = v + *(Px + ix + 5) * ny;

                    v1m = v + *(Px + ix - 1) * ny;
                    v2m = v + *(Px + ix - 2) * ny;
                    v3m = v + *(Px + ix - 3) * ny;
                    v4m = v + *(Px + ix - 4) * ny;
                    v5m = v + *(Px + ix - 5) * ny;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        *(dv + idy) = (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                        a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                        a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                        a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                        a11c[5] * (*(v5p + iy) - *(v5m + iy))) * odn;
                }
            }
        }
    }
}


void d2xP_v(double *restrict dv, const double *restrict v,
            const double *restrict odn, const unsigned int *restrict P,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;

                v1p = v + *(Px + ix + 1) * ny;
                v2p = v + *(Px + ix + 2) * ny;
                v3p = v + *(Px + ix + 3) * ny;
                v4p = v + *(Px + ix + 4) * ny;
                v5p = v + *(Px + ix + 5) * ny;

                v1m = v + *(Px + ix - 1) * ny;
                v2m = v + *(Px + ix - 2) * ny;
                v3m = v + *(Px + ix - 3) * ny;
                v4m = v + *(Px + ix - 4) * ny;
                v5m = v + *(Px + ix - 5) * ny;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    *(dv + idy) = (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                    a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                    a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                    a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                    a11c[5] * (*(v5p + iy) - *(v5m + iy))) * *(odn + ix);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;

                    v1p = v + *(Px + ix + 1) * ny;
                    v2p = v + *(Px + ix + 2) * ny;
                    v3p = v + *(Px + ix + 3) * ny;
                    v4p = v + *(Px + ix + 4) * ny;
                    v5p = v + *(Px + ix + 5) * ny;

                    v1m = v + *(Px + ix - 1) * ny;
                    v2m = v + *(Px + ix - 2) * ny;
                    v3m = v + *(Px + ix - 3) * ny;
                    v4m = v + *(Px + ix - 4) * ny;
                    v5m = v + *(Px + ix - 5) * ny;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy;
                        *(dv + idy) = (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                        a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                        a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                        a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                        a11c[5] * (*(v5p + iy) - *(v5m + iy))) * *(odn + ix);
                }
            }
        }
    }
}


void d2yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict vix;
    const unsigned int *restrict Py = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;
                vix = v + idx;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    *(dv + idy) = (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                    a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                    a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                    a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                    a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * odn;
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
                        *(dv + idy) = (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                        a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                        a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                        a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                        a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * odn;
                }
            }
        }
    }
}


void d2yP_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int *restrict P,
                const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict vix;
    const unsigned int *restrict Py = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;
                vix = v + idx;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy;
                    *(dv + idy) = (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                    a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                    a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                    a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                    a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * *(odn + iy);
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
                        *(dv + idy) = (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                        a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                        a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                        a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                        a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * *(odn + iy);
                }
            }
        }
    }
}


void d2xp_s(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;

    const double *restrict v1 = v + ny;
    const double *restrict v2 = v1 + ny;
    const double *restrict v3 = v2 + ny;
    const double *restrict v4 = v3 + ny;
    const double *restrict v5 = v4 + ny;
    const double *restrict v6 = v5 + ny;
    const double *restrict v7 = v6 + ny;
    const double *restrict v8 = v7 + ny;
    const double *restrict v9 = v8 + ny;
    const double *restrict v10 = v9 + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                dvdx_ix = dvdx + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = (a11d[ix][0] * *(v + iy) +
                                       a11d[ix][1] * *(v1 + iy) +
                                       a11d[ix][2] * *(v2 + iy) +
                                       a11d[ix][3] * *(v3 + iy) +
                                       a11d[ix][4] * *(v4 + iy) +
                                       a11d[ix][5] * *(v5 + iy) +
                                       a11d[ix][6] * *(v6 + iy) +
                                       a11d[ix][7] * *(v7 + iy) +
                                       a11d[ix][8] * *(v8 + iy) +
                                       a11d[ix][9] * *(v9 + iy) +
                                       a11d[ix][10] * *(v10 + iy)) * odx;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx + ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = (a11d[ix][0] * *(v + iy) +
                                           a11d[ix][1] * *(v1 + iy) +
                                           a11d[ix][2] * *(v2 + iy) +
                                           a11d[ix][3] * *(v3 + iy) +
                                           a11d[ix][4] * *(v4 + iy) +
                                           a11d[ix][5] * *(v5 + iy) +
                                           a11d[ix][6] * *(v6 + iy) +
                                           a11d[ix][7] * *(v7 + iy) +
                                           a11d[ix][8] * *(v8 + iy) +
                                           a11d[ix][9] * *(v9 + iy) +
                                           a11d[ix][10] * *(v10 + iy)) * odx;
                }
            }
        }
    }
}


void d2xp_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;
    odx += ixmin;

    const double *restrict v1 = v + ny;
    const double *restrict v2 = v1 + ny;
    const double *restrict v3 = v2 + ny;
    const double *restrict v4 = v3 + ny;
    const double *restrict v5 = v4 + ny;
    const double *restrict v6 = v5 + ny;
    const double *restrict v7 = v6 + ny;
    const double *restrict v8 = v7 + ny;
    const double *restrict v9 = v8 + ny;
    const double *restrict v10 = v9 + ny;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                dvdx_ix = dvdx + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = (a11d[ix][0] * *(v + iy) +
                                       a11d[ix][1] * *(v1 + iy) +
                                       a11d[ix][2] * *(v2 + iy) +
                                       a11d[ix][3] * *(v3 + iy) +
                                       a11d[ix][4] * *(v4 + iy) +
                                       a11d[ix][5] * *(v5 + iy) +
                                       a11d[ix][6] * *(v6 + iy) +
                                       a11d[ix][7] * *(v7 + iy) +
                                       a11d[ix][8] * *(v8 + iy) +
                                       a11d[ix][9] * *(v9 + iy) +
                                       a11d[ix][10] * *(v10 + iy)) * *(odx + ix);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx + ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = (a11d[ix][0] * *(v + iy) +
                                           a11d[ix][1] * *(v1 + iy) +
                                           a11d[ix][2] * *(v2 + iy) +
                                           a11d[ix][3] * *(v3 + iy) +
                                           a11d[ix][4] * *(v4 + iy) +
                                           a11d[ix][5] * *(v5 + iy) +
                                           a11d[ix][6] * *(v6 + iy) +
                                           a11d[ix][7] * *(v7 + iy) +
                                           a11d[ix][8] * *(v8 + iy) +
                                           a11d[ix][9] * *(v9 + iy) +
                                           a11d[ix][10] * *(v10 + iy)) * *(odx + ix);
                }
            }
        }
    }
}


void d2yp_s(double *restrict dvdy, const double *restrict v, const double ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;

    const double *restrict v1 = v + 1;
    const double *restrict v2 = v1 + 1;
    const double *restrict v3 = v2 + 1;
    const double *restrict v4 = v3 + 1;
    const double *restrict v5 = v4 + 1;
    const double *restrict v6 = v5 + 1;
    const double *restrict v7 = v6 + 1;
    const double *restrict v8 = v7 + 1;
    const double *restrict v9 = v8 + 1;
    const double *restrict v10 = v9 + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * ny;
                dvdy_ix = dvdy + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dvdy_ix + iy) = (a11d[iy][0] * *(v + idx) +
                                       a11d[iy][1] * *(v1 + idx) +
                                       a11d[iy][2] * *(v2 + idx) +
                                       a11d[iy][3] * *(v3 + idx) +
                                       a11d[iy][4] * *(v4 + idx) +
                                       a11d[iy][5] * *(v5 + idx) +
                                       a11d[iy][6] * *(v6 + idx) +
                                       a11d[iy][7] * *(v7 + idx) +
                                       a11d[iy][8] * *(v8 + idx) +
                                       a11d[iy][9] * *(v9 + idx) +
                                       a11d[iy][10] * *(v10 + idx)) * ody;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dvdy_ix = dvdy + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dvdy_ix + iy) = (a11d[iy][0] * *(v + idx) +
                                           a11d[iy][1] * *(v1 + idx) +
                                           a11d[iy][2] * *(v2 + idx) +
                                           a11d[iy][3] * *(v3 + idx) +
                                           a11d[iy][4] * *(v4 + idx) +
                                           a11d[iy][5] * *(v5 + idx) +
                                           a11d[iy][6] * *(v6 + idx) +
                                           a11d[iy][7] * *(v7 + idx) +
                                           a11d[iy][8] * *(v8 + idx) +
                                           a11d[iy][9] * *(v9 + idx) +
                                           a11d[iy][10] * *(v10 + idx)) * ody;
                    }
                }
            }
    }
}


void d2yp_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;
    ody += iymin;

    const double *restrict v1 = v + 1;
    const double *restrict v2 = v1 + 1;
    const double *restrict v3 = v2 + 1;
    const double *restrict v4 = v3 + 1;
    const double *restrict v5 = v4 + 1;
    const double *restrict v6 = v5 + 1;
    const double *restrict v7 = v6 + 1;
    const double *restrict v8 = v7 + 1;
    const double *restrict v9 = v8 + 1;
    const double *restrict v10 = v9 + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * ny;
                dvdy_ix = dvdy + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dvdy_ix + iy) = (a11d[iy][0] * *(v + idx) +
                                       a11d[iy][1] * *(v1 + idx) +
                                       a11d[iy][2] * *(v2 + idx) +
                                       a11d[iy][3] * *(v3 + idx) +
                                       a11d[iy][4] * *(v4 + idx) +
                                       a11d[iy][5] * *(v5 + idx) +
                                       a11d[iy][6] * *(v6 + idx) +
                                       a11d[iy][7] * *(v7 + idx) +
                                       a11d[iy][8] * *(v8 + idx) +
                                       a11d[iy][9] * *(v9 + idx) +
                                       a11d[iy][10] * *(v10 + idx)) * *(ody + iy);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dvdy_ix = dvdy + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dvdy_ix + iy) = (a11d[iy][0] * *(v + idx) +
                                           a11d[iy][1] * *(v1 + idx) +
                                           a11d[iy][2] * *(v2 + idx) +
                                           a11d[iy][3] * *(v3 + idx) +
                                           a11d[iy][4] * *(v4 + idx) +
                                           a11d[iy][5] * *(v5 + idx) +
                                           a11d[iy][6] * *(v6 + idx) +
                                           a11d[iy][7] * *(v7 + idx) +
                                           a11d[iy][8] * *(v8 + idx) +
                                           a11d[iy][9] * *(v9 + idx) +
                                           a11d[iy][10] * *(v10 + idx)) * *(ody + iy);
                }
            }
        }
    }
}


void d2xm_s(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;

    const double *restrict v1 = v - ny;
    const double *restrict v2 = v1 - ny;
    const double *restrict v3 = v2 - ny;
    const double *restrict v4 = v3 - ny;
    const double *restrict v5 = v4 - ny;
    const double *restrict v6 = v5 - ny;
    const double *restrict v7 = v6 - ny;
    const double *restrict v8 = v7 - ny;
    const double *restrict v9 = v8 - ny;
    const double *restrict v10 = v9 - ny;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                dvdx_ix = dvdx - ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    *(dvdx_ix + iy) = - (a11d[ix][0] * *(v + iy) +
                                         a11d[ix][1] * *(v1 + iy) +
                                         a11d[ix][2] * *(v2 + iy) +
                                         a11d[ix][3] * *(v3 + iy) +
                                         a11d[ix][4] * *(v4 + iy) +
                                         a11d[ix][5] * *(v5 + iy) +
                                         a11d[ix][6] * *(v6 + iy) +
                                         a11d[ix][7] * *(v7 + iy) +
                                         a11d[ix][8] * *(v8 + iy) +
                                         a11d[ix][9] * *(v9 + iy) +
                                         a11d[ix][10] * *(v10 + iy)) * odx;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx - ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        *(dvdx_ix + iy) = - (a11d[ix][0] * *(v + iy) +
                                             a11d[ix][1] * *(v1 + iy) +
                                             a11d[ix][2] * *(v2 + iy) +
                                             a11d[ix][3] * *(v3 + iy) +
                                             a11d[ix][4] * *(v4 + iy) +
                                             a11d[ix][5] * *(v5 + iy) +
                                             a11d[ix][6] * *(v6 + iy) +
                                             a11d[ix][7] * *(v7 + iy) +
                                             a11d[ix][8] * *(v8 + iy) +
                                             a11d[ix][9] * *(v9 + iy) +
                                             a11d[ix][10] * *(v10 + iy)) * odx;
                }
            }
        }
    }
}


void d2xm_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;
    odx += ixmax;

    const double *restrict v1 = v - ny;
    const double *restrict v2 = v1 - ny;
    const double *restrict v3 = v2 - ny;
    const double *restrict v4 = v3 - ny;
    const double *restrict v5 = v4 - ny;
    const double *restrict v6 = v5 - ny;
    const double *restrict v7 = v6 - ny;
    const double *restrict v8 = v7 - ny;
    const double *restrict v9 = v8 - ny;
    const double *restrict v10 = v9 - ny;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                dvdx_ix = dvdx - ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    *(dvdx_ix + iy) = - (a11d[ix][0] * *(v + iy) +
                                         a11d[ix][1] * *(v1 + iy) +
                                         a11d[ix][2] * *(v2 + iy) +
                                         a11d[ix][3] * *(v3 + iy) +
                                         a11d[ix][4] * *(v4 + iy) +
                                         a11d[ix][5] * *(v5 + iy) +
                                         a11d[ix][6] * *(v6 + iy) +
                                         a11d[ix][7] * *(v7 + iy) +
                                         a11d[ix][8] * *(v8 + iy) +
                                         a11d[ix][9] * *(v9 + iy) +
                                         a11d[ix][10] * *(v10 + iy)) * *(odx - ix);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx - ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        *(dvdx_ix + iy) = - (a11d[ix][0] * *(v + iy) +
                                             a11d[ix][1] * *(v1 + iy) +
                                             a11d[ix][2] * *(v2 + iy) +
                                             a11d[ix][3] * *(v3 + iy) +
                                             a11d[ix][4] * *(v4 + iy) +
                                             a11d[ix][5] * *(v5 + iy) +
                                             a11d[ix][6] * *(v6 + iy) +
                                             a11d[ix][7] * *(v7 + iy) +
                                             a11d[ix][8] * *(v8 + iy) +
                                             a11d[ix][9] * *(v9 + iy) +
                                             a11d[ix][10] * *(v10 + iy)) * *(odx - ix);
                }
            }
        }
    }
}


void d2ym_s(double *restrict dvdy, const double *restrict v, const double ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;

    const double *restrict v1 = v - 1;
    const double *restrict v2 = v1 - 1;
    const double *restrict v3 = v2 - 1;
    const double *restrict v4 = v3 - 1;
    const double *restrict v5 = v4 - 1;
    const double *restrict v6 = v5 - 1;
    const double *restrict v7 = v6 - 1;
    const double *restrict v8 = v7 - 1;
    const double *restrict v9 = v8 - 1;
    const double *restrict v10 = v9 - 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * ny;
                dvdy_ix = dvdy + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dvdy_ix - iy) = - (a11d[iy][0] * *(v + idx) +
                                         a11d[iy][1] * *(v1 + idx) +
                                         a11d[iy][2] * *(v2 + idx) +
                                         a11d[iy][3] * *(v3 + idx) +
                                         a11d[iy][4] * *(v4 + idx) +
                                         a11d[iy][5] * *(v5 + idx) +
                                         a11d[iy][6] * *(v6 + idx) +
                                         a11d[iy][7] * *(v7 + idx) +
                                         a11d[iy][8] * *(v8 + idx) +
                                         a11d[iy][9] * *(v9 + idx) +
                                         a11d[iy][10] * *(v10 + idx)) * ody;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dvdy_ix = dvdy + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dvdy_ix - iy) = - (a11d[iy][0] * *(v + idx) +
                                             a11d[iy][1] * *(v1 + idx) +
                                             a11d[iy][2] * *(v2 + idx) +
                                             a11d[iy][3] * *(v3 + idx) +
                                             a11d[iy][4] * *(v4 + idx) +
                                             a11d[iy][5] * *(v5 + idx) +
                                             a11d[iy][6] * *(v6 + idx) +
                                             a11d[iy][7] * *(v7 + idx) +
                                             a11d[iy][8] * *(v8 + idx) +
                                             a11d[iy][9] * *(v9 + idx) +
                                             a11d[iy][10] * *(v10 + idx)) * ody;
                }
            }
        }
    }
}


void d2ym_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
            const unsigned int ny,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;
    ody += iymax;

    const double *restrict v1 = v - 1;
    const double *restrict v2 = v1 - 1;
    const double *restrict v3 = v2 - 1;
    const double *restrict v4 = v3 - 1;
    const double *restrict v5 = v4 - 1;
    const double *restrict v6 = v5 - 1;
    const double *restrict v7 = v6 - 1;
    const double *restrict v8 = v7 - 1;
    const double *restrict v9 = v8 - 1;
    const double *restrict v10 = v9 - 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * ny;
                dvdy_ix = dvdy + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dvdy_ix - iy) = - (a11d[iy][0] * *(v + idx) +
                                         a11d[iy][1] * *(v1 + idx) +
                                         a11d[iy][2] * *(v2 + idx) +
                                         a11d[iy][3] * *(v3 + idx) +
                                         a11d[iy][4] * *(v4 + idx) +
                                         a11d[iy][5] * *(v5 + idx) +
                                         a11d[iy][6] * *(v6 + idx) +
                                         a11d[iy][7] * *(v7 + idx) +
                                         a11d[iy][8] * *(v8 + idx) +
                                         a11d[iy][9] * *(v9 + idx) +
                                         a11d[iy][10] * *(v10 + idx)) * *(ody - iy);
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dvdy_ix = dvdy + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dvdy_ix - iy) = - (a11d[iy][0] * *(v + idx) +
                                             a11d[iy][1] * *(v1 + idx) +
                                             a11d[iy][2] * *(v2 + idx) +
                                             a11d[iy][3] * *(v3 + idx) +
                                             a11d[iy][4] * *(v4 + idx) +
                                             a11d[iy][5] * *(v5 + idx) +
                                             a11d[iy][6] * *(v6 + idx) +
                                             a11d[iy][7] * *(v7 + idx) +
                                             a11d[iy][8] * *(v8 + idx) +
                                             a11d[iy][9] * *(v9 + idx) +
                                             a11d[iy][10] * *(v10 + idx)) * *(ody - iy);
                }
            }
        }
    }
}


/*----------------------------*/
/* Global 2d differentiation */
/*--------------------------*/


void d2x_s(double *restrict dvdx, const double *restrict v, const double odx,
           const unsigned int nx, const unsigned int ny, const unsigned int threads) {

    d2xc_s(dvdx, v, odx, ny, 5, nx - 6, 0, ny - 1, threads);
    d2xp_s(dvdx, v, odx, ny, 0, 4, 0, ny - 1, 1);
    d2xm_s(dvdx, v, odx, ny, nx - 5, nx - 1, 0, ny - 1, 1);
}


void d2x_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
           const unsigned int nx, const unsigned int ny, const unsigned int threads) {

    d2xc_v(dvdx, v, odx, ny, 5, nx - 6, 0, ny - 1, threads);
    d2xp_v(dvdx, v, odx, ny, 0, 4, 0, ny - 1, 1);
    d2xm_v(dvdx, v, odx, ny, nx - 5, nx - 1, 0, ny - 1, 1);
}


void d2y_s(double *restrict dvdy, const double *restrict v, const double ody,
           const unsigned int nx, const unsigned int ny, const unsigned int threads) {

    d2yc_s(dvdy, v, ody, ny, 0, nx - 1, 5, ny - 6, threads);
    d2yp_s(dvdy, v, ody, ny, 0, nx - 1, 0, 4, 1);
    d2ym_s(dvdy, v, ody, ny, 0, nx - 1, ny - 5, ny - 1, 1);
}


void d2y_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
           const unsigned int nx, const unsigned int ny, const unsigned int threads) {

    d2yc_v(dvdy, v, ody, ny, 0, nx - 1, 5, ny - 6, threads);
    d2yp_v(dvdy, v, ody, ny, 0, nx - 1, 0, 4, 1);
    d2ym_v(dvdy, v, ody, ny, 0, nx - 1, ny - 5, ny - 1, 1);
}


/*-------------------------------*/
/* Subdomain 3d differentiation */
/*-----------------------------*/


void d3xc_s(double *restrict dvdx, const double *restrict v, const double odx,
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
    dvdx += offset;

    const double *restrict v_1m = v - nynz;
    const double *restrict v_2m = v_1m - nynz;
    const double *restrict v_3m = v_2m - nynz;
    const double *restrict v_4m = v_3m - nynz;
    const double *restrict v_5m = v_4m - nynz;

    const double *restrict v_1p = v + nynz;
    const double *restrict v_2p = v_1p + nynz;
    const double *restrict v_3p = v_2p + nynz;
    const double *restrict v_4p = v_3p + nynz;
    const double *restrict v_5p = v_4p + nynz;

    switch(threads){
        case 1:
            for (ix=0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy=0; iy <= my; iy++){
                    idy = idx + iy * nz;

                    for (iz=0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odx;
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
                        *(dvdx + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odx;
                    }
                }
            }
        }
    }
}


void d3xc_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
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
    dvdx += offset;
    odx += ixmin;

    const double *restrict v_1m = v - nynz;
    const double *restrict v_2m = v_1m - nynz;
    const double *restrict v_3m = v_2m - nynz;
    const double *restrict v_4m = v_3m - nynz;
    const double *restrict v_5m = v_4m - nynz;

    const double *restrict v_1p = v + nynz;
    const double *restrict v_2p = v_1p + nynz;
    const double *restrict v_3p = v_2p + nynz;
    const double *restrict v_4p = v_3p + nynz;
    const double *restrict v_5p = v_4p + nynz;

    switch(threads){
        case 1:
            for (ix=0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy=0; iy <= my; iy++){
                    idy = idx + iy * nz;

                    for (iz=0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odx + ix);
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
                        *(dvdx + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odx + ix);
                    }
                }
            }
        }
    }
}


void d3yc_s(double *restrict dvdy, const double *restrict v, const double ody,
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
    dvdy += offset;

    const double *restrict v_1m = v - nz;
    const double *restrict v_2m = v_1m - nz;
    const double *restrict v_3m = v_2m - nz;
    const double *restrict v_4m = v_3m - nz;
    const double *restrict v_5m = v_4m - nz;

    const double *restrict v_1p = v + nz;
    const double *restrict v_2p = v_1p + nz;
    const double *restrict v_3p = v_2p + nz;
    const double *restrict v_4p = v_3p + nz;
    const double *restrict v_5p = v_4p + nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        *(dvdy + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * ody;
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
                            *(dvdy + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                             a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                             a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                             a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                             a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * ody;
                    }
                }
            }
        }
    }
}


void d3yc_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
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
    dvdy += offset;
    ody += iymin;

    const double *restrict v_1m = v - nz;
    const double *restrict v_2m = v_1m - nz;
    const double *restrict v_3m = v_2m - nz;
    const double *restrict v_4m = v_3m - nz;
    const double *restrict v_5m = v_4m - nz;

    const double *restrict v_1p = v + nz;
    const double *restrict v_2p = v_1p + nz;
    const double *restrict v_3p = v_2p + nz;
    const double *restrict v_4p = v_3p + nz;
    const double *restrict v_5p = v_4p + nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        *(dvdy + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(ody + iy);
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
                            *(dvdy + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                             a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                             a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                             a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                             a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(ody + iy);
                    }
                }
            }
        }
    }
}


void d3zc_s(double *restrict dvdz, const double *restrict v, const double odz,
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
    dvdz += offset;

    const double *restrict v_1m = v - 1;
    const double *restrict v_2m = v_1m - 1;
    const double *restrict v_3m = v_2m - 1;
    const double *restrict v_4m = v_3m - 1;
    const double *restrict v_5m = v_4m - 1;

    const double *restrict v_1p = v + 1;
    const double *restrict v_2p = v_1p + 1;
    const double *restrict v_3p = v_2p + 1;
    const double *restrict v_4p = v_3p + 1;
    const double *restrict v_5p = v_4p + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        *(dvdz + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odz;
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
                        *(dvdz + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odz;
                    }
                }
            }
        }
    }
}


void d3zc_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
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
    dvdz += offset;
    odz += izmin;

    const double *restrict v_1m = v - 1;
    const double *restrict v_2m = v_1m - 1;
    const double *restrict v_3m = v_2m - 1;
    const double *restrict v_4m = v_3m - 1;
    const double *restrict v_5m = v_4m - 1;

    const double *restrict v_1p = v + 1;
    const double *restrict v_2p = v_1p + 1;
    const double *restrict v_3p = v_2p + 1;
    const double *restrict v_4p = v_3p + 1;
    const double *restrict v_5p = v_4p + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        *(dvdz + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odz + iz);
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
                        *(dvdz + idz) = (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                         a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                         a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                         a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                         a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odz + iz);
                    }
                }
            }
        }
    }
}


void d3xP_s(double *restrict dv, const double *restrict v,
            const double odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                v1p = v + *(Px + ix + 1) * nynz;
                v2p = v + *(Px + ix + 2) * nynz;
                v3p = v + *(Px + ix + 3) * nynz;
                v4p = v + *(Px + ix + 4) * nynz;
                v5p = v + *(Px + ix + 5) * nynz;

                v1m = v + *(Px + ix - 1) * nynz;
                v2m = v + *(Px + ix - 2) * nynz;
                v3m = v + *(Px + ix - 3) * nynz;
                v4m = v + *(Px + ix - 4) * nynz;
                v5m = v + *(Px + ix - 5) * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        *(dv + idz) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                        a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                        a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                        a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                        a11c[5] * (*(v5p + iz) - *(v5m + iz))) * odn;
                    }
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    v1p = v + *(Px + ix + 1) * nynz;
                    v2p = v + *(Px + ix + 2) * nynz;
                    v3p = v + *(Px + ix + 3) * nynz;
                    v4p = v + *(Px + ix + 4) * nynz;
                    v5p = v + *(Px + ix + 5) * nynz;

                    v1m = v + *(Px + ix - 1) * nynz;
                    v2m = v + *(Px + ix - 2) * nynz;
                    v3m = v + *(Px + ix - 3) * nynz;
                    v4m = v + *(Px + ix - 4) * nynz;
                    v5m = v + *(Px + ix - 5) * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            *(dv + idz) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                            a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                            a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                            a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                            a11c[5] * (*(v5p + iz) - *(v5m + iz))) * odn;
                    }
                }
            }
        }
    }
}


void d3xP_v(double *restrict dv, const double *restrict v,
            const double *restrict odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, idn;
    unsigned int nynz = ny * nz;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                v1p = v + *(Px + ix + 1) * nynz;
                v2p = v + *(Px + ix + 2) * nynz;
                v3p = v + *(Px + ix + 3) * nynz;
                v4p = v + *(Px + ix + 4) * nynz;
                v5p = v + *(Px + ix + 5) * nynz;

                v1m = v + *(Px + ix - 1) * nynz;
                v2m = v + *(Px + ix - 2) * nynz;
                v3m = v + *(Px + ix - 3) * nynz;
                v4m = v + *(Px + ix - 4) * nynz;
                v5m = v + *(Px + ix - 5) * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idx + idy + iz;
                        idn = idy + iz;
                        *(dv + idz) = (a11c[1] * (*(v1p + idn) - *(v1m + idn)) +
                                        a11c[2] * (*(v2p + idn) - *(v2m + idn)) +
                                        a11c[3] * (*(v3p + idn) - *(v3m + idn)) +
                                        a11c[4] * (*(v4p + idn) - *(v4m + idn)) +
                                        a11c[5] * (*(v5p + idn) - *(v5m + idn))) * *(odn + ix);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, idn, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    v1p = v + *(Px + ix + 1) * nynz;
                    v2p = v + *(Px + ix + 2) * nynz;
                    v3p = v + *(Px + ix + 3) * nynz;
                    v4p = v + *(Px + ix + 4) * nynz;
                    v5p = v + *(Px + ix + 5) * nynz;

                    v1m = v + *(Px + ix - 1) * nynz;
                    v2m = v + *(Px + ix - 2) * nynz;
                    v3m = v + *(Px + ix - 3) * nynz;
                    v4m = v + *(Px + ix - 4) * nynz;
                    v5m = v + *(Px + ix - 5) * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = iy * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idx + idy + iz;
                            idn = idy + iz;
                            *(dv + idz) = (a11c[1] * (*(v1p + idn) - *(v1m + idn)) +
                                            a11c[2] * (*(v2p + idn) - *(v2m + idn)) +
                                            a11c[3] * (*(v3p + idn) - *(v3m + idn)) +
                                            a11c[4] * (*(v4p + idn) - *(v4m + idn)) +
                                            a11c[5] * (*(v5p + idn) - *(v5m + idn))) * *(odn + ix);
                    }
                }
            }
        }
    }
}


void d3yP_s(double *restrict dv, const double *restrict v,
            const double odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Py = P + 5;


    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    v1p = v + idx + *(Py + iy + 1) * nz;
                    v2p = v + idx + *(Py + iy + 2) * nz;
                    v3p = v + idx + *(Py + iy + 3) * nz;
                    v4p = v + idx + *(Py + iy + 4) * nz;
                    v5p = v + idx + *(Py + iy + 5) * nz;

                    v1m = v + idx + *(Py + iy - 1) * nz;
                    v2m = v + idx + *(Py + iy - 2) * nz;
                    v3m = v + idx + *(Py + iy - 3) * nz;
                    v4m = v + idx + *(Py + iy - 4) * nz;
                    v5m = v + idx + *(Py + iy - 5) * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        *(dv + idy) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                        a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                        a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                        a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                        a11c[5] * (*(v5p + iz) - *(v5m + iz))) * odn;
                    }
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {

                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {

                        idy = idx + iy * nz;

                        v1p = v + idx + *(Py + iy + 1) * nz;
                        v2p = v + idx + *(Py + iy + 2) * nz;
                        v3p = v + idx + *(Py + iy + 3) * nz;
                        v4p = v + idx + *(Py + iy + 4) * nz;
                        v5p = v + idx + *(Py + iy + 5) * nz;

                        v1m = v + idx + *(Py + iy - 1) * nz;
                        v2m = v + idx + *(Py + iy - 2) * nz;
                        v3m = v + idx + *(Py + iy - 3) * nz;
                        v4m = v + idx + *(Py + iy - 4) * nz;
                        v5m = v + idx + *(Py + iy - 5) * nz;

                        for (iz = izmin; iz <= izmax; iz++) {

                            idz = idy + iz;

                            *(dv + idy) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                            a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                            a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                            a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                            a11c[5] * (*(v5p + iz) - *(v5m + iz))) * odn;
                    }
                }
            }
        }
    }
}


void d3yP_v(double *restrict dv, const double *restrict v,
            const double *restrict odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Py = P + 5;


    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    v1p = v + idx + *(Py + iy + 1) * nz;
                    v2p = v + idx + *(Py + iy + 2) * nz;
                    v3p = v + idx + *(Py + iy + 3) * nz;
                    v4p = v + idx + *(Py + iy + 4) * nz;
                    v5p = v + idx + *(Py + iy + 5) * nz;

                    v1m = v + idx + *(Py + iy - 1) * nz;
                    v2m = v + idx + *(Py + iy - 2) * nz;
                    v3m = v + idx + *(Py + iy - 3) * nz;
                    v4m = v + idx + *(Py + iy - 4) * nz;
                    v5m = v + idx + *(Py + iy - 5) * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        *(dv + idy) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                        a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                        a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                        a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                        a11c[5] * (*(v5p + iz) - *(v5m + iz))) * *(odn + iy);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;

                        v1p = v + idx + *(Py + iy + 1) * nz;
                        v2p = v + idx + *(Py + iy + 2) * nz;
                        v3p = v + idx + *(Py + iy + 3) * nz;
                        v4p = v + idx + *(Py + iy + 4) * nz;
                        v5p = v + idx + *(Py + iy + 5) * nz;

                        v1m = v + idx + *(Py + iy - 1) * nz;
                        v2m = v + idx + *(Py + iy - 2) * nz;
                        v3m = v + idx + *(Py + iy - 3) * nz;
                        v4m = v + idx + *(Py + iy - 4) * nz;
                        v5m = v + idx + *(Py + iy - 5) * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            *(dv + idy) = (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                            a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                            a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                            a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                            a11c[5] * (*(v5p + iz) - *(v5m + iz))) * *(odn + iy);
                    }
                }
            }
        }
    }
}


void d3zP_s(double *restrict dv, const double *restrict v,
            const double odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        *(dv + idy) = (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(P + iz - 1))) +
                                        a11c[2] * (*(v + idy + *(Pz + iz + 2)) - *(v + idy + *(P + iz - 2))) +
                                        a11c[3] * (*(v + idy + *(Pz + iz + 3)) - *(v + idy + *(P + iz - 3))) +
                                        a11c[4] * (*(v + idy + *(Pz + iz + 4)) - *(v + idy + *(P + iz - 4))) +
                                        a11c[5] * (*(v + idy + *(Pz + iz + 5)) - *(v + idy + *(P + iz - 5)))) * odn;
                    }
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            *(dv + idy) = (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(P + iz - 1))) +
                                            a11c[2] * (*(v + idy + *(Pz + iz + 2)) - *(v + idy + *(P + iz - 2))) +
                                            a11c[3] * (*(v + idy + *(Pz + iz + 3)) - *(v + idy + *(P + iz - 3))) +
                                            a11c[4] * (*(v + idy + *(Pz + iz + 4)) - *(v + idy + *(P + iz - 4))) +
                                            a11c[5] * (*(v + idy + *(Pz + iz + 5)) - *(v + idy + *(P + iz - 5)))) * odn;
                    }
                }
            }
        }
    }
}


void d3zP_v(double *restrict dv, const double *restrict v,
            const double *restrict odn, const unsigned int *restrict P,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax, const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;

                    for (iz = izmin; iz <= izmax; iz++) {
                        idz = idy + iz;
                        *(dv + idy) = (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(Pz + iz - 1))) +
                                        a11c[2] * (*(v + idy + *(Pz + iz + 2)) - *(v + idy + *(Pz + iz - 2))) +
                                        a11c[3] * (*(v + idy + *(Pz + iz + 3)) - *(v + idy + *(Pz + iz - 3))) +
                                        a11c[4] * (*(v + idy + *(Pz + iz + 4)) - *(v + idy + *(Pz + iz - 4))) +
                                        a11c[5] * (*(v + idy + *(Pz + iz + 5)) - *(v + idy + *(Pz + iz - 5)))) * *(odn + iz);
                    }
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            *(dv + idy) = (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(Pz + iz - 1))) +
                                            a11c[2] * (*(v + idy + *(Pz + iz + 2)) - *(v + idy + *(Pz + iz - 2))) +
                                            a11c[3] * (*(v + idy + *(Pz + iz + 3)) - *(v + idy + *(Pz + iz - 3))) +
                                            a11c[4] * (*(v + idy + *(Pz + iz + 4)) - *(v + idy + *(Pz + iz - 4))) +
                                            a11c[5] * (*(v + idy + *(Pz + iz + 5)) - *(v + idy + *(Pz + iz - 5)))) * *(odn + iz);
                    }
                }
            }
        }
    }
}



void d3xp_s(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(ixmax);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;

    const double *restrict v1 = v + nynz;
    const double *restrict v2 = v1 + nynz;
    const double *restrict v3 = v2 + nynz;
    const double *restrict v4 = v3 + nynz;
    const double *restrict v5 = v4 + nynz;
    const double *restrict v6 = v5 + nynz;
    const double *restrict v7 = v6 + nynz;
    const double *restrict v8 = v7 + nynz;
    const double *restrict v9 = v8 + nynz;
    const double *restrict v10 = v9 + nynz;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = iy * nz;
                    dvdx_ix = dvdx + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = (a11d[ix][0] * *(v + idz) +
                                           a11d[ix][1] * *(v1 + idz) +
                                           a11d[ix][2] * *(v2 + idz) +
                                           a11d[ix][3] * *(v3 + idz) +
                                           a11d[ix][4] * *(v4 + idz) +
                                           a11d[ix][5] * *(v5 + idz) +
                                           a11d[ix][6] * *(v6 + idz) +
                                           a11d[ix][7] * *(v7 + idz) +
                                           a11d[ix][8] * *(v8 + idz) +
                                           a11d[ix][9] * *(v9 + idz) +
                                           a11d[ix][10] * *(v10 + idz)) * odx;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = (a11d[ix][0] * *(v + idz) +
                                            a11d[ix][1] * *(v1 + idz) +
                                            a11d[ix][2] * *(v2 + idz) +
                                            a11d[ix][3] * *(v3 + idz) +
                                            a11d[ix][4] * *(v4 + idz) +
                                            a11d[ix][5] * *(v5 + idz) +
                                            a11d[ix][6] * *(v6 + idz) +
                                            a11d[ix][7] * *(v7 + idz) +
                                            a11d[ix][8] * *(v8 + idz) +
                                            a11d[ix][9] * *(v9 + idz) +
                                            a11d[ix][10] * *(v10 + idz)) * odx;
                    }
                }
            }
        }
    }
}


void d3xp_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(ixmax);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;
    odx += ixmin;

    const double *restrict v1 = v + nynz;
    const double *restrict v2 = v1 + nynz;
    const double *restrict v3 = v2 + nynz;
    const double *restrict v4 = v3 + nynz;
    const double *restrict v5 = v4 + nynz;
    const double *restrict v6 = v5 + nynz;
    const double *restrict v7 = v6 + nynz;
    const double *restrict v8 = v7 + nynz;
    const double *restrict v9 = v8 + nynz;
    const double *restrict v10 = v9 + nynz;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = iy * nz;
                    dvdx_ix = dvdx + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = (a11d[ix][0] * *(v + idz) +
                                           a11d[ix][1] * *(v1 + idz) +
                                           a11d[ix][2] * *(v2 + idz) +
                                           a11d[ix][3] * *(v3 + idz) +
                                           a11d[ix][4] * *(v4 + idz) +
                                           a11d[ix][5] * *(v5 + idz) +
                                           a11d[ix][6] * *(v6 + idz) +
                                           a11d[ix][7] * *(v7 + idz) +
                                           a11d[ix][8] * *(v8 + idz) +
                                           a11d[ix][9] * *(v9 + idz) +
                                           a11d[ix][10] * *(v10 + idz)) * *(odx + ix);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = (a11d[ix][0] * *(v + idz) +
                                            a11d[ix][1] * *(v1 + idz) +
                                            a11d[ix][2] * *(v2 + idz) +
                                            a11d[ix][3] * *(v3 + idz) +
                                            a11d[ix][4] * *(v4 + idz) +
                                            a11d[ix][5] * *(v5 + idz) +
                                            a11d[ix][6] * *(v6 + idz) +
                                            a11d[ix][7] * *(v7 + idz) +
                                            a11d[ix][8] * *(v8 + idz) +
                                            a11d[ix][9] * *(v9 + idz) +
                                            a11d[ix][10] * *(v10 + idz)) * *(odx + ix);
                    }
                }
            }
        }
    }
}


void d3yp_s(double *restrict dvdy, const double *restrict v, const double ody,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, iz, idx, idy, idz, idv;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    dvdy += offset;

    const double *restrict v1 = v + nz;
    const double *restrict v2 = v1 + nz;
    const double *restrict v3 = v2 + nz;
    const double *restrict v4 = v3 + nz;
    const double *restrict v5 = v4 + nz;
    const double *restrict v6 = v5 + nz;
    const double *restrict v7 = v6 + nz;
    const double *restrict v8 = v7 + nz;
    const double *restrict v9 = v8 + nz;
    const double *restrict v10 = v9 + nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy < 5; iy++){
                    idy = iy * nz;

                    for (iz = 0; iz <= mz; iz++){
                        idv = idx + iz;
                        idz = idv + idy;
                        *(dvdy + idz) = (a11d[iy][0] * *(v + idv) +
                                         a11d[iy][1] * *(v1 + idv) +
                                         a11d[iy][2] * *(v2 + idv) +
                                         a11d[iy][3] * *(v3 + idv) +
                                         a11d[iy][4] * *(v4 + idv) +
                                         a11d[iy][5] * *(v5 + idv) +
                                         a11d[iy][6] * *(v6 + idv) +
                                         a11d[iy][7] * *(v7 + idv) +
                                         a11d[iy][8] * *(v8 + idv) +
                                         a11d[iy][9] * *(v9 + idv) +
                                         a11d[iy][10] * *(v10 + idv)) * ody;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, idv)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;

                        for (iz = 0; iz <= mz; iz++){
                            idv = idx + iz;
                            idz = idv + idy;
                            *(dvdy + idz) = (a11d[iy][0] * *(v + idv) +
                                             a11d[iy][1] * *(v1 + idv) +
                                             a11d[iy][2] * *(v2 + idv) +
                                             a11d[iy][3] * *(v3 + idv) +
                                             a11d[iy][4] * *(v4 + idv) +
                                             a11d[iy][5] * *(v5 + idv) +
                                             a11d[iy][6] * *(v6 + idv) +
                                             a11d[iy][7] * *(v7 + idv) +
                                             a11d[iy][8] * *(v8 + idv) +
                                             a11d[iy][9] * *(v9 + idv) +
                                             a11d[iy][10] * *(v10 + idv)) * ody;
                    }
                }
            }
        }
    }
}


void d3yp_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, iz, idx, idy, idz, idv;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    dvdy += offset;
    ody += iymin;

    const double *restrict v1 = v + nz;
    const double *restrict v2 = v1 + nz;
    const double *restrict v3 = v2 + nz;
    const double *restrict v4 = v3 + nz;
    const double *restrict v5 = v4 + nz;
    const double *restrict v6 = v5 + nz;
    const double *restrict v7 = v6 + nz;
    const double *restrict v8 = v7 + nz;
    const double *restrict v9 = v8 + nz;
    const double *restrict v10 = v9 + nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy < 5; iy++){
                    idy = iy * nz;

                    for (iz = 0; iz <= mz; iz++){
                        idv = idx + iz;
                        idz = idv + idy;
                        *(dvdy + idz) = (a11d[iy][0] * *(v + idv) +
                                         a11d[iy][1] * *(v1 + idv) +
                                         a11d[iy][2] * *(v2 + idv) +
                                         a11d[iy][3] * *(v3 + idv) +
                                         a11d[iy][4] * *(v4 + idv) +
                                         a11d[iy][5] * *(v5 + idv) +
                                         a11d[iy][6] * *(v6 + idv) +
                                         a11d[iy][7] * *(v7 + idv) +
                                         a11d[iy][8] * *(v8 + idv) +
                                         a11d[iy][9] * *(v9 + idv) +
                                         a11d[iy][10] * *(v10 + idv)) * *(ody + iy);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, idv)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;

                        for (iz = 0; iz <= mz; iz++){
                            idv = idx + iz;
                            idz = idv + idy;
                            *(dvdy + idz) = (a11d[iy][0] * *(v + idv) +
                                             a11d[iy][1] * *(v1 + idv) +
                                             a11d[iy][2] * *(v2 + idv) +
                                             a11d[iy][3] * *(v3 + idv) +
                                             a11d[iy][4] * *(v4 + idv) +
                                             a11d[iy][5] * *(v5 + idv) +
                                             a11d[iy][6] * *(v6 + idv) +
                                             a11d[iy][7] * *(v7 + idv) +
                                             a11d[iy][8] * *(v8 + idv) +
                                             a11d[iy][9] * *(v9 + idv) +
                                             a11d[iy][10] * *(v10 + idv)) * *(ody + iy);
                    }
                }
            }
        }
    }
}


void d3zp_s(double *restrict dvdz, const double *restrict v, const double odz,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(izmax);
    unsigned int ix, iy, iz, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double *restrict dvdz_ix;

    v += offset;
    dvdz += offset;

    const double *restrict v1 = v + 1;
    const double *restrict v2 = v1 + 1;
    const double *restrict v3 = v2 + 1;
    const double *restrict v4 = v3 + 1;
    const double *restrict v5 = v4 + 1;
    const double *restrict v6 = v5 + 1;
    const double *restrict v7 = v6 + 1;
    const double *restrict v8 = v7 + 1;
    const double *restrict v9 = v8 + 1;
    const double *restrict v10 = v9 + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = idx + iy * nz;
                    dvdz_ix = dvdz + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dvdz_ix + iz) = (a11d[iz][0] * *(v + idy) +
                                           a11d[iz][1] * *(v1 + idy) +
                                           a11d[iz][2] * *(v2 + idy) +
                                           a11d[iz][3] * *(v3 + idy) +
                                           a11d[iz][4] * *(v4 + idy) +
                                           a11d[iz][5] * *(v5 + idy) +
                                           a11d[iz][6] * *(v6 + idy) +
                                           a11d[iz][7] * *(v7 + idy) +
                                           a11d[iz][8] * *(v8 + idy) +
                                           a11d[iz][9] * *(v9 + idy) +
                                           a11d[iz][10] * *(v10 + idy)) * odz;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dvdz_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dvdz_ix = dvdz + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dvdz_ix + iz) = (a11d[iz][0] * *(v + idy) +
                                               a11d[iz][1] * *(v1 + idy) +
                                               a11d[iz][2] * *(v2 + idy) +
                                               a11d[iz][3] * *(v3 + idy) +
                                               a11d[iz][4] * *(v4 + idy) +
                                               a11d[iz][5] * *(v5 + idy) +
                                               a11d[iz][6] * *(v6 + idy) +
                                               a11d[iz][7] * *(v7 + idy) +
                                               a11d[iz][8] * *(v8 + idy) +
                                               a11d[iz][9] * *(v9 + idy) +
                                               a11d[iz][10] * *(v10 + idy)) * odz;
                    }
                }
            }
        }
    }
}


void d3zp_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(izmax);
    unsigned int ix, iy, iz, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;
    double *restrict dvdz_ix;

    v += offset;
    dvdz += offset;
    odz += izmin;

    const double *restrict v1 = v + 1;
    const double *restrict v2 = v1 + 1;
    const double *restrict v3 = v2 + 1;
    const double *restrict v4 = v3 + 1;
    const double *restrict v5 = v4 + 1;
    const double *restrict v6 = v5 + 1;
    const double *restrict v7 = v6 + 1;
    const double *restrict v8 = v7 + 1;
    const double *restrict v9 = v8 + 1;
    const double *restrict v10 = v9 + 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = idx + iy * nz;
                    dvdz_ix = dvdz + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dvdz_ix + iz) = (a11d[iz][0] * *(v + idy) +
                                           a11d[iz][1] * *(v1 + idy) +
                                           a11d[iz][2] * *(v2 + idy) +
                                           a11d[iz][3] * *(v3 + idy) +
                                           a11d[iz][4] * *(v4 + idy) +
                                           a11d[iz][5] * *(v5 + idy) +
                                           a11d[iz][6] * *(v6 + idy) +
                                           a11d[iz][7] * *(v7 + idy) +
                                           a11d[iz][8] * *(v8 + idy) +
                                           a11d[iz][9] * *(v9 + idy) +
                                           a11d[iz][10] * *(v10 + idy)) * *(odz + iz);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dvdz_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dvdz_ix = dvdz + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dvdz_ix + iz) = (a11d[iz][0] * *(v + idy) +
                                               a11d[iz][1] * *(v1 + idy) +
                                               a11d[iz][2] * *(v2 + idy) +
                                               a11d[iz][3] * *(v3 + idy) +
                                               a11d[iz][4] * *(v4 + idy) +
                                               a11d[iz][5] * *(v5 + idy) +
                                               a11d[iz][6] * *(v6 + idy) +
                                               a11d[iz][7] * *(v7 + idy) +
                                               a11d[iz][8] * *(v8 + idy) +
                                               a11d[iz][9] * *(v9 + idy) +
                                               a11d[iz][10] * *(v10 + idy)) * *(odz + iz);
                    }
                }
            }
        }
    }
}


void d3xm_s(double *restrict dvdx, const double *restrict v, const double odx,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(ixmin);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;

    const double *restrict v1 = v - nynz;
    const double *restrict v2 = v1 - nynz;
    const double *restrict v3 = v2 - nynz;
    const double *restrict v4 = v3 - nynz;
    const double *restrict v5 = v4 - nynz;
    const double *restrict v6 = v5 - nynz;
    const double *restrict v7 = v6 - nynz;
    const double *restrict v8 = v7 - nynz;
    const double *restrict v9 = v8 - nynz;
    const double *restrict v10 = v9 - nynz;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = iy * nz;
                    dvdx_ix = dvdx - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = - (a11d[ix][0] * *(v + idz) +
                                             a11d[ix][1] * *(v1 + idz) +
                                             a11d[ix][2] * *(v2 + idz) +
                                             a11d[ix][3] * *(v3 + idz) +
                                             a11d[ix][4] * *(v4 + idz) +
                                             a11d[ix][5] * *(v5 + idz) +
                                             a11d[ix][6] * *(v6 + idz) +
                                             a11d[ix][7] * *(v7 + idz) +
                                             a11d[ix][8] * *(v8 + idz) +
                                             a11d[ix][9] * *(v9 + idz) +
                                             a11d[ix][10] * *(v10 + idz)) * odx;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = - (a11d[ix][0] * *(v + idz) +
                                                 a11d[ix][1] * *(v1 + idz) +
                                                 a11d[ix][2] * *(v2 + idz) +
                                                 a11d[ix][3] * *(v3 + idz) +
                                                 a11d[ix][4] * *(v4 + idz) +
                                                 a11d[ix][5] * *(v5 + idz) +
                                                 a11d[ix][6] * *(v6 + idz) +
                                                 a11d[ix][7] * *(v7 + idz) +
                                                 a11d[ix][8] * *(v8 + idz) +
                                                 a11d[ix][9] * *(v9 + idz) +
                                                 a11d[ix][10] * *(v10 + idz)) * odx;
                    }
                }
            }
        }
    }
}


void d3xm_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(ixmin);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;
    double *restrict dvdx_ix;

    v += offset;
    dvdx += offset;
    odx += ixmax;

    const double *restrict v1 = v - nynz;
    const double *restrict v2 = v1 - nynz;
    const double *restrict v3 = v2 - nynz;
    const double *restrict v4 = v3 - nynz;
    const double *restrict v5 = v4 - nynz;
    const double *restrict v6 = v5 - nynz;
    const double *restrict v7 = v6 - nynz;
    const double *restrict v8 = v7 - nynz;
    const double *restrict v9 = v8 - nynz;
    const double *restrict v10 = v9 - nynz;

    switch(threads){
        case 1:
            for (ix = 0; ix < 5; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = iy * nz;
                    dvdx_ix = dvdx - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = - (a11d[ix][0] * *(v + idz) +
                                             a11d[ix][1] * *(v1 + idz) +
                                             a11d[ix][2] * *(v2 + idz) +
                                             a11d[ix][3] * *(v3 + idz) +
                                             a11d[ix][4] * *(v4 + idz) +
                                             a11d[ix][5] * *(v5 + idz) +
                                             a11d[ix][6] * *(v6 + idz) +
                                             a11d[ix][7] * *(v7 + idz) +
                                             a11d[ix][8] * *(v8 + idz) +
                                             a11d[ix][9] * *(v9 + idz) +
                                             a11d[ix][10] * *(v10 + idz)) * *(odx - ix);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = - (a11d[ix][0] * *(v + idz) +
                                                 a11d[ix][1] * *(v1 + idz) +
                                                 a11d[ix][2] * *(v2 + idz) +
                                                 a11d[ix][3] * *(v3 + idz) +
                                                 a11d[ix][4] * *(v4 + idz) +
                                                 a11d[ix][5] * *(v5 + idz) +
                                                 a11d[ix][6] * *(v6 + idz) +
                                                 a11d[ix][7] * *(v7 + idz) +
                                                 a11d[ix][8] * *(v8 + idz) +
                                                 a11d[ix][9] * *(v9 + idz) +
                                                 a11d[ix][10] * *(v10 + idz)) * *(odx - ix);
                    }
                }
            }
        }
    }
}


void d3ym_s(double *restrict dvdy, const double *restrict v, const double ody,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;

    const double *restrict v1 = v - nz;
    const double *restrict v2 = v1 - nz;
    const double *restrict v3 = v2 - nz;
    const double *restrict v4 = v3 - nz;
    const double *restrict v5 = v4 - nz;
    const double *restrict v6 = v5 - nz;
    const double *restrict v7 = v6 - nz;
    const double *restrict v8 = v7 - nz;
    const double *restrict v9 = v8 - nz;
    const double *restrict v10 = v9 - nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy < 5; iy++){
                    idy = iy * nz;
                    dvdy_ix = dvdy + idx - idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idx + iz;
                        *(dvdy_ix + iz) = - (a11d[iy][0] * *(v + idz) +
                                             a11d[iy][1] * *(v1 + idz) +
                                             a11d[iy][2] * *(v2 + idz) +
                                             a11d[iy][3] * *(v3 + idz) +
                                             a11d[iy][4] * *(v4 + idz) +
                                             a11d[iy][5] * *(v5 + idz) +
                                             a11d[iy][6] * *(v6 + idz) +
                                             a11d[iy][7] * *(v7 + idz) +
                                             a11d[iy][8] * *(v8 + idz) +
                                             a11d[iy][9] * *(v9 + idz) +
                                             a11d[iy][10] * *(v10 + idz)) * ody;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;
                        dvdy_ix = dvdy + idx - idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idx + iz;
                            *(dvdy_ix + iz) = - (a11d[iy][0] * *(v + idz) +
                                                 a11d[iy][1] * *(v1 + idz) +
                                                 a11d[iy][2] * *(v2 + idz) +
                                                 a11d[iy][3] * *(v3 + idz) +
                                                 a11d[iy][4] * *(v4 + idz) +
                                                 a11d[iy][5] * *(v5 + idz) +
                                                 a11d[iy][6] * *(v6 + idz) +
                                                 a11d[iy][7] * *(v7 + idz) +
                                                 a11d[iy][8] * *(v8 + idz) +
                                                 a11d[iy][9] * *(v9 + idz) +
                                                 a11d[iy][10] * *(v10 + idz)) * ody;
                    }
                }
            }
        }
    }
}


void d3ym_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;
    double *restrict dvdy_ix;

    v += offset;
    dvdy += offset;
    ody += iymax;

    const double *restrict v1 = v - nz;
    const double *restrict v2 = v1 - nz;
    const double *restrict v3 = v2 - nz;
    const double *restrict v4 = v3 - nz;
    const double *restrict v5 = v4 - nz;
    const double *restrict v6 = v5 - nz;
    const double *restrict v7 = v6 - nz;
    const double *restrict v8 = v7 - nz;
    const double *restrict v9 = v8 - nz;
    const double *restrict v10 = v9 - nz;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy < 5; iy++){
                    idy = iy * nz;
                    dvdy_ix = dvdy + idx - idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idx + iz;
                        *(dvdy_ix + iz) = - (a11d[iy][0] * *(v + idz) +
                                             a11d[iy][1] * *(v1 + idz) +
                                             a11d[iy][2] * *(v2 + idz) +
                                             a11d[iy][3] * *(v3 + idz) +
                                             a11d[iy][4] * *(v4 + idz) +
                                             a11d[iy][5] * *(v5 + idz) +
                                             a11d[iy][6] * *(v6 + idz) +
                                             a11d[iy][7] * *(v7 + idz) +
                                             a11d[iy][8] * *(v8 + idz) +
                                             a11d[iy][9] * *(v9 + idz) +
                                             a11d[iy][10] * *(v10 + idz)) * *(ody - iy);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdy_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;
                        dvdy_ix = dvdy + idx - idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idx + iz;
                            *(dvdy_ix + iz) = - (a11d[iy][0] * *(v + idz) +
                                                 a11d[iy][1] * *(v1 + idz) +
                                                 a11d[iy][2] * *(v2 + idz) +
                                                 a11d[iy][3] * *(v3 + idz) +
                                                 a11d[iy][4] * *(v4 + idz) +
                                                 a11d[iy][5] * *(v5 + idz) +
                                                 a11d[iy][6] * *(v6 + idz) +
                                                 a11d[iy][7] * *(v7 + idz) +
                                                 a11d[iy][8] * *(v8 + idz) +
                                                 a11d[iy][9] * *(v9 + idz) +
                                                 a11d[iy][10] * *(v10 + idz)) * *(ody - iy);
                    }
                }
            }
        }
    }
}


void d3zm_s(double *restrict dvdz, const double *restrict v, const double odz,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(izmin);
    unsigned int ix, iy, iz, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;
    double *restrict dvdz_ix;

    v += offset;
    dvdz += offset;

    const double *restrict v1 = v - 1;
    const double *restrict v2 = v1 - 1;
    const double *restrict v3 = v2 - 1;
    const double *restrict v4 = v3 - 1;
    const double *restrict v5 = v4 - 1;
    const double *restrict v6 = v5 - 1;
    const double *restrict v7 = v6 - 1;
    const double *restrict v8 = v7 - 1;
    const double *restrict v9 = v8 - 1;
    const double *restrict v10 = v9 - 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = idx + iy * nz;
                    dvdz_ix = dvdz + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dvdz_ix - iz) = - (a11d[iz][0] * *(v + idy) +
                                             a11d[iz][1] * *(v1 + idy) +
                                             a11d[iz][2] * *(v2 + idy) +
                                             a11d[iz][3] * *(v3 + idy) +
                                             a11d[iz][4] * *(v4 + idy) +
                                             a11d[iz][5] * *(v5 + idy) +
                                             a11d[iz][6] * *(v6 + idy) +
                                             a11d[iz][7] * *(v7 + idy) +
                                             a11d[iz][8] * *(v8 + idy) +
                                             a11d[iz][9] * *(v9 + idy) +
                                             a11d[iz][10] * *(v10 + idy)) * odz;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dvdz_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dvdz_ix = dvdz + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dvdz_ix - iz) = - (a11d[iz][0] * *(v + idy) +
                                                 a11d[iz][1] * *(v1 + idy) +
                                                 a11d[iz][2] * *(v2 + idy) +
                                                 a11d[iz][3] * *(v3 + idy) +
                                                 a11d[iz][4] * *(v4 + idy) +
                                                 a11d[iz][5] * *(v5 + idy) +
                                                 a11d[iz][6] * *(v6 + idy) +
                                                 a11d[iz][7] * *(v7 + idy) +
                                                 a11d[iz][8] * *(v8 + idy) +
                                                 a11d[iz][9] * *(v9 + idy) +
                                                 a11d[iz][10] * *(v10 + idy)) * odz;
                    }
                }
            }
        }
    }
}


void d3zm_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
            const unsigned int ny, const unsigned int nz,
            const unsigned int ixmin, const unsigned int ixmax,
            const unsigned int iymin, const unsigned int iymax,
            const unsigned int izmin, const unsigned int izmax,
            const unsigned int threads) {

    (void)(izmin);
    unsigned int ix, iy, iz, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;
    double *restrict dvdz_ix;

    v += offset;
    dvdz += offset;
    odz += izmax;

    const double *restrict v1 = v - 1;
    const double *restrict v2 = v1 - 1;
    const double *restrict v3 = v2 - 1;
    const double *restrict v4 = v3 - 1;
    const double *restrict v5 = v4 - 1;
    const double *restrict v6 = v5 - 1;
    const double *restrict v7 = v6 - 1;
    const double *restrict v8 = v7 - 1;
    const double *restrict v9 = v8 - 1;
    const double *restrict v10 = v9 - 1;

    switch(threads){
        case 1:
            for (ix = 0; ix <= mx; ix++){
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++){
                    idy = idx + iy * nz;
                    dvdz_ix = dvdz + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dvdz_ix - iz) = - (a11d[iz][0] * *(v + idy) +
                                             a11d[iz][1] * *(v1 + idy) +
                                             a11d[iz][2] * *(v2 + idy) +
                                             a11d[iz][3] * *(v3 + idy) +
                                             a11d[iz][4] * *(v4 + idy) +
                                             a11d[iz][5] * *(v5 + idy) +
                                             a11d[iz][6] * *(v6 + idy) +
                                             a11d[iz][7] * *(v7 + idy) +
                                             a11d[iz][8] * *(v8 + idy) +
                                             a11d[iz][9] * *(v9 + idy) +
                                             a11d[iz][10] * *(v10 + idy)) * *(odz - iz);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dvdz_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dvdz_ix = dvdz + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dvdz_ix - iz) = - (a11d[iz][0] * *(v + idy) +
                                                 a11d[iz][1] * *(v1 + idy) +
                                                 a11d[iz][2] * *(v2 + idy) +
                                                 a11d[iz][3] * *(v3 + idy) +
                                                 a11d[iz][4] * *(v4 + idy) +
                                                 a11d[iz][5] * *(v5 + idy) +
                                                 a11d[iz][6] * *(v6 + idy) +
                                                 a11d[iz][7] * *(v7 + idy) +
                                                 a11d[iz][8] * *(v8 + idy) +
                                                 a11d[iz][9] * *(v9 + idy) +
                                                 a11d[iz][10] * *(v10 + idy)) * *(odz - iz);
                    }
                }
            }
        }
    }
}


/*----------------------------*/
/* Global 3d differentiation */
/*--------------------------*/

void d3x_s(double *restrict dvdx, const double *restrict v, const double odx,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3xc_s(dvdx, v, odx, ny, nz, 5, nx - 6, 0, ny - 1, 0, nz - 1, threads);
    d3xp_s(dvdx, v, odx, ny, nz, 0, 4, 0, ny - 1, 0, nz - 1, threads);
    d3xm_s(dvdx, v, odx, ny, nz, nx - 5, nx - 1, 0, ny - 1, 0, nz - 1, threads);
}


void d3x_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3yc_v(dvdx, v, odx, ny, nz, 5, nx - 6, 0, ny - 1, 0, nz - 1, threads);
    d3yp_v(dvdx, v, odx, ny, nz, 0, 4, 0, ny - 1, 0, nz - 1, threads);
    d3ym_v(dvdx, v, odx, ny, nz, nx - 5, nx - 1, 0, ny - 1, 0, nz - 1, threads);
}


void d3y_s(double *restrict dvdy, const double *restrict v, const double ody,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3yc_s(dvdy, v, ody, ny, nz, 0, nx - 1, 5, ny - 6, 0, nz - 1, threads);
    d3yp_s(dvdy, v, ody, ny, nz, 0, nx - 1, 0, 4, 0, nz - 1, threads);
    d3ym_s(dvdy, v, ody, ny, nz, 0, nx - 1, ny - 5, ny - 1, 0, nz - 1, threads);
}


void d3y_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3yc_v(dvdy, v, ody, ny, nz, 0, nx - 1, 5, ny - 6, 0, nz - 1, threads);
    d3yp_v(dvdy, v, ody, ny, nz, 0, nx - 1, 0, 4, 0, nz - 1, threads);
    d3ym_v(dvdy, v, ody, ny, nz, 0, nx - 1, ny - 5, ny - 1, 0, nz - 1, threads);
}


void d3z_s(double *restrict dvdz, const double *restrict v, const double odz,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3zc_s(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, 5, nz - 6, threads);
    d3zp_s(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, 0, 4, threads);
    d3zm_s(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, nz - 5, nz - 1, threads);
}


void d3z_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
           const unsigned int nx, const unsigned int ny, const unsigned int nz,
           const unsigned int threads) {

    d3zc_v(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, 5, nz - 6, threads);
    d3zp_v(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, 0, 4, threads);
    d3zm_v(dvdz, v, odz, ny, nz, 0, nx - 1, 0, ny - 1, nz - 5, nz - 1, threads);
}