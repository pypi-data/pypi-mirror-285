#include <stdio.h>
#include <omp.h>
#include <time.h>
#include "coefficients.h"
#include "kernels_sf.h"


////////////////////////////////////////////////////////////////////////////////
// 2d SF
////////////////////////////////////////////////////////////////////////////////

void sf2d_xc(double *restrict vf, const double *restrict v, double xnu_n,
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
                    *(vf + idy) = xnu_n * (d11c[0] *  *(v + idy) +
                                           d11c[1] * (*(v_1p + idy) + *(v_1m + idy)) +
                                           d11c[2] * (*(v_2p + idy) + *(v_2m + idy)) +
                                           d11c[3] * (*(v_3p + idy) + *(v_3m + idy)) +
                                           d11c[4] * (*(v_4p + idy) + *(v_4m + idy)) +
                                           d11c[5] * (*(v_5p + idy) + *(v_5m + idy)));
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
                        *(vf + idy) = xnu_n * (d11c[0] *  *(v + idy) +
                                               d11c[1] * (*(v_1p + idy) + *(v_1m + idy)) +
                                               d11c[2] * (*(v_2p + idy) + *(v_2m + idy)) +
                                               d11c[3] * (*(v_3p + idy) + *(v_3m + idy)) +
                                               d11c[4] * (*(v_4p + idy) + *(v_4m + idy)) +
                                               d11c[5] * (*(v_5p + idy) + *(v_5m + idy)));
                }
            }
        }
    }
}


void sf2d_yc(double *restrict vf, const double *restrict v, double xnu_n,
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
                    *(vf + idy) = xnu_n * (d11c[0] * *(v + idy) +
                                           d11c[1] * (*(v_1p + idy) + *(v_1m + idy)) +
                                           d11c[2] * (*(v_2p + idy) + *(v_2m + idy)) +
                                           d11c[3] * (*(v_3p + idy) + *(v_3m + idy)) +
                                           d11c[4] * (*(v_4p + idy) + *(v_4m + idy)) +
                                           d11c[5] * (*(v_5p + idy) + *(v_5m + idy)));
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
                        *(vf + idy) = xnu_n * (d11c[0] * *(v + idy) +
                                               d11c[1] * (*(v_1p + idy) + *(v_1m + idy)) +
                                               d11c[2] * (*(v_2p + idy) + *(v_2m + idy)) +
                                               d11c[3] * (*(v_3p + idy) + *(v_3m + idy)) +
                                               d11c[4] * (*(v_4p + idy) + *(v_4m + idy)) +
                                               d11c[5] * (*(v_5p + idy) + *(v_5m + idy)));
                }
            }
        }
    }
}


void sf2d_xP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    unsigned int ix, iy, idx, idy;
    const double *restrict v0;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * ny;

                v0 = v + *(Px + ix) * ny;
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
                    *(vf + idy) = xnu_n * (d11c[0] *  *(v0 + iy) +
                                           d11c[1] * (*(v1p + iy) + *(v1m + iy)) +
                                           d11c[2] * (*(v2p + iy) + *(v2m + iy)) +
                                           d11c[3] * (*(v3p + iy) + *(v3m + iy)) +
                                           d11c[4] * (*(v4p + iy) + *(v4m + iy)) +
                                           d11c[5] * (*(v5p + iy) + *(v5m + iy)));
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, v0, \
                                                            v1m, v2m, v3m, v4m, v5m, \
                                                            v1p, v2p, v3p, v4p, v5p)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * ny;

                    v0 = v + *(Px + ix) * ny;
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
                        *(vf + idy) = xnu_n * (d11c[0] *  *(v0 + iy) +
                                               d11c[1] * (*(v1p + iy) + *(v1m + iy)) +
                                               d11c[2] * (*(v2p + iy) + *(v2m + iy)) +
                                               d11c[3] * (*(v3p + iy) + *(v3m + iy)) +
                                               d11c[4] * (*(v4p + iy) + *(v4m + iy)) +
                                               d11c[5] * (*(v5p + iy) + *(v5m + iy)));
                }
            }
        }
    }
}


void sf2d_yP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

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
                    *(vf + idy) = xnu_n * (d11c[0] *  *(vix + *(Py + iy)) +
                                           d11c[1] * (*(vix + *(Py + iy + 1)) + *(vix + *(Py + iy - 1))) +
                                           d11c[2] * (*(vix + *(Py + iy + 2)) + *(vix + *(Py + iy - 2))) +
                                           d11c[3] * (*(vix + *(Py + iy + 3)) + *(vix + *(Py + iy - 3))) +
                                           d11c[4] * (*(vix + *(Py + iy + 4)) + *(vix + *(Py + iy - 4))) +
                                           d11c[5] * (*(vix + *(Py + iy + 5)) + *(vix + *(Py + iy - 5))));
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
                        *(vf + idy) = xnu_n * (d11c[0] *  *(vix + *(Py + iy)) +
                                               d11c[1] * (*(vix + *(Py + iy + 1)) + *(vix + *(Py + iy - 1))) +
                                               d11c[2] * (*(vix + *(Py + iy + 2)) + *(vix + *(Py + iy - 2))) +
                                               d11c[3] * (*(vix + *(Py + iy + 3)) + *(vix + *(Py + iy - 3))) +
                                               d11c[4] * (*(vix + *(Py + iy + 4)) + *(vix + *(Py + iy - 4))) +
                                               d11c[5] * (*(vix + *(Py + iy + 5)) + *(vix + *(Py + iy - 5))));
                }
            }
        }
    }
}


