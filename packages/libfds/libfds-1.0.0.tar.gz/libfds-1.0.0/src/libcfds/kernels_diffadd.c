#include <stdio.h>
#include <omp.h>
#include <time.h>
#include "kernels_diffadd.h"
#include "coefficients.h"


/*---------------------------------------------*/
/* Subdomain 2d differentiation with addition */
/*-------------------------------------------*/


void d2add_xc_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dv += offset;

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
                    *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
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
                        *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                        a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                        a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                        a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                        a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odn;
                }
            }
        }
    }
}


void d2add_xc_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dv += offset;
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
                    *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
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
                        *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                        a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                        a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                        a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                        a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odn + ix);
                }
            }
        }
    }
}


void d2add_yc_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dv += offset;

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
                    *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
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
                        *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                        a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                        a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                        a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                        a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * odn;
                }
            }
        }
    }
}


void d2add_yc_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    dv += offset;
    odn += iymin;

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
                    *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                    a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                    a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                    a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                    a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odn + iy);
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
                        *(dv + idy) += (a11c[1] * (*(v_1p + idy) - *(v_1m + idy)) +
                                        a11c[2] * (*(v_2p + idy) - *(v_2m + idy)) +
                                        a11c[3] * (*(v_3p + idy) - *(v_3m + idy)) +
                                        a11c[4] * (*(v_4p + idy) - *(v_4m + idy)) +
                                        a11c[5] * (*(v_5p + idy) - *(v_5m + idy))) * *(odn + iy);
                }
            }
        }
    }
}


void d2add_xP_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int *restrict P, const unsigned int ny,
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
                    *(dv + idy) += (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                    a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                    a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                    a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                    a11c[5] * (*(v5p + iy) - *(v5m + iy))) * odn;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, \
                                v1m, v2m, v3m, v4m, v5m, v1p, v2p, v3p, v4p, v5p)
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
                        *(dv + idy) += (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                        a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                        a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                        a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                        a11c[5] * (*(v5p + iy) - *(v5m + iy))) * odn;
                }
            }
        }
    }
}


void d2add_xP_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int *restrict P, const unsigned int ny,
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
                    *(dv + idy) += (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
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
                        *(dv + idy) += (a11c[1] * (*(v1p + iy) - *(v1m + iy)) +
                                        a11c[2] * (*(v2p + iy) - *(v2m + iy)) +
                                        a11c[3] * (*(v3p + iy) - *(v3m + iy)) +
                                        a11c[4] * (*(v4p + iy) - *(v4m + iy)) +
                                        a11c[5] * (*(v5p + iy) - *(v5m + iy))) * *(odn + ix);
                }
            }
        }
    }
}


void d2add_yP_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int *restrict P, const unsigned int ny,
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
                    *(dv + idy) += (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
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
                        *(dv + idy) += (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                        a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                        a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                        a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                        a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * odn;
                }
            }
        }
    }
}


void d2add_yP_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int *restrict P, const unsigned int ny,
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
                    *(dv + idy) += (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
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
                        *(dv + idy) += (a11c[1] * (*(vix + *(Py + iy + 1)) - *(vix + *(Py + iy - 1))) +
                                        a11c[2] * (*(vix + *(Py + iy + 2)) - *(vix + *(Py + iy - 2))) +
                                        a11c[3] * (*(vix + *(Py + iy + 3)) - *(vix + *(Py + iy - 3))) +
                                        a11c[4] * (*(vix + *(Py + iy + 4)) - *(vix + *(Py + iy - 4))) +
                                        a11c[5] * (*(vix + *(Py + iy + 5)) - *(vix + *(Py + iy - 5)))) * *(odn + iy);
                }
            }
        }
    }
}


