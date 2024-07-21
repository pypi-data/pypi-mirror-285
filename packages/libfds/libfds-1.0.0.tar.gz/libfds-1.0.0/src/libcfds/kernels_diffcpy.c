#include <stdio.h>
#include <omp.h>
#include <time.h>
#include "kernels_diffcpy.h"
#include "coefficients.h"

/*-------------------------------*/
/* Subdomain 2d differentiation */
/*-----------------------------*/


void d2cpy_xc_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vc += offset;
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
                    *(dvdx + idy) = *(vc + idy) + (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                                   a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                                   a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                                   a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                                   a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odn;
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
                        *(dvdx + idy) = *(vc + idy) + (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                                       a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                                       a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                                       a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                                       a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odn;
                }
            }
        }
    }
}


void d2cpy_xc_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vc += offset;
    dvdx += offset;
    odn += ixmin;

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
                    *(dvdx + idy) = *(vc + idy) + (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                                   a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                                   a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                                   a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                                   a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odn + ix);
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
                        *(dvdx + idy) = *(vc + idy) + (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                                       a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                                       a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                                       a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                                       a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odn + ix);
                }
            }
        }
    }
}


void d2cpy_xP_s(double *restrict dv, const double *restrict v, const double *restrict vc,
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
                    *(dv + idy) = *(vc + idy) + (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
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
                        *(dv + idy) = *(vc + idy) + (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                                     a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                                     a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                                     a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                                     a11c[5] * (*(v5p + iy) - *(v5m + iy))) * odn;
                }
            }
        }
    }
}


void d2cpy_xP_v(double *restrict dv, const double *restrict v, const double *restrict vc,
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
                    *(dv + idy) = *(vc + idy) + (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
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
                        *(dv + idy) = *(vc + idy) + (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                                     a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                                     a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                                     a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                                     a11c[5] * (*(v5p + iy) - *(v5m + iy))) * *(odn + ix);
                }
            }
        }
    }
}


void d2cpy_xp_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdx_ix;
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
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
                vc_ix = vc + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = *(vc_ix + iy) + (a11d[ix][0] * *(v + iy) +
                                                       a11d[ix][1] * *(v1 + iy) +
                                                       a11d[ix][2] * *(v2 + iy) +
                                                       a11d[ix][3] * *(v3 + iy) +
                                                       a11d[ix][4] * *(v4 + iy) +
                                                       a11d[ix][5] * *(v5 + iy) +
                                                       a11d[ix][6] * *(v6 + iy) +
                                                       a11d[ix][7] * *(v7 + iy) +
                                                       a11d[ix][8] * *(v8 + iy) +
                                                       a11d[ix][9] * *(v9 + iy) +
                                                       a11d[ix][10] * *(v10 + iy)) * odn;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx + ix * ny;
                    vc_ix = vc + ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = *(vc_ix + iy) + (a11d[ix][0] * *(v + iy) +
                                                           a11d[ix][1] * *(v1 + iy) +
                                                           a11d[ix][2] * *(v2 + iy) +
                                                           a11d[ix][3] * *(v3 + iy) +
                                                           a11d[ix][4] * *(v4 + iy) +
                                                           a11d[ix][5] * *(v5 + iy) +
                                                           a11d[ix][6] * *(v6 + iy) +
                                                           a11d[ix][7] * *(v7 + iy) +
                                                           a11d[ix][8] * *(v8 + iy) +
                                                           a11d[ix][9] * *(v9 + iy) +
                                                           a11d[ix][10] * *(v10 + iy)) * odn;
                }
            }
        }
    }
}