void sf2d_xp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf + ny;
    double *restrict vf2 = vf1 + ny;
    double *restrict vf3 = vf2 + ny;
    double *restrict vf4 = vf3 + ny;

    switch(threads){
        case 1:
            for (iy = 0; iy <= my; iy++){
                *(vf + iy) = xnu_0 * (d11d[1][1] * *(v + iy) +
                                      d11d[1][2] * *(v1 + iy) +
                                      d11d[1][3] * *(v2 + iy) +
                                      d11d[1][4] * *(v3 + iy));
                *(vf1 + iy) = xnu_n * (d11d[2][1] * *(v + iy) +
                                       d11d[2][2] * *(v1 + iy) +
                                       d11d[2][3] * *(v2 + iy) +
                                       d11d[2][4] * *(v3 + iy) +
                                       d11d[2][5] * *(v4 + iy) +
                                       d11d[2][6] * *(v5 + iy) +
                                       d11d[2][7] * *(v6 + iy));
                *(vf2 + iy) = xnu_n * (d11d[3][1] * *(v + iy) +
                                       d11d[3][2] * *(v1 + iy) +
                                       d11d[3][3] * *(v2 + iy) +
                                       d11d[3][4] * *(v3 + iy) +
                                       d11d[3][5] * *(v4 + iy) +
                                       d11d[3][6] * *(v5 + iy) +
                                       d11d[3][7] * *(v6 + iy) +
                                       d11d[3][8] * *(v7 + iy) +
                                       d11d[3][9] * *(v8 + iy) +
                                       d11d[3][10] * *(v9 + iy) +
                                       d11d[3][11] * *(v10 + iy));
                *(vf3 + iy) = xnu_n * (d11d[4][1] * *(v + iy) +
                                       d11d[4][2] * *(v1 + iy) +
                                       d11d[4][3] * *(v2 + iy) +
                                       d11d[4][4] * *(v3 + iy) +
                                       d11d[4][5] * *(v4 + iy) +
                                       d11d[4][6] * *(v5 + iy) +
                                       d11d[4][7] * *(v6 + iy) +
                                       d11d[4][8] * *(v7 + iy) +
                                       d11d[4][9] * *(v8 + iy) +
                                       d11d[4][10] * *(v9 + iy) +
                                       d11d[4][11] * *(v10 + iy));
                *(vf4 + iy) = xnu_n * (d11d[5][1] * *(v + iy) +
                                       d11d[5][2] * *(v1 + iy) +
                                       d11d[5][3] * *(v2 + iy) +
                                       d11d[5][4] * *(v3 + iy) +
                                       d11d[5][5] * *(v4 + iy) +
                                       d11d[5][6] * *(v5 + iy) +
                                       d11d[5][7] * *(v6 + iy) +
                                       d11d[5][8] * *(v7 + iy) +
                                       d11d[5][9] * *(v8 + iy) +
                                       d11d[5][10] * *(v9 + iy) +
                                       d11d[5][11] * *(v10 + iy));
            }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(iy)
            {
            #pragma omp for nowait
            for (iy = 0; iy <= my; iy++){
                *(vf + iy) = xnu_0 * (d11d[1][1] * *(v + iy) +
                                      d11d[1][2] * *(v1 + iy) +
                                      d11d[1][3] * *(v2 + iy) +
                                      d11d[1][4] * *(v3 + iy));
                *(vf1 + iy) = xnu_n * (d11d[2][1] * *(v + iy) +
                                       d11d[2][2] * *(v1 + iy) +
                                       d11d[2][3] * *(v2 + iy) +
                                       d11d[2][4] * *(v3 + iy) +
                                       d11d[2][5] * *(v4 + iy) +
                                       d11d[2][6] * *(v5 + iy) +
                                       d11d[2][7] * *(v6 + iy));
                *(vf2 + iy) = xnu_n * (d11d[3][1] * *(v + iy) +
                                       d11d[3][2] * *(v1 + iy) +
                                       d11d[3][3] * *(v2 + iy) +
                                       d11d[3][4] * *(v3 + iy) +
                                       d11d[3][5] * *(v4 + iy) +
                                       d11d[3][6] * *(v5 + iy) +
                                       d11d[3][7] * *(v6 + iy) +
                                       d11d[3][8] * *(v7 + iy) +
                                       d11d[3][9] * *(v8 + iy) +
                                       d11d[3][10] * *(v9 + iy) +
                                       d11d[3][11] * *(v10 + iy));
                *(vf3 + iy) = xnu_n * (d11d[4][1] * *(v + iy) +
                                       d11d[4][2] * *(v1 + iy) +
                                       d11d[4][3] * *(v2 + iy) +
                                       d11d[4][4] * *(v3 + iy) +
                                       d11d[4][5] * *(v4 + iy) +
                                       d11d[4][6] * *(v5 + iy) +
                                       d11d[4][7] * *(v6 + iy) +
                                       d11d[4][8] * *(v7 + iy) +
                                       d11d[4][9] * *(v8 + iy) +
                                       d11d[4][10] * *(v9 + iy) +
                                       d11d[4][11] * *(v10 + iy));
                *(vf4 + iy) = xnu_n * (d11d[5][1] * *(v + iy) +
                                       d11d[5][2] * *(v1 + iy) +
                                       d11d[5][3] * *(v2 + iy) +
                                       d11d[5][4] * *(v3 + iy) +
                                       d11d[5][5] * *(v4 + iy) +
                                       d11d[5][6] * *(v5 + iy) +
                                       d11d[5][7] * *(v6 + iy) +
                                       d11d[5][8] * *(v7 + iy) +
                                       d11d[5][9] * *(v8 + iy) +
                                       d11d[5][10] * *(v9 + iy) +
                                       d11d[5][11] * *(v10 + iy));
            }
        }
    }
}