void d2add_xp_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmax);
    unsigned int ix, iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                dv_ix = dv + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dv_ix + iy) += (a11d[ix][0] * *(v + iy) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dv_ix = dv +  ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dv_ix + iy) += (a11d[ix][0] * *(v + iy) +
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


void d2add_xp_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;
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
                dv_ix = dv + ix * ny;

                for (iy = 0; iy <= my; iy++){
                    *(dv_ix + iy) += (a11d[ix][0] * *(v + iy) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dv_ix = dv + ix * ny;

                    for (iy = 0; iy <= my; iy++){
                        *(dv_ix + iy) += (a11d[ix][0] * *(v + iy) +
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


void d2add_yp_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                dv_ix = dv + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dv_ix + iy) += (a11d[iy][0] * *(v + idx) +
                                      a11d[iy][1] * *(v1 + idx) +
                                      a11d[iy][2] * *(v2 + idx) +
                                      a11d[iy][3] * *(v3 + idx) +
                                      a11d[iy][4] * *(v4 + idx) +
                                      a11d[iy][5] * *(v5 + idx) +
                                      a11d[iy][6] * *(v6 + idx) +
                                      a11d[iy][7] * *(v7 + idx) +
                                      a11d[iy][8] * *(v8 + idx) +
                                      a11d[iy][9] * *(v9 + idx) +
                                      a11d[iy][10] * *(v10 + idx)) * odn;
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dv_ix = dv + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dv_ix + iy) += (a11d[iy][0] * *(v + idx) +
                                          a11d[iy][1] * *(v1 + idx) +
                                          a11d[iy][2] * *(v2 + idx) +
                                          a11d[iy][3] * *(v3 + idx) +
                                          a11d[iy][4] * *(v4 + idx) +
                                          a11d[iy][5] * *(v5 + idx) +
                                          a11d[iy][6] * *(v6 + idx) +
                                          a11d[iy][7] * *(v7 + idx) +
                                          a11d[iy][8] * *(v8 + idx) +
                                          a11d[iy][9] * *(v9 + idx) +
                                          a11d[iy][10] * *(v10 + idx)) * odn;
                }
            }
        }
    }
}


void d2add_yp_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;
    odn += iymin;

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
                dv_ix = dv + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dv_ix + iy) += (a11d[iy][0] * *(v + idx) +
                                      a11d[iy][1] * *(v1 + idx) +
                                      a11d[iy][2] * *(v2 + idx) +
                                      a11d[iy][3] * *(v3 + idx) +
                                      a11d[iy][4] * *(v4 + idx) +
                                      a11d[iy][5] * *(v5 + idx) +
                                      a11d[iy][6] * *(v6 + idx) +
                                      a11d[iy][7] * *(v7 + idx) +
                                      a11d[iy][8] * *(v8 + idx) +
                                      a11d[iy][9] * *(v9 + idx) +
                                      a11d[iy][10] * *(v10 + idx)) * *(odn + iy);
                }
            }
            break;

        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dv_ix = dv + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dv_ix + iy) += (a11d[iy][0] * *(v + idx) +
                                          a11d[iy][1] * *(v1 + idx) +
                                          a11d[iy][2] * *(v2 + idx) +
                                          a11d[iy][3] * *(v3 + idx) +
                                          a11d[iy][4] * *(v4 + idx) +
                                          a11d[iy][5] * *(v5 + idx) +
                                          a11d[iy][6] * *(v6 + idx) +
                                          a11d[iy][7] * *(v7 + idx) +
                                          a11d[iy][8] * *(v8 + idx) +
                                          a11d[iy][9] * *(v9 + idx) +
                                          a11d[iy][10] * *(v10 + idx)) * *(odn + iy);
                }
            }
        }
    }
}