void d2cpy_xp_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dvdx_ix;
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
    dvdx += offset;
    odn += ixmin;

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
                vc_ix = vc + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = *(vc_ix + iy) + (a11d[ix][0] * *(v + iy) +
                                                       a11d[ix][1] * *(v1 + iy) +
                                                       a11d[ix][2] * *(v2 + iy) +
                                                       a11d[ix][3] * *(v3 + iy) +
                                                       a11d[ix][4] * *(v4 + iy) +
                                                       a11d[ix][5] * *(v5 + iy) +
                                                       a11d[ix][6] * *(v6 + iy) +
                                                       a11d[ix][7] * *(v7 + iy) +
                                                       a11d[ix][8] * *(v8 + iy) +
                                                       a11d[ix][9] * *(v9 + iy) +
                                                       a11d[ix][10] * *(v10 + iy)) * *(odn + ix);
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx + ix * ny;
                    vc_ix = vc + ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = *(vc_ix + iy) + (a11d[ix][0] * *(v + iy) +
                                                           a11d[ix][1] * *(v1 + iy) +
                                                           a11d[ix][2] * *(v2 + iy) +
                                                           a11d[ix][3] * *(v3 + iy) +
                                                           a11d[ix][4] * *(v4 + iy) +
                                                           a11d[ix][5] * *(v5 + iy) +
                                                           a11d[ix][6] * *(v6 + iy) +
                                                           a11d[ix][7] * *(v7 + iy) +
                                                           a11d[ix][8] * *(v8 + iy) +
                                                           a11d[ix][9] * *(v9 + iy) +
                                                           a11d[ix][10] * *(v10 + iy)) * *(odn + ix);
                }
            }
        }
    }
}


void d2cpy_xm_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dvdx_ix;
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
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
                vc_ix = vc - ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = *(vc_ix + iy) - (a11d[ix][0] * *(v + iy) +
                                                       a11d[ix][1] * *(v1 + iy) +
                                                       a11d[ix][2] * *(v2 + iy) +
                                                       a11d[ix][3] * *(v3 + iy) +
                                                       a11d[ix][4] * *(v4 + iy) +
                                                       a11d[ix][5] * *(v5 + iy) +
                                                       a11d[ix][6] * *(v6 + iy) +
                                                       a11d[ix][7] * *(v7 + iy) +
                                                       a11d[ix][8] * *(v8 + iy) +
                                                       a11d[ix][9] * *(v9 + iy) +
                                                       a11d[ix][10] * *(v10 + iy)) * odn;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx - ix * ny;
                    vc_ix = vc - ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = *(vc_ix + iy) - (a11d[ix][0] * *(v + iy) +
                                                           a11d[ix][1] * *(v1 + iy) +
                                                           a11d[ix][2] * *(v2 + iy) +
                                                           a11d[ix][3] * *(v3 + iy) +
                                                           a11d[ix][4] * *(v4 + iy) +
                                                           a11d[ix][5] * *(v5 + iy) +
                                                           a11d[ix][6] * *(v6 + iy) +
                                                           a11d[ix][7] * *(v7 + iy) +
                                                           a11d[ix][8] * *(v8 + iy) +
                                                           a11d[ix][9] * *(v9 + iy) +
                                                           a11d[ix][10] * *(v10 + iy)) * odn;
                }
            }
        }
    }
}


void d2cpy_xm_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dvdx_ix;
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
    dvdx += offset;
    odn += ixmax;

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
                vc_ix = vc - ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dvdx_ix + iy) = *(vc_ix + iy) - (a11d[ix][0] * *(v + iy) +
                                                       a11d[ix][1] * *(v1 + iy) +
                                                       a11d[ix][2] * *(v2 + iy) +
                                                       a11d[ix][3] * *(v3 + iy) +
                                                       a11d[ix][4] * *(v4 + iy) +
                                                       a11d[ix][5] * *(v5 + iy) +
                                                       a11d[ix][6] * *(v6 + iy) +
                                                       a11d[ix][7] * *(v7 + iy) +
                                                       a11d[ix][8] * *(v8 + iy) +
                                                       a11d[ix][9] * *(v9 + iy) +
                                                       a11d[ix][10] * *(v10 + iy)) * *(odn - ix);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dvdx_ix = dvdx - ix * ny;
                    vc_ix = vc - ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dvdx_ix + iy) = *(vc_ix + iy) - (a11d[ix][0] * *(v + iy) +
                                                           a11d[ix][1] * *(v1 + iy) +
                                                           a11d[ix][2] * *(v2 + iy) +
                                                           a11d[ix][3] * *(v3 + iy) +
                                                           a11d[ix][4] * *(v4 + iy) +
                                                           a11d[ix][5] * *(v5 + iy) +
                                                           a11d[ix][6] * *(v6 + iy) +
                                                           a11d[ix][7] * *(v7 + iy) +
                                                           a11d[ix][8] * *(v8 + iy) +
                                                           a11d[ix][9] * *(v9 + iy) +
                                                           a11d[ix][10] * *(v10 + iy)) * *(odn - ix);
                }
            }
        }
    }
}


/*-------------------------------*/
/* Subdomain 3d differentiation */
/*-----------------------------*/