void sf2d_xm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy;
    const unsigned int my = iymax - iymin;
    const unsigned int offset = ixmax * ny + iymin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf - ny;
    double *restrict vf2 = vf1 - ny;
    double *restrict vf3 = vf2 - ny;
    double *restrict vf4 = vf3 - ny;

    for (iy = 0; iy <= my; iy++){
        *(vf + iy) = xnu_0 * (d11d[1][1] * *(v + iy) +
                              d11d[1][2] * *(v1 + iy) +
                              d11d[1][3] * *(v2 + iy) +
                              d11d[1][4] * *(v3 + iy));
        *(vf1 + iy) = xnu_n * (d11d[2][1] * *(v + iy) +
                               d11d[2][2] * *(v1 + iy) +
                               d11d[2][3] * *(v2 + iy) +
                               d11d[2][4] * *(v3 + iy) +
                               d11d[2][5] * *(v4 + iy) +
                               d11d[2][6] * *(v5 + iy) +
                               d11d[2][7] * *(v6 + iy));
        *(vf2 + iy) = xnu_n * (d11d[3][1] * *(v + iy) +
                               d11d[3][2] * *(v1 + iy) +
                               d11d[3][3] * *(v2 + iy) +
                               d11d[3][4] * *(v3 + iy) +
                               d11d[3][5] * *(v4 + iy) +
                               d11d[3][6] * *(v5 + iy) +
                               d11d[3][7] * *(v6 + iy) +
                               d11d[3][8] * *(v7 + iy) +
                               d11d[3][9] * *(v8 + iy) +
                               d11d[3][10] * *(v9 + iy) +
                               d11d[3][11] * *(v10 + iy));
        *(vf3 + iy) = xnu_n * (d11d[4][1] * *(v + iy) +
                               d11d[4][2] * *(v1 + iy) +
                               d11d[4][3] * *(v2 + iy) +
                               d11d[4][4] * *(v3 + iy) +
                               d11d[4][5] * *(v4 + iy) +
                               d11d[4][6] * *(v5 + iy) +
                               d11d[4][7] * *(v6 + iy) +
                               d11d[4][8] * *(v7 + iy) +
                               d11d[4][9] * *(v8 + iy) +
                               d11d[4][10] * *(v9 + iy) +
                               d11d[4][11] * *(v10 + iy));
        *(vf4 + iy) = xnu_n * (d11d[5][1] * *(v + iy) +
                               d11d[5][2] * *(v1 + iy) +
                               d11d[5][3] * *(v2 + iy) +
                               d11d[5][4] * *(v3 + iy) +
                               d11d[5][5] * *(v4 + iy) +
                               d11d[5][6] * *(v5 + iy) +
                               d11d[5][7] * *(v6 + iy) +
                               d11d[5][8] * *(v7 + iy) +
                               d11d[5][9] * *(v8 + iy) +
                               d11d[5][10] * *(v9 + iy) +
                               d11d[5][11] * *(v10 + iy));
    }
}


void sf2d_yp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf + 1;
    double *restrict vf2 = vf1 + 1;
    double *restrict vf3 = vf2 + 1;
    double *restrict vf4 = vf3 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        *(vf + idx) = xnu_0 * (d11d[1][1]* *(v + idx) +
                               d11d[1][2]* *(v1 + idx) +
                               d11d[1][3]* *(v2 + idx) +
                               d11d[1][4]* *(v3 + idx));
        *(vf1 + idx) = xnu_n * (d11d[2][1]* *(v + idx) +
                                d11d[2][2]* *(v1 + idx) +
                                d11d[2][3]* *(v2 + idx) +
                                d11d[2][4]* *(v3 + idx) +
                                d11d[2][5]* *(v4 + idx) +
                                d11d[2][6]* *(v5 + idx) +
                                d11d[2][7]* *(v6 + idx));
        *(vf2 + idx) = xnu_n * (d11d[3][1]* *(v + idx) +
                                d11d[3][2]* *(v1 + idx) +
                                d11d[3][3]* *(v2 + idx) +
                                d11d[3][4]* *(v3 + idx) +
                                d11d[3][5]* *(v4 + idx) +
                                d11d[3][6]* *(v5 + idx) +
                                d11d[3][7]* *(v6 + idx) +
                                d11d[3][8]* *(v7 + idx) +
                                d11d[3][9]* *(v8 + idx) +
                                d11d[3][10]* *(v9 + idx) +
                                d11d[3][11]* *(v10 + idx));
        *(vf3 + idx) = xnu_n * (d11d[4][1]* *(v + idx) +
                                d11d[4][2]* *(v1 + idx) +
                                d11d[4][3]* *(v2 + idx) +
                                d11d[4][4]* *(v3 + idx) +
                                d11d[4][5]* *(v4 + idx) +
                                d11d[4][6]* *(v5 + idx) +
                                d11d[4][7]* *(v6 + idx) +
                                d11d[4][8]* *(v7 + idx) +
                                d11d[4][9]* *(v8 + idx) +
                                d11d[4][10]* *(v9 + idx) +
                                d11d[4][11]* *(v10 + idx));
        *(vf4 + idx) = xnu_n * (d11d[5][1]* *(v + idx) +
                                d11d[5][2]* *(v1 + idx) +
                                d11d[5][3]* *(v2 + idx) +
                                d11d[5][4]* *(v3 + idx) +
                                d11d[5][5]* *(v4 + idx) +
                                d11d[5][6]* *(v5 + idx) +
                                d11d[5][7]* *(v6 + idx) +
                                d11d[5][8]* *(v7 + idx) +
                                d11d[5][9]* *(v8 + idx) +
                                d11d[5][10]* *(v9 + idx) +
                                d11d[5][11]* *(v10 + idx));
    }
}