void d2add_xm_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmin);
    unsigned int ix, iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                dv_ix = dv - ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    *(dv_ix + iy) -= (a11d[ix][0] * *(v + iy) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dv_ix = dv - ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        *(dv_ix + iy) -= (a11d[ix][0] * *(v + iy) +
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


void d2add_xm_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, ix;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;
    double *restrict dv_ix;

    v += offset;
    dv += offset;
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
                dv_ix = dv - ix * ny;

                for (iy = 0; iy <= my; iy++) {
                    *(dv_ix + iy) -= (a11d[ix][0] * *(v + iy) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    dv_ix = dv - ix * ny;

                    for (iy = 0; iy <= my; iy++) {
                        *(dv_ix + iy) -= (a11d[ix][0] * *(v + iy) +
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


void d2add_ym_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                dv_ix = dv + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dv_ix - iy) -= (a11d[iy][0] * *(v + idx) +
                                      a11d[iy][1] * *(v1 + idx) +
                                      a11d[iy][2] * *(v2 + idx) +
                                      a11d[iy][3] * *(v3 + idx) +
                                      a11d[iy][4] * *(v4 + idx) +
                                      a11d[iy][5] * *(v5 + idx) +
                                      a11d[iy][6] * *(v6 + idx) +
                                      a11d[iy][7] * *(v7 + idx) +
                                      a11d[iy][8] * *(v8 + idx) +
                                      a11d[iy][9] * *(v9 + idx) +
                                      a11d[iy][10] * *(v10 + idx)) * odn;
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dv_ix = dv + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dv_ix - iy) -= (a11d[iy][0] * *(v + idx) +
                                          a11d[iy][1] * *(v1 + idx) +
                                          a11d[iy][2] * *(v2 + idx) +
                                          a11d[iy][3] * *(v3 + idx) +
                                          a11d[iy][4] * *(v4 + idx) +
                                          a11d[iy][5] * *(v5 + idx) +
                                          a11d[iy][6] * *(v6 + idx) +
                                          a11d[iy][7] * *(v7 + idx) +
                                          a11d[iy][8] * *(v8 + idx) +
                                          a11d[iy][9] * *(v9 + idx) +
                                          a11d[iy][10] * *(v10 + idx)) * odn;
                }
            }
        }
    }
}


void d2add_ym_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax,
                const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iy, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;
    double *restrict dv_ix;

    v += offset;
    dv += offset;
    odn += iymax;

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
                dv_ix = dv + idx;

                for (iy = 0; iy < 5; iy++) {
                    *(dv_ix - iy) -= (a11d[iy][0] * *(v + idx) +
                                      a11d[iy][1] * *(v1 + idx) +
                                      a11d[iy][2] * *(v2 + idx) +
                                      a11d[iy][3] * *(v3 + idx) +
                                      a11d[iy][4] * *(v4 + idx) +
                                      a11d[iy][5] * *(v5 + idx) +
                                      a11d[iy][6] * *(v6 + idx) +
                                      a11d[iy][7] * *(v7 + idx) +
                                      a11d[iy][8] * *(v8 + idx) +
                                      a11d[iy][9] * *(v9 + idx) +
                                      a11d[iy][10] * *(v10 + idx)) * *(odn - iy);
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * ny;
                    dv_ix = dv + idx;

                    for (iy = 0; iy < 5; iy++) {
                        *(dv_ix - iy) -= (a11d[iy][0] * *(v + idx) +
                                          a11d[iy][1] * *(v1 + idx) +
                                          a11d[iy][2] * *(v2 + idx) +
                                          a11d[iy][3] * *(v3 + idx) +
                                          a11d[iy][4] * *(v4 + idx) +
                                          a11d[iy][5] * *(v5 + idx) +
                                          a11d[iy][6] * *(v6 + idx) +
                                          a11d[iy][7] * *(v7 + idx) +
                                          a11d[iy][8] * *(v8 + idx) +
                                          a11d[iy][9] * *(v9 + idx) +
                                          a11d[iy][10] * *(v10 + idx)) * *(odn - iy);
                }
            }
        }
    }
}


/*---------------------------------------------*/
/* Subdomain 3d differentiation with addition */
/*-------------------------------------------*/


void d3add_xc_s(double *restrict dv, const double *restrict v, const double odn,
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
    dv += offset;

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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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


void d3add_xc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    dv += offset;
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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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


void d3add_yc_s(double *restrict dv, const double *restrict v, const double odn,
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
    dv += offset;

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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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
                for (ix = 0; ix <= mx; ix++) {
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++) {
                        idy = idx + iy * nz;

                        for (iz = 0; iz <= mz; iz++) {
                            idz = idy + iz;
                            *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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


void d3add_yc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    dv += offset;
    odn += iymin;

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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                          a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                          a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                          a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                          a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + iy);
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
                            *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                              a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                              a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                              a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                              a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + iy);
                    }
                }
            }
        }
    }
}