void d3cpy_xc_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny, const unsigned int nz,
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
    vc += offset;
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
                        *(dvdx + idz) = *(vc + idz) + (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                                       a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                                       a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                                       a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                                       a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odn;
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
                        *(dvdx + idz) = *(vc + idz) + (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                                       a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                                       a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                                       a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                                       a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * odn;
                    }
                }
            }
        }
    }
}


void d3cpy_xc_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int ny, const unsigned int nz,
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
    vc += offset;
    dvdx += offset;
    odn += ixmin;

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
                        *(dvdx + idz) = *(vc + idz) + (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                                       a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                                       a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                                       a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                                       a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + ix);
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
                        *(dvdx + idz) = *(vc + idz) + (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                                       a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                                       a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                                       a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                                       a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + ix);
                    }
                }
            }
        }
    }
}


void d3cpy_xP_s(double *restrict dv, const double *restrict v, const double *restrict vc,
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
                        *(dv + idz) = *(vc + idz) + (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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
                            *(dv + idz) = *(vc + idz) + (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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


void d3cpy_xP_v(double *restrict dv, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int *restrict P,
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
                        *(dv + idz) = *(vc + idz) + (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                                     a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                                     a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                                     a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                                     a11c[5] * (*(v5p + iz) - *(v5m + iz))) * *(odn + ix);
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
                            *(dv + idz) = *(vc + idz) + (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
                                                         a11c[2] * (*(v2p + iz) - *(v2m + iz)) +
                                                         a11c[3] * (*(v3p + iz) - *(v3m + iz)) +
                                                         a11c[4] * (*(v4p + iz) - *(v4m + iz)) +
                                                         a11c[5] * (*(v5p + iz) - *(v5m + iz))) * *(odn + ix);
                    }
                }
            }
        }
    }
}



void d3cpy_xp_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny, const unsigned int nz,
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
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
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
                    vc_ix = vc + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = *(vc_ix + iz) + (a11d[ix][0] * *(v + idz) +
                                                           a11d[ix][1] * *(v1 + idz) +
                                                           a11d[ix][2] * *(v2 + idz) +
                                                           a11d[ix][3] * *(v3 + idz) +
                                                           a11d[ix][4] * *(v4 + idz) +
                                                           a11d[ix][5] * *(v5 + idz) +
                                                           a11d[ix][6] * *(v6 + idz) +
                                                           a11d[ix][7] * *(v7 + idz) +
                                                           a11d[ix][8] * *(v8 + idz) +
                                                           a11d[ix][9] * *(v9 + idz) +
                                                           a11d[ix][10] * *(v10 + idz)) * odn;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx + idx + idy;
                        vc_ix = vc + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = *(vc_ix + iz) + (a11d[ix][0] * *(v + idz) +
                                                               a11d[ix][1] * *(v1 + idz) +
                                                               a11d[ix][2] * *(v2 + idz) +
                                                               a11d[ix][3] * *(v3 + idz) +
                                                               a11d[ix][4] * *(v4 + idz) +
                                                               a11d[ix][5] * *(v5 + idz) +
                                                               a11d[ix][6] * *(v6 + idz) +
                                                               a11d[ix][7] * *(v7 + idz) +
                                                               a11d[ix][8] * *(v8 + idz) +
                                                               a11d[ix][9] * *(v9 + idz) +
                                                               a11d[ix][10] * *(v10 + idz)) * odn;
                    }
                }
            }
        }
    }
}


void d3cpy_xp_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int ny, const unsigned int nz,
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
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
    dvdx += offset;
    odn += ixmin;

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
                    vc_ix = vc + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = *(vc_ix + iz) + (a11d[ix][0] * *(v + idz) +
                                                           a11d[ix][1] * *(v1 + idz) +
                                                           a11d[ix][2] * *(v2 + idz) +
                                                           a11d[ix][3] * *(v3 + idz) +
                                                           a11d[ix][4] * *(v4 + idz) +
                                                           a11d[ix][5] * *(v5 + idz) +
                                                           a11d[ix][6] * *(v6 + idz) +
                                                           a11d[ix][7] * *(v7 + idz) +
                                                           a11d[ix][8] * *(v8 + idz) +
                                                           a11d[ix][9] * *(v9 + idz) +
                                                           a11d[ix][10] * *(v10 + idz)) * *(odn + ix);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx + idx + idy;
                        vc_ix = vc + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = *(vc_ix + iz) + (a11d[ix][0] * *(v + idz) +
                                                               a11d[ix][1] * *(v1 + idz) +
                                                               a11d[ix][2] * *(v2 + idz) +
                                                               a11d[ix][3] * *(v3 + idz) +
                                                               a11d[ix][4] * *(v4 + idz) +
                                                               a11d[ix][5] * *(v5 + idz) +
                                                               a11d[ix][6] * *(v6 + idz) +
                                                               a11d[ix][7] * *(v7 + idz) +
                                                               a11d[ix][8] * *(v8 + idz) +
                                                               a11d[ix][9] * *(v9 + idz) +
                                                               a11d[ix][10] * *(v10 + idz)) * *(odn + ix);
                    }
                }
            }
        }
    }
}