void sf2d_ym(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, idx;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int offset = ixmin * ny + iymax;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf - 1;
    double *restrict vf2 = vf1 - 1;
    double *restrict vf3 = vf2 - 1;
    double *restrict vf4 = vf3 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * ny;
        *(vf + idx) = xnu_0 * (d11d[1][1]* *(v + idx) +
                               d11d[1][2]* *(v1 + idx) +
                               d11d[1][3]* *(v2 + idx) +
                               d11d[1][4]* *(v3 + idx));
        *(vf1 + idx) = xnu_n * (d11d[2][1]* *(v + idx) +
                                d11d[2][2]* *(v1 + idx) +
                                d11d[2][3]* *(v2 + idx) +
                                d11d[2][4]* *(v3 + idx) +
                                d11d[2][5]* *(v4 + idx) +
                                d11d[2][6]* *(v5 + idx) +
                                d11d[2][7]* *(v6 + idx));
        *(vf2 + idx) = xnu_n * (d11d[3][1]* *(v + idx) +
                                d11d[3][2]* *(v1 + idx) +
                                d11d[3][3]* *(v2 + idx) +
                                d11d[3][4]* *(v3 + idx) +
                                d11d[3][5]* *(v4 + idx) +
                                d11d[3][6]* *(v5 + idx) +
                                d11d[3][7]* *(v6 + idx) +
                                d11d[3][8]* *(v7 + idx) +
                                d11d[3][9]* *(v8 + idx) +
                                d11d[3][10]* *(v9 + idx) +
                                d11d[3][11]* *(v10 + idx));
        *(vf3 + idx) = xnu_n * (d11d[4][1]* *(v + idx) +
                                d11d[4][2]* *(v1 + idx) +
                                d11d[4][3]* *(v2 + idx) +
                                d11d[4][4]* *(v3 + idx) +
                                d11d[4][5]* *(v4 + idx) +
                                d11d[4][6]* *(v5 + idx) +
                                d11d[4][7]* *(v6 + idx) +
                                d11d[4][8]* *(v7 + idx) +
                                d11d[4][9]* *(v8 + idx) +
                                d11d[4][10]* *(v9 + idx) +
                                d11d[4][11]* *(v10 + idx));
        *(vf4 + idx) = xnu_n * (d11d[5][1]* *(v + idx) +
                                d11d[5][2]* *(v1 + idx) +
                                d11d[5][3]* *(v2 + idx) +
                                d11d[5][4]* *(v3 + idx) +
                                d11d[5][5]* *(v4 + idx) +
                                d11d[5][6]* *(v5 + idx) +
                                d11d[5][7]* *(v6 + idx) +
                                d11d[5][8]* *(v7 + idx) +
                                d11d[5][9]* *(v8 + idx) +
                                d11d[5][10]* *(v9 + idx) +
                                d11d[5][11]* *(v10 + idx));
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d SF
////////////////////////////////////////////////////////////////////////////////

void sf3d_xc(double *restrict vf, const double *restrict v, double xnu_n,
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
        for (ix=0; ix <= mx; ix++){
            idx = ix * nynz;

            for (iy=0; iy <= my; iy++){
                idy = idx + iy * nz;

                for (iz=0; iz <= mz; iz++){
                    idz = idy + iz;
                    *(vf + idz) = xnu_n * (d11c[0] *  *(v + idz) +
                                           d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                           d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                           d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                           d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                           d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
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
                        *(vf + idz) = xnu_n * (d11c[0] *  *(v + idz) +
                                               d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                               d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                               d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                               d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                               d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
                    }
                }
            }
        }
    }
}


void sf3d_yc(double *restrict vf, const double *restrict v, double xnu_n,
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
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    *(vf + idz) = xnu_n * (d11c[0] * *(v + idz) +
                                           d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                           d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                           d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                           d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                           d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
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
                        *(vf + idz) = xnu_n * (d11c[0] * *(v + idz) +
                                               d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                               d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                               d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                               d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                               d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
                    }
                }
            }
        }
    }
}


void sf3d_zc(double *restrict vf, const double *restrict v, double xnu_n,
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
        for (ix = 0; ix <= mx; ix++) {
            idx = ix * nynz;

            for (iy = 0; iy <= my; iy++) {
                idy = idx + iy * nz;

                for (iz = 0; iz <= mz; iz++) {
                    idz = idy + iz;
                    *(vf + idz) = xnu_n * (d11c[0] * *(v + idz) +
                                           d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                           d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                           d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                           d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                           d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
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
                        *(vf + idz) = xnu_n * (d11c[0] * *(v + idz) +
                                               d11c[1] * (*(v_1p + idz) + *(v_1m + idz)) +
                                               d11c[2] * (*(v_2p + idz) + *(v_2m + idz)) +
                                               d11c[3] * (*(v_3p + idz) + *(v_3m + idz)) +
                                               d11c[4] * (*(v_4p + idz) + *(v_4m + idz)) +
                                               d11c[5] * (*(v_5p + idz) + *(v_5m + idz)));
                    }
                }
            }
        }
    }
}


void sf3d_xP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz, idn;
    const unsigned int nynz = ny * nz;
    const double *restrict v0;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Px = P + 5;

    switch(threads){
        case 1:
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;
            v0 = v + *(Px + ix) * nynz;
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
                    *(vf + idz) = xnu_n * (d11c[0] * *(v0 + idn) +
                                           d11c[1] * (*(v1p + idn) + *(v1m + idn)) +
                                           d11c[2] * (*(v2p + idn) + *(v2m + idn)) +
                                           d11c[3] * (*(v3p + idn) + *(v3m + idn)) +
                                           d11c[4] * (*(v4p + idn) + *(v4m + idn)) +
                                           d11c[5] * (*(v5p + idn) + *(v5m + idn)));
                }
            }
        }
        break;
    default:
        #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
            idx, idy, idz, idn, v0, v1p, v2p, v3p, v4p, v5p, v1m, v2m, v3m, v4m, v5m)
            {
            #pragma omp for nowait
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;
                v0 = v + *(Px + ix) * nynz;
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
                        *(vf + idz) = xnu_n * (d11c[0] * *(v0 + idn) +
                                               d11c[1] * (*(v1p + idn) + *(v1m + idn)) +
                                               d11c[2] * (*(v2p + idn) + *(v2m + idn)) +
                                               d11c[3] * (*(v3p + idn) + *(v3m + idn)) +
                                               d11c[4] * (*(v4p + idn) + *(v4m + idn)) +
                                               d11c[5] * (*(v5p + idn) + *(v5m + idn)));
                    }
                }
            }
        }
    }
}