void d3add_zc_s(double *restrict dv, const double *restrict v, const double odn,
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
    dv += offset;

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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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
            for (ix = 0; ix <= mx; ix++) {
                idx = ix * nynz;

                for (iy = 0; iy <= my; iy++) {
                    idy = idx + iy * nz;

                    for (iz = 0; iz <= mz; iz++) {
                        idz = idy + iz;
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
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


void d3add_zc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    dv += offset;
    odn += izmin;

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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                        a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                        a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                        a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                        a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + iz);
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
                        *(dv + idz) += (a11c[1] * (*(v_1p + idz) - *(v_1m + idz)) +
                                        a11c[2] * (*(v_2p + idz) - *(v_2m + idz)) +
                                        a11c[3] * (*(v_3p + idz) - *(v_3m + idz)) +
                                        a11c[4] * (*(v_4p + idz) - *(v_4m + idz)) +
                                        a11c[5] * (*(v_5p + idz) - *(v_5m + idz))) * *(odn + iz);
                    }
                }
            }
        }
    }
}


void d3add_xP_s(double *restrict dv, const double *restrict v,
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
                        *(dv + idz) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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
                            *(dv + idz) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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


void d3add_xP_v(double *restrict dv, const double *restrict v,
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
                        *(dv + idz) += (a11c[1] * (*(v1p + idn) - *(v1m + idn)) +
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
                            *(dv + idz) += (a11c[1] * (*(v1p + idn) - *(v1m + idn)) +
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


void d3add_yP_s(double *restrict dv, const double *restrict v,
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
                        *(dv + idy) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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
                            *(dv + idy) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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


void d3add_yP_v(double *restrict dv, const double *restrict v,
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
                        *(dv + idy) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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
                            *(dv + idy) += (a11c[1] * (*(v1p + iz) - *(v1m + iz)) +
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


void d3add_zP_s(double *restrict dv, const double *restrict v,
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
                        *(dv + idy) += (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(P + iz - 1))) +
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
                            *(dv + idy) += (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(P + iz - 1))) +
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


void d3add_zP_v(double *restrict dv, const double *restrict v,
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
                        *(dv + idy) += (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(Pz + iz - 1))) +
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
                            *(dv + idy) += (a11c[1] * (*(v + idy + *(Pz + iz + 1)) - *(v + idy + *(Pz + iz - 1))) +
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


void d3add_xp_s(double *restrict dv, const double *restrict v, const double odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                    dv_ix = dv + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dv_ix + iz) += (a11d[ix][0] * *(v + idz) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dv_ix = dv + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dv_ix + iz) += (a11d[ix][0] * *(v + idz) +
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


void d3add_xp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;
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
                    dv_ix = dv + idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dv_ix + iz) += (a11d[ix][0] * *(v + idz) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dv_ix = dv + idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dv_ix + iz) += (a11d[ix][0] * *(v + idz) +
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


void d3add_yp_s(double *restrict dv, const double *restrict v, const double odn,
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
    dv += offset;

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
                        *(dv + idz) += (a11d[iy][0] * *(v + idv) +
                                          a11d[iy][1] * *(v1 + idv) +
                                          a11d[iy][2] * *(v2 + idv) +
                                          a11d[iy][3] * *(v3 + idv) +
                                          a11d[iy][4] * *(v4 + idv) +
                                          a11d[iy][5] * *(v5 + idv) +
                                          a11d[iy][6] * *(v6 + idv) +
                                          a11d[iy][7] * *(v7 + idv) +
                                          a11d[iy][8] * *(v8 + idv) +
                                          a11d[iy][9] * *(v9 + idv) +
                                          a11d[iy][10] * *(v10 + idv)) * odn;
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
                            *(dv + idz) += (a11d[iy][0] * *(v + idv) +
                                              a11d[iy][1] * *(v1 + idv) +
                                              a11d[iy][2] * *(v2 + idv) +
                                              a11d[iy][3] * *(v3 + idv) +
                                              a11d[iy][4] * *(v4 + idv) +
                                              a11d[iy][5] * *(v5 + idv) +
                                              a11d[iy][6] * *(v6 + idv) +
                                              a11d[iy][7] * *(v7 + idv) +
                                              a11d[iy][8] * *(v8 + idv) +
                                              a11d[iy][9] * *(v9 + idv) +
                                              a11d[iy][10] * *(v10 + idv)) * odn;
                    }
                }
            }
        }
    }
}


void d3add_yp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    dv += offset;
    odn += iymin;

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
                        *(dv + idz) += (a11d[iy][0] * *(v + idv) +
                                          a11d[iy][1] * *(v1 + idv) +
                                          a11d[iy][2] * *(v2 + idv) +
                                          a11d[iy][3] * *(v3 + idv) +
                                          a11d[iy][4] * *(v4 + idv) +
                                          a11d[iy][5] * *(v5 + idv) +
                                          a11d[iy][6] * *(v6 + idv) +
                                          a11d[iy][7] * *(v7 + idv) +
                                          a11d[iy][8] * *(v8 + idv) +
                                          a11d[iy][9] * *(v9 + idv) +
                                          a11d[iy][10] * *(v10 + idv)) * *(odn + iy);
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
                            *(dv + idz) += (a11d[iy][0] * *(v + idv) +
                                              a11d[iy][1] * *(v1 + idv) +
                                              a11d[iy][2] * *(v2 + idv) +
                                              a11d[iy][3] * *(v3 + idv) +
                                              a11d[iy][4] * *(v4 + idv) +
                                              a11d[iy][5] * *(v5 + idv) +
                                              a11d[iy][6] * *(v6 + idv) +
                                              a11d[iy][7] * *(v7 + idv) +
                                              a11d[iy][8] * *(v8 + idv) +
                                              a11d[iy][9] * *(v9 + idv) +
                                              a11d[iy][10] * *(v10 + idv)) * *(odn + iy);
                    }
                }
            }
        }
    }
}