void d3cpy_xm_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double odn, const unsigned int ny, const unsigned int nz,
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
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
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
                    vc_ix = vc - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = *(vc_ix + iz) - (a11d[ix][0] * *(v + idz) +
                                                           a11d[ix][1] * *(v1 + idz) +
                                                           a11d[ix][2] * *(v2 + idz) +
                                                           a11d[ix][3] * *(v3 + idz) +
                                                           a11d[ix][4] * *(v4 + idz) +
                                                           a11d[ix][5] * *(v5 + idz) +
                                                           a11d[ix][6] * *(v6 + idz) +
                                                           a11d[ix][7] * *(v7 + idz) +
                                                           a11d[ix][8] * *(v8 + idz) +
                                                           a11d[ix][9] * *(v9 + idz) +
                                                           a11d[ix][10] * *(v10 + idz)) * odn;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx - idx + idy;
                        vc_ix = vc - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = *(vc_ix + iz) - (a11d[ix][0] * *(v + idz) +
                                                               a11d[ix][1] * *(v1 + idz) +
                                                               a11d[ix][2] * *(v2 + idz) +
                                                               a11d[ix][3] * *(v3 + idz) +
                                                               a11d[ix][4] * *(v4 + idz) +
                                                               a11d[ix][5] * *(v5 + idz) +
                                                               a11d[ix][6] * *(v6 + idz) +
                                                               a11d[ix][7] * *(v7 + idz) +
                                                               a11d[ix][8] * *(v8 + idz) +
                                                               a11d[ix][9] * *(v9 + idz) +
                                                               a11d[ix][10] * *(v10 + idz)) * odn;
                    }
                }
            }
        }
    }
}


void d3cpy_xm_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                const double *restrict odn, const unsigned int ny, const unsigned int nz,
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
    const double *restrict vc_ix;

    v += offset;
    vc += offset;
    dvdx += offset;
    odn += ixmax;

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
                    vc_ix = vc - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dvdx_ix + iz) = *(vc_ix + iz) - (a11d[ix][0] * *(v + idz) +
                                                           a11d[ix][1] * *(v1 + idz) +
                                                           a11d[ix][2] * *(v2 + idz) +
                                                           a11d[ix][3] * *(v3 + idz) +
                                                           a11d[ix][4] * *(v4 + idz) +
                                                           a11d[ix][5] * *(v5 + idz) +
                                                           a11d[ix][6] * *(v6 + idz) +
                                                           a11d[ix][7] * *(v7 + idz) +
                                                           a11d[ix][8] * *(v8 + idz) +
                                                           a11d[ix][9] * *(v9 + idz) +
                                                           a11d[ix][10] * *(v10 + idz)) * *(odn - ix);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dvdx_ix, vc_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dvdx_ix = dvdx - idx + idy;
                        vc_ix = vc - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dvdx_ix + iz) = *(vc_ix + iz) - (a11d[ix][0] * *(v + idz) +
                                                               a11d[ix][1] * *(v1 + idz) +
                                                               a11d[ix][2] * *(v2 + idz) +
                                                               a11d[ix][3] * *(v3 + idz) +
                                                               a11d[ix][4] * *(v4 + idz) +
                                                               a11d[ix][5] * *(v5 + idz) +
                                                               a11d[ix][6] * *(v6 + idz) +
                                                               a11d[ix][7] * *(v7 + idz) +
                                                               a11d[ix][8] * *(v8 + idz) +
                                                               a11d[ix][9] * *(v9 + idz) +
                                                               a11d[ix][10] * *(v10 + idz)) * *(odn - ix);
                    }
                }
            }
        }
    }
}