void sf3d_yP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    const double *restrict v0;
    const double *restrict v1m, *restrict v2m, *restrict v3m, *restrict v4m, *restrict v5m;
    const double *restrict v1p, *restrict v2p, *restrict v3p, *restrict v4p, *restrict v5p;
    const unsigned int *restrict Py = P + 5;

    switch(threads){
        case 1:
            for (ix = ixmin; ix <= ixmax; ix++) {
                idx = ix * nynz;

                for (iy = iymin; iy <= iymax; iy++) {
                    idy = idx + iy * nz;
                    v0 = v + idx +  *(Py + iy) * nz;
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
                        *(vf + idz) = xnu_n * (d11c[0] *  *(v0 + iz) +
                                               d11c[1] * (*(v1p + iz) + *(v1m + iz)) +
                                               d11c[2] * (*(v2p + iz) + *(v2m + iz)) +
                                               d11c[3] * (*(v3p + iz) + *(v3m + iz)) +
                                               d11c[4] * (*(v4p + iz) + *(v4m + iz)) +
                                               d11c[5] * (*(v5p + iz) + *(v5m + iz)));
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
                idx, idy, idz, v0, v1p, v2p, v3p, v4p, v5p, v1m, v2m, v3m, v4m, v5m)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;
                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        v0 = v + idx +  *(Py + iy) * nz;
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
                            *(vf + idz) = xnu_n * (d11c[0] *  *(v0 + iz) +
                                                   d11c[1] * (*(v1p + iz) + *(v1m + iz)) +
                                                   d11c[2] * (*(v2p + iz) + *(v2m + iz)) +
                                                   d11c[3] * (*(v3p + iz) + *(v3m + iz)) +
                                                   d11c[4] * (*(v4p + iz) + *(v4m + iz)) +
                                                   d11c[5] * (*(v5p + iz) + *(v5m + iz)));
                    }
                }
            }
        }
    }
}


void sf3d_zP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int nynz = ny * nz;
    const unsigned int *restrict Pz = P + 5;
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
                        *(vf + idz) = xnu_n * (d11c[0] *  *(viy + *(Pz + iz)) +
                                               d11c[1] * (*(viy + *(Pz + iz + 1)) + *(viy + *(Pz + iz - 1))) +
                                               d11c[2] * (*(viy + *(Pz + iz + 2)) + *(viy + *(Pz + iz - 2))) +
                                               d11c[3] * (*(viy + *(Pz + iz + 3)) + *(viy + *(Pz + iz - 3))) +
                                               d11c[4] * (*(viy + *(Pz + iz + 4)) + *(viy + *(Pz + iz - 4))) +
                                               d11c[5] * (*(viy + *(Pz + iz + 5)) + *(viy + *(Pz + iz - 5))));
                    }
                }
            }
            break;
        default:
            #pragma omp parallel num_threads(threads) private(ix, iy, iz, \
                                                                idx, idy, idz, viy)
            {
                #pragma omp for nowait
                for (ix = ixmin; ix <= ixmax; ix++) {
                    idx = ix * nynz;

                    for (iy = iymin; iy <= iymax; iy++) {
                        idy = idx + iy * nz;
                        viy = v + idy;

                        for (iz = izmin; iz <= izmax; iz++) {
                            idz = idy + iz;
                            *(vf + idz) = xnu_n * (d11c[0] *  *(viy + *(Pz + iz)) +
                                                   d11c[1] * (*(viy + *(Pz + iz + 1)) + *(viy + *(Pz + iz - 1))) +
                                                   d11c[2] * (*(viy + *(Pz + iz + 2)) + *(viy + *(Pz + iz - 2))) +
                                                   d11c[3] * (*(viy + *(Pz + iz + 3)) + *(viy + *(Pz + iz - 3))) +
                                                   d11c[4] * (*(viy + *(Pz + iz + 4)) + *(viy + *(Pz + iz - 4))) +
                                                   d11c[5] * (*(viy + *(Pz + iz + 5)) + *(viy + *(Pz + iz - 5))));
                    }
                }
            }
        }
    }
}