void d3add_zp_s(double *restrict dv, const double *restrict v, const double odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                    dv_ix = dv + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dv_ix + iz) += (a11d[iz][0] * *(v + idy) +
                                            a11d[iz][1] * *(v1 + idy) +
                                            a11d[iz][2] * *(v2 + idy) +
                                            a11d[iz][3] * *(v3 + idy) +
                                            a11d[iz][4] * *(v4 + idy) +
                                            a11d[iz][5] * *(v5 + idy) +
                                            a11d[iz][6] * *(v6 + idy) +
                                            a11d[iz][7] * *(v7 + idy) +
                                            a11d[iz][8] * *(v8 + idy) +
                                            a11d[iz][9] * *(v9 + idy) +
                                            a11d[iz][10] * *(v10 + idy)) * odn;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dv_ix = dv + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dv_ix + iz) += (a11d[iz][0] * *(v + idy) +
                                                a11d[iz][1] * *(v1 + idy) +
                                                a11d[iz][2] * *(v2 + idy) +
                                                a11d[iz][3] * *(v3 + idy) +
                                                a11d[iz][4] * *(v4 + idy) +
                                                a11d[iz][5] * *(v5 + idy) +
                                                a11d[iz][6] * *(v6 + idy) +
                                                a11d[iz][7] * *(v7 + idy) +
                                                a11d[iz][8] * *(v8 + idy) +
                                                a11d[iz][9] * *(v9 + idy) +
                                                a11d[iz][10] * *(v10 + idy)) * odn;
                    }
                }
            }
        }
    }
}


void d3add_zp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;
    odn += izmin;

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
                    dv_ix = dv + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dv_ix + iz) += (a11d[iz][0] * *(v + idy) +
                                            a11d[iz][1] * *(v1 + idy) +
                                            a11d[iz][2] * *(v2 + idy) +
                                            a11d[iz][3] * *(v3 + idy) +
                                            a11d[iz][4] * *(v4 + idy) +
                                            a11d[iz][5] * *(v5 + idy) +
                                            a11d[iz][6] * *(v6 + idy) +
                                            a11d[iz][7] * *(v7 + idy) +
                                            a11d[iz][8] * *(v8 + idy) +
                                            a11d[iz][9] * *(v9 + idy) +
                                            a11d[iz][10] * *(v10 + idy)) * *(odn + iz);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dv_ix = dv + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dv_ix + iz) += (a11d[iz][0] * *(v + idy) +
                                                a11d[iz][1] * *(v1 + idy) +
                                                a11d[iz][2] * *(v2 + idy) +
                                                a11d[iz][3] * *(v3 + idy) +
                                                a11d[iz][4] * *(v4 + idy) +
                                                a11d[iz][5] * *(v5 + idy) +
                                                a11d[iz][6] * *(v6 + idy) +
                                                a11d[iz][7] * *(v7 + idy) +
                                                a11d[iz][8] * *(v8 + idy) +
                                                a11d[iz][9] * *(v9 + idy) +
                                                a11d[iz][10] * *(v10 + idy)) * *(odn + iz);
                    }
                }
            }
        }
    }
}