void sf3d_xp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(ixmax);
    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf + nynz;
    double *restrict vf2 = vf1 + nynz;
    double *restrict vf3 = vf2 + nynz;
    double *restrict vf4 = vf3 + nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            *(vf + idz) = xnu_0 * (d11d[1][1] * *(v + idz) +
                                   d11d[1][2] * *(v1 + idz) +
                                   d11d[1][3] * *(v2 + idz) +
                                   d11d[1][4] * *(v3 + idz));
            *(vf1 + idz) = xnu_n * (d11d[2][1] * *(v + idz) +
                                    d11d[2][2] * *(v1 + idz) +
                                    d11d[2][3] * *(v2 + idz) +
                                    d11d[2][4] * *(v3 + idz) +
                                    d11d[2][5] * *(v4 + idz) +
                                    d11d[2][6] * *(v5 + idz) +
                                    d11d[2][7] * *(v6 + idz));
            *(vf2 + idz) = xnu_n * (d11d[3][1] * *(v + idz) +
                                    d11d[3][2] * *(v1 + idz) +
                                    d11d[3][3] * *(v2 + idz) +
                                    d11d[3][4] * *(v3 + idz) +
                                    d11d[3][5] * *(v4 + idz) +
                                    d11d[3][6] * *(v5 + idz) +
                                    d11d[3][7] * *(v6 + idz) +
                                    d11d[3][8] * *(v7 + idz) +
                                    d11d[3][9] * *(v8 + idz) +
                                    d11d[3][10] * *(v9 + idz) +
                                    d11d[3][11] * *(v10 + idz));
            *(vf3 + idz) = xnu_n * (d11d[4][1] * *(v + idz) +
                                    d11d[4][2] * *(v1 + idz) +
                                    d11d[4][3] * *(v2 + idz) +
                                    d11d[4][4] * *(v3 + idz) +
                                    d11d[4][5] * *(v4 + idz) +
                                    d11d[4][6] * *(v5 + idz) +
                                    d11d[4][7] * *(v6 + idz) +
                                    d11d[4][8] * *(v7 + idz) +
                                    d11d[4][9] * *(v8 + idz) +
                                    d11d[4][10] * *(v9 + idz) +
                                    d11d[4][11] * *(v10 + idz));
            *(vf4 + idz) = xnu_n * (d11d[5][1] * *(v + idz) +
                                    d11d[5][2] * *(v1 + idz) +
                                    d11d[5][3] * *(v2 + idz) +
                                    d11d[5][4] * *(v3 + idz) +
                                    d11d[5][5] * *(v4 + idz) +
                                    d11d[5][6] * *(v5 + idz) +
                                    d11d[5][7] * *(v6 + idz) +
                                    d11d[5][8] * *(v7 + idz) +
                                    d11d[5][9] * *(v8 + idz) +
                                    d11d[5][10] * *(v9 + idz) +
                                    d11d[5][11] * *(v10 + idz));
        }
    }
}


void sf3d_xm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(ixmin);
    unsigned int iy, iz, idy, idz;
    const unsigned int my = iymax - iymin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmax * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf - nynz;
    double *restrict vf2 = vf1 - nynz;
    double *restrict vf3 = vf2 - nynz;
    double *restrict vf4 = vf3 - nynz;

    for (iy = 0; iy <= my; iy++){
        idy = iy * nz;

        for (iz = 0; iz <= mz; iz++){
            idz = idy + iz;
            *(vf + idz) = xnu_0 * (d11d[1][1] * *(v + idz) +
                                   d11d[1][2] * *(v1 + idz) +
                                   d11d[1][3] * *(v2 + idz) +
                                   d11d[1][4] * *(v3 + idz));
            *(vf1 + idz) = xnu_n * (d11d[2][1] * *(v + idz) +
                                    d11d[2][2] * *(v1 + idz) +
                                    d11d[2][3] * *(v2 + idz) +
                                    d11d[2][4] * *(v3 + idz) +
                                    d11d[2][5] * *(v4 + idz) +
                                    d11d[2][6] * *(v5 + idz) +
                                    d11d[2][7] * *(v6 + idz));
            *(vf2 + idz) = xnu_n * (d11d[3][1] * *(v + idz) +
                                    d11d[3][2] * *(v1 + idz) +
                                    d11d[3][3] * *(v2 + idz) +
                                    d11d[3][4] * *(v3 + idz) +
                                    d11d[3][5] * *(v4 + idz) +
                                    d11d[3][6] * *(v5 + idz) +
                                    d11d[3][7] * *(v6 + idz) +
                                    d11d[3][8] * *(v7 + idz) +
                                    d11d[3][9] * *(v8 + idz) +
                                    d11d[3][10] * *(v9 + idz) +
                                    d11d[3][11] * *(v10 + idz));
            *(vf3 + idz) = xnu_n * (d11d[4][1] * *(v + idz) +
                                    d11d[4][2] * *(v1 + idz) +
                                    d11d[4][3] * *(v2 + idz) +
                                    d11d[4][4] * *(v3 + idz) +
                                    d11d[4][5] * *(v4 + idz) +
                                    d11d[4][6] * *(v5 + idz) +
                                    d11d[4][7] * *(v6 + idz) +
                                    d11d[4][8] * *(v7 + idz) +
                                    d11d[4][9] * *(v8 + idz) +
                                    d11d[4][10] * *(v9 + idz) +
                                    d11d[4][11] * *(v10 + idz));
            *(vf4 + idz) = xnu_n * (d11d[5][1] * *(v + idz) +
                                    d11d[5][2] * *(v1 + idz) +
                                    d11d[5][3] * *(v2 + idz) +
                                    d11d[5][4] * *(v3 + idz) +
                                    d11d[5][5] * *(v4 + idz) +
                                    d11d[5][6] * *(v5 + idz) +
                                    d11d[5][7] * *(v6 + idz) +
                                    d11d[5][8] * *(v7 + idz) +
                                    d11d[5][9] * *(v8 + idz) +
                                    d11d[5][10] * *(v9 + idz) +
                                    d11d[5][11] * *(v10 + idz));
        }
    }
}


void sf3d_yp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(iymax);
    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf + nz;
    double *restrict vf2 = vf1 + nz;
    double *restrict vf3 = vf2 + nz;
    double *restrict vf4 = vf3 + nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            *(vf + idz) = xnu_0 * (d11d[1][1]* *(v + idz) +
                                   d11d[1][2]* *(v1 + idz) +
                                   d11d[1][3]* *(v2 + idz) +
                                   d11d[1][4]* *(v3 + idz));
            *(vf1 + idz) = xnu_n * (d11d[2][1]* *(v + idz) +
                                    d11d[2][2]* *(v1 + idz) +
                                    d11d[2][3]* *(v2 + idz) +
                                    d11d[2][4]* *(v3 + idz) +
                                    d11d[2][5]* *(v4 + idz) +
                                    d11d[2][6]* *(v5 + idz) +
                                    d11d[2][7]* *(v6 + idz));
            *(vf2 + idz) = xnu_n * (d11d[3][1]* *(v + idz) +
                                    d11d[3][2]* *(v1 + idz) +
                                    d11d[3][3]* *(v2 + idz) +
                                    d11d[3][4]* *(v3 + idz) +
                                    d11d[3][5]* *(v4 + idz) +
                                    d11d[3][6]* *(v5 + idz) +
                                    d11d[3][7]* *(v6 + idz) +
                                    d11d[3][8]* *(v7 + idz) +
                                    d11d[3][9]* *(v8 + idz) +
                                    d11d[3][10]* *(v9 + idz) +
                                    d11d[3][11]* *(v10 + idz));
            *(vf3 + idz) = xnu_n * (d11d[4][1]* *(v + idz) +
                                    d11d[4][2]* *(v1 + idz) +
                                    d11d[4][3]* *(v2 + idz) +
                                    d11d[4][4]* *(v3 + idz) +
                                    d11d[4][5]* *(v4 + idz) +
                                    d11d[4][6]* *(v5 + idz) +
                                    d11d[4][7]* *(v6 + idz) +
                                    d11d[4][8]* *(v7 + idz) +
                                    d11d[4][9]* *(v8 + idz) +
                                    d11d[4][10]* *(v9 + idz) +
                                    d11d[4][11]* *(v10 + idz));
            *(vf4 + idz) = xnu_n * (d11d[5][1]* *(v + idz) +
                                    d11d[5][2]* *(v1 + idz) +
                                    d11d[5][3]* *(v2 + idz) +
                                    d11d[5][4]* *(v3 + idz) +
                                    d11d[5][5]* *(v4 + idz) +
                                    d11d[5][6]* *(v5 + idz) +
                                    d11d[5][7]* *(v6 + idz) +
                                    d11d[5][8]* *(v7 + idz) +
                                    d11d[5][9]* *(v8 + idz) +
                                    d11d[5][10]* *(v9 + idz) +
                                    d11d[5][11]* *(v10 + idz));
        }
    }
}


void sf3d_ym(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(iymin);
    unsigned int ix, iz, idx, idz;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int mz = izmax - izmin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymax * nz + izmin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf - nz;
    double *restrict vf2 = vf1 - nz;
    double *restrict vf3 = vf2 - nz;
    double *restrict vf4 = vf3 - nz;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iz = 0; iz <= mz; iz++){
            idz = idx + iz;
            *(vf + idz) = xnu_0 * (d11d[1][1]* *(v + idz) +
                                   d11d[1][2]* *(v1 + idz) +
                                   d11d[1][3]* *(v2 + idz) +
                                   d11d[1][4]* *(v3 + idz));
            *(vf1 + idz) = xnu_n * (d11d[2][1]* *(v + idz) +
                                    d11d[2][2]* *(v1 + idz) +
                                    d11d[2][3]* *(v2 + idz) +
                                    d11d[2][4]* *(v3 + idz) +
                                    d11d[2][5]* *(v4 + idz) +
                                    d11d[2][6]* *(v5 + idz) +
                                    d11d[2][7]* *(v6 + idz));
            *(vf2 + idz) = xnu_n * (d11d[3][1]* *(v + idz) +
                                    d11d[3][2]* *(v1 + idz) +
                                    d11d[3][3]* *(v2 + idz) +
                                    d11d[3][4]* *(v3 + idz) +
                                    d11d[3][5]* *(v4 + idz) +
                                    d11d[3][6]* *(v5 + idz) +
                                    d11d[3][7]* *(v6 + idz) +
                                    d11d[3][8]* *(v7 + idz) +
                                    d11d[3][9]* *(v8 + idz) +
                                    d11d[3][10]* *(v9 + idz) +
                                    d11d[3][11]* *(v10 + idz));
            *(vf3 + idz) = xnu_n * (d11d[4][1]* *(v + idz) +
                                    d11d[4][2]* *(v1 + idz) +
                                    d11d[4][3]* *(v2 + idz) +
                                    d11d[4][4]* *(v3 + idz) +
                                    d11d[4][5]* *(v4 + idz) +
                                    d11d[4][6]* *(v5 + idz) +
                                    d11d[4][7]* *(v6 + idz) +
                                    d11d[4][8]* *(v7 + idz) +
                                    d11d[4][9]* *(v8 + idz) +
                                    d11d[4][10]* *(v9 + idz) +
                                    d11d[4][11]* *(v10 + idz));
            *(vf4 + idz) = xnu_n * (d11d[5][1]* *(v + idz) +
                                    d11d[5][2]* *(v1 + idz) +
                                    d11d[5][3]* *(v2 + idz) +
                                    d11d[5][4]* *(v3 + idz) +
                                    d11d[5][5]* *(v4 + idz) +
                                    d11d[5][6]* *(v5 + idz) +
                                    d11d[5][7]* *(v6 + idz) +
                                    d11d[5][8]* *(v7 + idz) +
                                    d11d[5][9]* *(v8 + idz) +
                                    d11d[5][10]* *(v9 + idz) +
                                    d11d[5][11]* *(v10 + idz));
        }
    }
}