void d3add_xm_s(double *restrict dv, const double *restrict v, const double odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                    dv_ix = dv - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dv_ix + iz) -= (a11d[ix][0] * *(v + idz) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dv_ix = dv - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dv_ix + iz) -= (a11d[ix][0] * *(v + idz) +
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


void d3add_xm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;
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
                    dv_ix = dv - idx + idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idy + iz;
                        *(dv_ix + iz) -= (a11d[ix][0] * *(v + idz) +
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
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix < 5; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = iy * nz;
                        dv_ix = dv - idx + idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idy + iz;
                            *(dv_ix + iz) -= (a11d[ix][0] * *(v + idz) +
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


void d3add_ym_s(double *restrict dv, const double *restrict v, const double odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                    dv_ix = dv + idx - idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idx + iz;
                        *(dv_ix + iz) -= (a11d[iy][0] * *(v + idz) +
                                            a11d[iy][1] * *(v1 + idz) +
                                            a11d[iy][2] * *(v2 + idz) +
                                            a11d[iy][3] * *(v3 + idz) +
                                            a11d[iy][4] * *(v4 + idz) +
                                            a11d[iy][5] * *(v5 + idz) +
                                            a11d[iy][6] * *(v6 + idz) +
                                            a11d[iy][7] * *(v7 + idz) +
                                            a11d[iy][8] * *(v8 + idz) +
                                            a11d[iy][9] * *(v9 + idz) +
                                            a11d[iy][10] * *(v10 + idz)) * odn;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;
                        dv_ix = dv + idx - idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idx + iz;
                            *(dv_ix + iz) -= (a11d[iy][0] * *(v + idz) +
                                                a11d[iy][1] * *(v1 + idz) +
                                                a11d[iy][2] * *(v2 + idz) +
                                                a11d[iy][3] * *(v3 + idz) +
                                                a11d[iy][4] * *(v4 + idz) +
                                                a11d[iy][5] * *(v5 + idz) +
                                                a11d[iy][6] * *(v6 + idz) +
                                                a11d[iy][7] * *(v7 + idz) +
                                                a11d[iy][8] * *(v8 + idz) +
                                                a11d[iy][9] * *(v9 + idz) +
                                                a11d[iy][10] * *(v10 + idz)) * odn;
                    }
                }
            }
        }
    }
}


void d3add_ym_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;
    odn += iymax;

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
                    dv_ix = dv + idx - idy;

                    for (iz = 0; iz <= mz; iz++){
                        idz = idx + iz;
                        *(dv_ix + iz) -= (a11d[iy][0] * *(v + idz) +
                                            a11d[iy][1] * *(v1 + idz) +
                                            a11d[iy][2] * *(v2 + idz) +
                                            a11d[iy][3] * *(v3 + idz) +
                                            a11d[iy][4] * *(v4 + idz) +
                                            a11d[iy][5] * *(v5 + idz) +
                                            a11d[iy][6] * *(v6 + idz) +
                                            a11d[iy][7] * *(v7 + idz) +
                                            a11d[iy][8] * *(v8 + idz) +
                                            a11d[iy][9] * *(v9 + idz) +
                                            a11d[iy][10] * *(v10 + idz)) * *(odn - iy);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy < 5; iy++){
                        idy = iy * nz;
                        dv_ix = dv + idx - idy;

                        for (iz = 0; iz <= mz; iz++){
                            idz = idx + iz;
                            *(dv_ix + iz) -= (a11d[iy][0] * *(v + idz) +
                                                a11d[iy][1] * *(v1 + idz) +
                                                a11d[iy][2] * *(v2 + idz) +
                                                a11d[iy][3] * *(v3 + idz) +
                                                a11d[iy][4] * *(v4 + idz) +
                                                a11d[iy][5] * *(v5 + idz) +
                                                a11d[iy][6] * *(v6 + idz) +
                                                a11d[iy][7] * *(v7 + idz) +
                                                a11d[iy][8] * *(v8 + idz) +
                                                a11d[iy][9] * *(v9 + idz) +
                                                a11d[iy][10] * *(v10 + idz)) * *(odn - iy);
                    }
                }
            }
        }
    }
}