void sf3d_zp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(izmax);
    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmin;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf + 1;
    double *restrict vf2 = vf1 + 1;
    double *restrict vf3 = vf2 + 1;
    double *restrict vf4 = vf3 + 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            *(vf + idy) = xnu_0 * (d11d[1][1]* *(v + idy) +
                                   d11d[1][2]* *(v1 + idy) +
                                   d11d[1][3]* *(v2 + idy) +
                                   d11d[1][4]* *(v3 + idy));
            *(vf1 + idy) = xnu_n * (d11d[2][1]* *(v + idy) +
                                    d11d[2][2]* *(v1 + idy) +
                                    d11d[2][3]* *(v2 + idy) +
                                    d11d[2][4]* *(v3 + idy) +
                                    d11d[2][5]* *(v4 + idy) +
                                    d11d[2][6]* *(v5 + idy) +
                                    d11d[2][7]* *(v6 + idy));
            *(vf2 + idy) = xnu_n * (d11d[3][1]* *(v + idy) +
                                    d11d[3][2]* *(v1 + idy) +
                                    d11d[3][3]* *(v2 + idy) +
                                    d11d[3][4]* *(v3 + idy) +
                                    d11d[3][5]* *(v4 + idy) +
                                    d11d[3][6]* *(v5 + idy) +
                                    d11d[3][7]* *(v6 + idy) +
                                    d11d[3][8]* *(v7 + idy) +
                                    d11d[3][9]* *(v8 + idy) +
                                    d11d[3][10]* *(v9 + idy) +
                                    d11d[3][11]* *(v10 + idy));
            *(vf3 + idy) = xnu_n * (d11d[4][1]* *(v + idy) +
                                    d11d[4][2]* *(v1 + idy) +
                                    d11d[4][3]* *(v2 + idy) +
                                    d11d[4][4]* *(v3 + idy) +
                                    d11d[4][5]* *(v4 + idy) +
                                    d11d[4][6]* *(v5 + idy) +
                                    d11d[4][7]* *(v6 + idy) +
                                    d11d[4][8]* *(v7 + idy) +
                                    d11d[4][9]* *(v8 + idy) +
                                    d11d[4][10]* *(v9 + idy) +
                                    d11d[4][11]* *(v10 + idy));
            *(vf4 + idy) = xnu_n * (d11d[5][1]* *(v + idy) +
                                    d11d[5][2]* *(v1 + idy) +
                                    d11d[5][3]* *(v2 + idy) +
                                    d11d[5][4]* *(v3 + idy) +
                                    d11d[5][5]* *(v4 + idy) +
                                    d11d[5][6]* *(v5 + idy) +
                                    d11d[5][7]* *(v6 + idy) +
                                    d11d[5][8]* *(v7 + idy) +
                                    d11d[5][9]* *(v8 + idy) +
                                    d11d[5][10]* *(v9 + idy) +
                                    d11d[5][11]* *(v10 + idy));
        }
    }
}


void sf3d_zm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads) {

    (void)(izmin);
    unsigned int ix, iy, idx, idy;
    const unsigned int mx = ixmax - ixmin;
    const unsigned int my = iymax - iymin;
    const unsigned int nynz = ny * nz;
    const unsigned int offset = ixmin * nynz + iymin * nz + izmax;

    v += offset;
    vf += offset;

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

    double *restrict vf1 = vf - 1;
    double *restrict vf2 = vf1 - 1;
    double *restrict vf3 = vf2 - 1;
    double *restrict vf4 = vf3 - 1;

    for (ix = 0; ix <= mx; ix++){
        idx = ix * nynz;

        for (iy = 0; iy <= my; iy++){
            idy = idx + iy * nz;
            *(vf + idy) = xnu_0 * (d11d[1][1]* *(v + idy) +
                                   d11d[1][2]* *(v1 + idy) +
                                   d11d[1][3]* *(v2 + idy) +
                                   d11d[1][4]* *(v3 + idy));
            *(vf1 + idy) = xnu_n * (d11d[2][1]* *(v + idy) +
                                    d11d[2][2]* *(v1 + idy) +
                                    d11d[2][3]* *(v2 + idy) +
                                    d11d[2][4]* *(v3 + idy) +
                                    d11d[2][5]* *(v4 + idy) +
                                    d11d[2][6]* *(v5 + idy) +
                                    d11d[2][7]* *(v6 + idy));
            *(vf2 + idy) = xnu_n * (d11d[3][1]* *(v + idy) +
                                    d11d[3][2]* *(v1 + idy) +
                                    d11d[3][3]* *(v2 + idy) +
                                    d11d[3][4]* *(v3 + idy) +
                                    d11d[3][5]* *(v4 + idy) +
                                    d11d[3][6]* *(v5 + idy) +
                                    d11d[3][7]* *(v6 + idy) +
                                    d11d[3][8]* *(v7 + idy) +
                                    d11d[3][9]* *(v8 + idy) +
                                    d11d[3][10]* *(v9 + idy) +
                                    d11d[3][11]* *(v10 + idy));
            *(vf3 + idy) = xnu_n * (d11d[4][1]* *(v + idy) +
                                    d11d[4][2]* *(v1 + idy) +
                                    d11d[4][3]* *(v2 + idy) +
                                    d11d[4][4]* *(v3 + idy) +
                                    d11d[4][5]* *(v4 + idy) +
                                    d11d[4][6]* *(v5 + idy) +
                                    d11d[4][7]* *(v6 + idy) +
                                    d11d[4][8]* *(v7 + idy) +
                                    d11d[4][9]* *(v8 + idy) +
                                    d11d[4][10]* *(v9 + idy) +
                                    d11d[4][11]* *(v10 + idy));
            *(vf4 + idy) = xnu_n * (d11d[5][1]* *(v + idy) +
                                    d11d[5][2]* *(v1 + idy) +
                                    d11d[5][3]* *(v2 + idy) +
                                    d11d[5][4]* *(v3 + idy) +
                                    d11d[5][5]* *(v4 + idy) +
                                    d11d[5][6]* *(v5 + idy) +
                                    d11d[5][7]* *(v6 + idy) +
                                    d11d[5][8]* *(v7 + idy) +
                                    d11d[5][9]* *(v8 + idy) +
                                    d11d[5][10]* *(v9 + idy) +
                                    d11d[5][11]* *(v10 + idy));
        }
    }
}