void d3add_zm_s(double *restrict dv, const double *restrict v, const double odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;

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
                    dv_ix = dv + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dv_ix - iz) -= (a11d[iz][0] * *(v + idy) +
                                            a11d[iz][1] * *(v1 + idy) +
                                            a11d[iz][2] * *(v2 + idy) +
                                            a11d[iz][3] * *(v3 + idy) +
                                            a11d[iz][4] * *(v4 + idy) +
                                            a11d[iz][5] * *(v5 + idy) +
                                            a11d[iz][6] * *(v6 + idy) +
                                            a11d[iz][7] * *(v7 + idy) +
                                            a11d[iz][8] * *(v8 + idy) +
                                            a11d[iz][9] * *(v9 + idy) +
                                            a11d[iz][10] * *(v10 + idy)) * odn;
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dv_ix = dv + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dv_ix - iz) -= (a11d[iz][0] * *(v + idy) +
                                                a11d[iz][1] * *(v1 + idy) +
                                                a11d[iz][2] * *(v2 + idy) +
                                                a11d[iz][3] * *(v3 + idy) +
                                                a11d[iz][4] * *(v4 + idy) +
                                                a11d[iz][5] * *(v5 + idy) +
                                                a11d[iz][6] * *(v6 + idy) +
                                                a11d[iz][7] * *(v7 + idy) +
                                                a11d[iz][8] * *(v8 + idy) +
                                                a11d[iz][9] * *(v9 + idy) +
                                                a11d[iz][10] * *(v10 + idy)) * odn;
                    }
                }
            }
        }
    }
}


void d3add_zm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
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
    double *restrict dv_ix;

    v += offset;
    dv += offset;
    odn += izmax;

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
                    dv_ix = dv + idy;

                    for (iz = 0; iz < 5; iz++){
                        *(dv_ix - iz) -= (a11d[iz][0] * *(v + idy) +
                                            a11d[iz][1] * *(v1 + idy) +
                                            a11d[iz][2] * *(v2 + idy) +
                                            a11d[iz][3] * *(v3 + idy) +
                                            a11d[iz][4] * *(v4 + idy) +
                                            a11d[iz][5] * *(v5 + idy) +
                                            a11d[iz][6] * *(v6 + idy) +
                                            a11d[iz][7] * *(v7 + idy) +
                                            a11d[iz][8] * *(v8 + idy) +
                                            a11d[iz][9] * *(v9 + idy) +
                                            a11d[iz][10] * *(v10 + idy)) * *(odn - iz);
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, dv_ix)
            {
                #pragma omp for nowait
                for (ix = 0; ix <= mx; ix++){
                    idx = ix * nynz;

                    for (iy = 0; iy <= my; iy++){
                        idy = idx + iy * nz;
                        dv_ix = dv + idy;

                        for (iz = 0; iz < 5; iz++){
                            *(dv_ix - iz) -= (a11d[iz][0] * *(v + idy) +
                                                a11d[iz][1] * *(v1 + idy) +
                                                a11d[iz][2] * *(v2 + idy) +
                                                a11d[iz][3] * *(v3 + idy) +
                                                a11d[iz][4] * *(v4 + idy) +
                                                a11d[iz][5] * *(v5 + idy) +
                                                a11d[iz][6] * *(v6 + idy) +
                                                a11d[iz][7] * *(v7 + idy) +
                                                a11d[iz][8] * *(v8 + idy) +
                                                a11d[iz][9] * *(v9 + idy) +
                                                a11d[iz][10] * *(v10 + idy)) * *(odn - iz);
                    }
                }
            }
        }
    }
}

