#include <stdio.h>
#include <omp.h>
#include <time.h>
#include <stdbool.h>
#include <unistd.h>  // sleep
#include "cobjects.h"
#include "cfields.h"
#include "ceulerianfluxes.h"
#include "kernels_diffadd.h"
#include "kernels_diffcpy.h"



////////////////////////////////////////////////////////////////////////////////
// 2d fluxes
////////////////////////////////////////////////////////////////////////////////

void static inline eflx2d_crt_s(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict re, const double *restrict p,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ee,
                                double *restrict F, double *restrict Fv, double *restrict Fe,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double invr, pre, rrv;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;

            invr = 1. / *(r + idy);
            pre = invr * (*(re + idy) + *(p + idy));
            rrv = *(rv + idy) * invr;

            *(E + idy) = *(ru + idy);
            *(Eu + idy) = *(ru + idy) * *(ru + idy) * invr + *(p + idy);
            *(Ev + idy) = *(ru + idy) * rrv;
            *(Ee + idy) = *(ru + idy) * pre;
            *(F + idy) = *(rv + idy);
            *(Fv + idy) = *(rv + idy) * rrv + *(p + idy);
            *(Fe + idy) = *(rv + idy) * pre;
        }
    }
}


void static inline eflx2d_crt_p(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict re, const double *restrict p,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ee,
                                double *restrict F, double *restrict Fv, double *restrict Fe,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax, const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double invr, pre, rrv;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, invr, pre, rrv)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                invr = 1. / *(r + idy);
                pre = invr * (*(re + idy) + *(p + idy));
                rrv = *(rv + idy) * invr;

                *(E + idy) = *(ru + idy);
                *(Eu + idy) = *(ru + idy) * *(ru + idy) * invr + *(p + idy);
                *(Ev + idy) = *(ru + idy) * rrv;
                *(Ee + idy) = *(ru + idy) * pre;
                *(F + idy) = *(rv + idy);
                *(Fv + idy) = *(rv + idy) * rrv + *(p + idy);
                *(Fe + idy) = *(rv + idy) * pre;
            }
        }
    }
}


void static inline eflx2d_crv_s(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict re, const double *restrict p, const double *restrict invJ,
                                const double *restrict dx_du, const double *restrict dy_du,
                                const double *restrict dx_dv, const double *restrict dy_dv,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ee,
                                double *restrict F, double *restrict Fu, double *restrict Fv, double *restrict Fe,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    double invr, pre, ru_pre, rv_pre, ruv, ruu, rvv;

    for (ix = ixmin; ix <= ixmax; ix++) {

        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {

            idy = idx + iy;
            invr = 1. / *(r + idy);
            pre = invr * (*(re + idy) + *(p + idy));
            ru_pre = *(ru + idy) * pre;
            rv_pre = *(rv + idy) * pre;
            ruv = invr * *(ru + idy) * *(rv + idy);
            ruu = invr * *(ru + idy) * *(ru + idy);
            rvv = invr * *(rv + idy) * *(rv + idy);

            *(E + idy) = (*(ru + idy) * *(dx_du + idy) + *(rv + idy) * *(dx_dv + idy)) * *(invJ + idy);
            *(F + idy) = (*(ru + idy) * *(dy_du + idy) + *(rv + idy) * *(dy_dv + idy)) * *(invJ + idy);

            *(Eu + idy) = (ruv * *(dx_dv + idy) + (ruu + *(p + idy)) * *(dx_du + idy)) * *(invJ + idy);
            *(Fu + idy) = (ruv * *(dy_dv + idy) + (ruu + *(p + idy)) * *(dy_du + idy)) * *(invJ + idy);

            *(Ev + idy) = (ruv * *(dx_du + idy) + (rvv + *(p + idy)) * *(dx_dv + idy)) * *(invJ + idy);
            *(Fv + idy) = (ruv * *(dy_du + idy) + (rvv + *(p + idy)) * *(dy_dv + idy)) * *(invJ + idy);

            *(Ee + idy) = (ru_pre * *(dx_du + idy) + rv_pre * *(dx_dv + idy)) * *(invJ + idy);
            *(Fe + idy) = (ru_pre * *(dy_du + idy) + rv_pre * *(dy_dv + idy)) * *(invJ + idy);
        }
    }
}


void static inline eflx2d_crv_p(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict re, const double *restrict p, const double *restrict invJ,
                                const double *restrict dx_du, const double *restrict dy_du,
                                const double *restrict dx_dv, const double *restrict dy_dv,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ee,
                                double *restrict F, double *restrict Fu, double *restrict Fv, double *restrict Fe,
                                const unsigned int ny,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    double invr, pre, ru_pre, rv_pre, ruv, ruu, rvv;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, \
                                       invr, pre, ru_pre, rv_pre, ruv, ruu, rvv)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {

            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {

                idy = idx + iy;

                invr = 1. / *(r + idy);
                pre = invr * (*(re + idy) + *(p + idy));
                ru_pre = *(ru + idy) * pre;
                rv_pre = *(rv + idy) * pre;
                ruv = invr * *(ru + idy) * *(rv + idy);
                ruu = invr * *(ru + idy) * *(ru + idy);
                rvv = invr * *(rv + idy) * *(rv + idy);

                *(E + idy) = (*(ru + idy) * *(dx_du + idy) + *(rv + idy) * *(dx_dv + idy)) * *(invJ + idy);
                *(F + idy) = (*(ru + idy) * *(dy_du + idy) + *(rv + idy) * *(dy_dv + idy)) * *(invJ + idy);

                *(Eu + idy) = (ruv * *(dx_dv + idy) + (ruu + *(p + idy)) * *(dx_du + idy)) * *(invJ + idy);
                *(Fu + idy) = (ruv * *(dy_dv + idy) + (ruu + *(p + idy)) * *(dy_du + idy)) * *(invJ + idy);

                *(Ev + idy) = (ruv * *(dx_du + idy) + (rvv + *(p + idy)) * *(dx_dv + idy)) * *(invJ + idy);
                *(Fv + idy) = (ruv * *(dy_du + idy) + (rvv + *(p + idy)) * *(dy_dv + idy)) * *(invJ + idy);

                *(Ee + idy) = (ru_pre * *(dx_du + idy) + rv_pre * *(dx_dv + idy)) * *(invJ + idy);
                *(Fe + idy) = (ru_pre * *(dy_du + idy) + rv_pre * *(dy_dv + idy)) * *(invJ + idy);
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d fluxes
////////////////////////////////////////////////////////////////////////////////


void static inline eflx3d_crt_s(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict rw, const double *restrict re, const double *restrict p,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ew, double *restrict Ee,
                                double *restrict F, double *restrict Fv, double *restrict Fw, double *restrict Fe,
                                double *restrict G, double *restrict Gw, double *restrict Ge,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr, pre, rrv, rrw;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                invr = 1. / *(r + idz);
                pre = invr * (*(re + idz) + *(p + idz));
                rrv = *(rv + idz) * invr;
                rrw = *(rw + idz) * invr;

                *(E + idz) = *(ru + idz);
                *(Eu + idz) = *(ru + idz) * *(ru + idz) * invr + *(p + idz);
                *(Ev + idz) = *(ru + idz) * rrv;
                *(Ew + idz) = *(ru + idz) * rrw;
                *(Ee + idz) = *(ru + idz) * pre;

                *(F + idz)  = *(rv + idz);
                /* *(Fu + idz) = *(Ev + idz)  */
                *(Fv + idz) = *(rv + idz) * rrv + *(p + idz);
                *(Fw + idz) = *(rv + idz) * rrw;
                *(Fe + idz) = *(rv + idz) * pre;

                *(G + idz) = *(rw + idz);
                /* *(Gu + idz) = *(Ew + idz) */
                /* *(Gv + idz) = *(Fw + idz) */
                *(Gw + idz) = *(rw + idz) * rrw + *(p + idz);
                *(Ge + idz) = *(rw + idz) * pre;

            }
        }
    }
}


void static inline eflx3d_crt_p(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict rw, const double *restrict re, const double *restrict p,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ew, double *restrict Ee,
                                double *restrict F, double *restrict Fv, double *restrict Fw, double *restrict Fe,
                                double *restrict G, double *restrict Gw, double *restrict Ge,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr, pre, rrv, rrw;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, \
                                                            invr, pre, rrv, rrw)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    invr = 1. / *(r + idz);
                    pre = invr * (*(re + idz) + *(p + idz));
                    rrv = *(rv + idz) * invr;
                    rrw = *(rw + idz) * invr;

                    *(E + idz) = *(ru + idz);
                    *(Eu + idz) = *(ru + idz) * *(ru + idz) * invr + *(p + idz);
                    *(Ev + idz) = *(ru + idz) * rrv;
                    *(Ew + idz) = *(ru + idz) * rrw;
                    *(Ee + idz) = *(ru + idz) * pre;

                    *(F + idz)  = *(rv + idz);
                    /* *(Fu + idz) = *(Ev + idz)  */
                    *(Fv + idz) = *(rv + idz) * rrv + *(p + idz);
                    *(Fw + idz) = *(rv + idz) * rrw;
                    *(Fe + idz) = *(rv + idz) * pre;

                    *(G + idz) = *(rw + idz);
                    /* *(Gu + idz) = *(Ew + idz) */
                    /* *(Gv + idz) = *(Fw + idz) */
                    *(Gw + idz) = *(rw + idz) * rrw + *(p + idz);
                    *(Ge + idz) = *(rw + idz) * pre;
                }
            }
        }
    }
}


void static inline eflx3d_crv_s(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict rw, const double *restrict re, const double *restrict p,
                                const double *restrict invJ,
                                const double *restrict dx_du, const double *restrict dy_du, const double *restrict dz_du,
                                const double *restrict dx_dv, const double *restrict dy_dv, const double *restrict dz_dv,
                                const double *restrict dx_dw, const double *restrict dy_dw, const double *restrict dz_dw,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ew, double *restrict Ee,
                                double *restrict F, double *restrict Fu, double *restrict Fv, double *restrict Fw, double *restrict Fe,
                                double *restrict G, double *restrict Gu, double *restrict Gv, double *restrict Gw, double *restrict Ge,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr, pre, ruu, rvv, rww, ruv, ruw, rvw, ru_pre, rv_pre, rw_pre;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                invr = 1. / *(r + idz);
                pre = invr * (*(re + idz) + *(p + idz));
                ru_pre = *(ru + idz) * pre;
                rv_pre = *(rv + idz) * pre;
                rw_pre = *(rw + idz) * pre;
                ruv = invr * *(ru + idz) * *(rv + idz);
                ruw = invr * *(ru + idz) * *(rw + idz);
                rvw = invr * *(rv + idz) * *(rw + idz);
                ruu = invr * *(ru + idz) * *(ru + idz) + *(p + idz);
                rvv = invr * *(rv + idz) * *(rv + idz) + *(p + idz);
                rww = invr * *(rw + idz) * *(rw + idz) + *(p + idz);

                *(E + idz) = (*(ru + idz) * *(dx_du + idz) +
                              *(rv + idz) * *(dx_dv + idz) +
                              *(rw + idz) * *(dx_dw + idz)) * *(invJ + idz);
                *(Eu + idz) = (ruu * *(dx_du + idz) +
                               ruv * *(dx_dv + idz) +
                               ruw * *(dx_dw + idz)) * *(invJ + idz);
                *(Ev + idz) = (ruv * *(dx_du + idz) +
                               rvv * *(dx_dv + idz) +
                               rvw * *(dx_dw + idz)) * *(invJ + idz);
                *(Ew + idz) = (ruw * *(dx_du + idz) +
                               rvw * *(dx_dv + idz) +
                               rww * *(dx_dw + idz)) * *(invJ + idz);
                *(Ee + idz) = (ru_pre * *(dx_du + idz) +
                               rv_pre * *(dx_dv + idz) +
                               rw_pre * *(dx_dw + idz)) * *(invJ + idz);

                *(F + idz) = (*(ru + idz) * *(dy_du + idz) +
                              *(rv + idz) * *(dy_dv + idz) +
                              *(rw + idz) * *(dy_dw + idz)) * *(invJ + idz);
                *(Fu + idz) = (ruu * *(dy_du + idz) +
                               ruv * *(dy_dv + idz) +
                               ruw * *(dy_dw + idz)) * *(invJ + idz);
                *(Fv + idz) = (ruv * *(dy_du + idz) +
                               rvv * *(dy_dv + idz) +
                               rvw * *(dy_dw + idz)) * *(invJ + idz);
                *(Fw + idz) = (ruw * *(dy_du + idz) +
                               rvw * *(dy_dv + idz) +
                               rww * *(dy_dw + idz)) * *(invJ + idz);
                *(Fe + idz) = (ru_pre * *(dy_du + idz) +
                               rv_pre * *(dy_dv + idz) +
                               rw_pre * *(dy_dw + idz)) * *(invJ + idz);

                *(G + idz) = (*(ru + idz) * *(dz_du + idz) +
                              *(rv + idz) * *(dz_dv + idz) +
                              *(rw + idz) * *(dz_dw + idz)) * *(invJ + idz);
                *(Gu + idz) = (ruu * *(dz_du + idz) +
                               ruv * *(dz_dv + idz) +
                               ruw * *(dz_dw + idz)) * *(invJ + idz);
                *(Gv + idz) = (ruv * *(dz_du + idz) +
                               rvv * *(dz_dv + idz) +
                               rvw * *(dz_dw + idz)) * *(invJ + idz);
                *(Gw + idz) = (ruw * *(dz_du + idz) +
                               rvw * *(dz_dv + idz) +
                               rww * *(dz_dw + idz)) * *(invJ + idz);
                *(Ge + idz) = (ru_pre * *(dz_du + idz) +
                               rv_pre * *(dz_dv + idz) +
                               rw_pre * *(dz_dw + idz)) * *(invJ + idz);
            }
        }
    }
}


void static inline eflx3d_crv_p(const double *restrict r, const double *restrict ru, const double *restrict rv,
                                const double *restrict rw, const double *restrict re, const double *restrict p,
                                const double *restrict invJ,
                                const double *restrict dx_du, const double *restrict dy_du, const double *restrict dz_du,
                                const double *restrict dx_dv, const double *restrict dy_dv, const double *restrict dz_dv,
                                const double *restrict dx_dw, const double *restrict dy_dw, const double *restrict dz_dw,
                                double *restrict E, double *restrict Eu, double *restrict Ev, double *restrict Ew, double *restrict Ee,
                                double *restrict F, double *restrict Fu, double *restrict Fv, double *restrict Fw, double *restrict Fe,
                                double *restrict G, double *restrict Gu, double *restrict Gv, double *restrict Gw, double *restrict Ge,
                                const unsigned int ny, const unsigned int nz,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int cpu){

    unsigned int ix, iy, iz, idx, idy, idz;
    unsigned int nynz = ny * nz;
    double invr, pre, ruu, rvv, rww, ruv, ruw, rvw, ru_pre, rv_pre, rw_pre;

    #pragma omp parallel num_threads(cpu) private(ix, iy, iz, idx, idy, idz, \
                invr, pre, ruu, rvv, rww, ruv, ruw, rvw, ru_pre, rv_pre, rw_pre)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    invr = 1. / *(r + idz);
                    pre = invr * (*(re + idz) + *(p + idz));

                    ruv = invr * *(ru + idz) * *(rv + idz);
                    ruw = invr * *(ru + idz) * *(rw + idz);
                    rvw = invr * *(rv + idz) * *(rw + idz);
                    ruu = invr * *(ru + idz) * *(ru + idz) + *(p + idz);
                    rvv = invr * *(rv + idz) * *(rv + idz) + *(p + idz);
                    rww = invr * *(rw + idz) * *(rw + idz) + *(p + idz);
                    ru_pre = *(ru + idz) * pre;
                    rv_pre = *(rv + idz) * pre;
                    rw_pre = *(rw + idz) * pre;

                    *(E + idz) = (*(ru + idz) * *(dx_du + idz) +
                                  *(rv + idz) * *(dx_dv + idz) +
                                  *(rw + idz) * *(dx_dw + idz)) * *(invJ + idz);
                    *(Eu + idz) = (ruu * *(dx_du + idz) +
                                   ruv * *(dx_dv + idz) +
                                   ruw * *(dx_dw + idz)) * *(invJ + idz);
                    *(Ev + idz) = (ruv * *(dx_du + idz) +
                                   rvv * *(dx_dv + idz) +
                                   rvw * *(dx_dw + idz)) * *(invJ + idz);
                    *(Ew + idz) = (ruw * *(dx_du + idz) +
                                   rvw * *(dx_dv + idz) +
                                   rww * *(dx_dw + idz)) * *(invJ + idz);
                    *(Ee + idz) = (ru_pre * *(dx_du + idz) +
                                   rv_pre * *(dx_dv + idz) +
                                   rw_pre * *(dx_dw + idz)) * *(invJ + idz);

                    *(F + idz) = (*(ru + idz) * *(dy_du + idz) +
                                  *(rv + idz) * *(dy_dv + idz) +
                                  *(rw + idz) * *(dy_dw + idz)) * *(invJ + idz);
                    *(Fu + idz) = (ruu * *(dy_du + idz) +
                                   ruv * *(dy_dv + idz) +
                                   ruw * *(dy_dw + idz)) * *(invJ + idz);
                    *(Fv + idz) = (ruv * *(dy_du + idz) +
                                   rvv * *(dy_dv + idz) +
                                   rvw * *(dy_dw + idz)) * *(invJ + idz);
                    *(Fw + idz) = (ruw * *(dy_du + idz) +
                                   rvw * *(dy_dv + idz) +
                                   rww * *(dy_dw + idz)) * *(invJ + idz);
                    *(Fe + idz) = (ru_pre * *(dy_du + idz) +
                                   rv_pre * *(dy_dv + idz) +
                                   rw_pre * *(dy_dw + idz)) * *(invJ + idz);

                    *(G + idz) = (*(ru + idz) * *(dz_du + idz) +
                                  *(rv + idz) * *(dz_dv + idz) +
                                  *(rw + idz) * *(dz_dw + idz)) * *(invJ + idz);
                    *(Gu + idz) = (ruu * *(dz_du + idz) +
                                   ruv * *(dz_dv + idz) +
                                   ruw * *(dz_dw + idz)) * *(invJ + idz);
                    *(Gv + idz) = (ruv * *(dz_du + idz) +
                                   rvv * *(dz_dv + idz) +
                                   rvw * *(dz_dw + idz)) * *(invJ + idz);
                    *(Gw + idz) = (ruw * *(dz_du + idz) +
                                   rvw * *(dz_dv + idz) +
                                   rww * *(dz_dw + idz)) * *(invJ + idz);
                    *(Ge + idz) = (ru_pre * *(dz_du + idz) +
                                   rv_pre * *(dz_dv + idz) +
                                   rw_pre * *(dz_dw + idz)) * *(invJ + idz);
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d eulerian fluxes Dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline eflx2d_crt_dispatcher(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            eflx2d_crt_s(fld->r, fld->ru, fld->rv, fld->re, fld->p,
                         fld->E, fld->Eu, fld->Ev, fld->Ee,
                         fld->F, fld->Fv, fld->Fe, fld->ny,
                         ixmin, ixmax, iymin, iymax);
            break;
        default:
            eflx2d_crt_p(fld->r, fld->ru, fld->rv, fld->re, fld->p,
                         fld->E, fld->Eu, fld->Ev, fld->Ee,
                         fld->F, fld->Fv, fld->Fe, fld->ny,
                         ixmin, ixmax, iymin, iymax, threads);
    }
}


void static inline eflx2d_crv_dispatcher(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            eflx2d_crv_s(fld->r, fld->ru, fld->rv, fld->re, fld->p,
                         fld->invJ, fld->dx_du, fld->dy_du, fld->dx_dv, fld->dy_dv,
                         fld->E, fld->Eu, fld->Ev, fld->Ee,
                         fld->F, fld->Fu, fld->Fv, fld->Fe,
                         fld->ny, ixmin, ixmax, iymin, iymax);
            break;
        default:
            eflx2d_crv_p(fld->r, fld->ru, fld->rv, fld->re, fld->p,
                         fld->invJ, fld->dx_du, fld->dy_du, fld->dx_dv, fld->dy_dv,
                         fld->E, fld->Eu, fld->Ev, fld->Ee,
                         fld->F, fld->Fu, fld->Fv, fld->Fe,
                         fld->ny, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static eflx2d_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx2d_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->eul_gtime = fmin(fld->eul_gtime, get_time(&start, &end));
}


void static eflx2d_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx2d_dispatcher(fld, &dmns[c], dmns[c].thread_info_eul.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_eul, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->eul_stime = fmin(fld->eul_stime, get_time(&start_loop, &end_loop));
}


void eulerian_fluxes2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->eul_call >= max_gcalls){
        eflx2d_func(fld);
    } else if (fld->eul_lock < fld->dmns_n){
        eflx2d_sing(fld);
    } else {
        eflx2d_glob(fld);
        fld->eul_call += 1;

        if (fld->eul_gtime > fld->eul_stime) {
            eflx2d_func = eflx2d_sing;
            fld->eul_glob = 0;
        } else {
            eflx2d_func = eflx2d_glob;
            fld->eul_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->eul_gtime > 1.5 * fld->eul_stime || fld->eul_stime > 1.5 * fld->eul_gtime) {
            fld->eul_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d eulerian fluxes Dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline eflx3d_crt_dispatcher(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            eflx3d_crt_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p,
                         fld->E, fld->Eu, fld->Ev, fld->Ew, fld->Ee,
                         fld->F, fld->Fv, fld->Fw, fld->Fe,
                         fld->G, fld->Gw, fld->Ge,
                         fld->ny, fld->nz,
                         ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            eflx3d_crt_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p,
                         fld->E, fld->Eu, fld->Ev, fld->Ew, fld->Ee,
                         fld->F, fld->Fv, fld->Fw, fld->Fe,
                         fld->G, fld->Gw, fld->Ge,
                         fld->ny, fld->nz,
                         ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static inline eflx3d_crv_dispatcher(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            eflx3d_crv_s(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p,
                         fld->invJ,
                         fld->dx_du, fld->dy_du, fld->dz_du,
                         fld->dx_dv, fld->dy_dv, fld->dz_dv,
                         fld->dx_dw, fld->dy_dw, fld->dz_dw,
                         fld->E, fld->Eu, fld->Ev, fld->Ew, fld->Ee,
                         fld->F, fld->Fu, fld->Fv, fld->Fw, fld->Fe,
                         fld->G, fld->Gu, fld->Gv, fld->Gw, fld->Ge,
                         fld->ny, fld->nz,
                         ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            eflx3d_crv_p(fld->r, fld->ru, fld->rv, fld->rw, fld->re, fld->p,
                         fld->invJ,
                         fld->dx_du, fld->dy_du, fld->dz_du,
                         fld->dx_dv, fld->dy_dv, fld->dz_dv,
                         fld->dx_dw, fld->dy_dw, fld->dz_dw,
                         fld->E, fld->Eu, fld->Ev, fld->Ew, fld->Ee,
                         fld->F, fld->Fu, fld->Fv, fld->Fw, fld->Fe,
                         fld->G, fld->Gu, fld->Gv, fld->Gw, fld->Ge,
                         fld->ny, fld->nz,
                         ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static eflx3d_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx3d_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->eul_gtime = fmin(fld->eul_gtime, get_time(&start, &end));
}


void static eflx3d_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx3d_dispatcher(fld, &dmns[c], dmns[c].thread_info_eul.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);

        set_thread_number(&dmns[c].thread_info_eul, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->eul_stime = fmin(fld->eul_stime, get_time(&start_loop, &end_loop));
}


void eulerian_fluxes3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->eul_call >= max_gcalls){
        eflx3d_func(fld);
    } else if (fld->eul_lock < fld->dmns_n){
        eflx3d_sing(fld);
    } else {
        eflx3d_glob(fld);
        fld->eul_call += 1;

        if (fld->eul_gtime > fld->eul_stime) {
            eflx3d_func = eflx3d_sing;
            fld->eul_glob = 0;
        } else {
            eflx3d_func = eflx3d_glob;
            fld->eul_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->eul_gtime > 1.5 * fld->eul_stime || fld->eul_stime > 1.5 * fld->eul_gtime) {
            fld->eul_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Euler derivatives (x)
////////////////////////////////////////////////////////////////////////////////

void static inline eflx2d_dux_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2cpy_xc_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2cpy_xc_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xc_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2cpy_xP_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2cpy_xP_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xP_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2cpy_xp_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2cpy_xp_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xp_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2cpy_xm_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2cpy_xm_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2cpy_xm_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static eflx2d_dux_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx2d_dux_dispatcher(fld, &dmns[c], dmns->thread_info_du.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_du, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->dux_stime = fmin(fld->dux_stime, get_time(&start_loop, &end_loop));
}


void static eflx2d_dux_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx2d_dux_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->dux_gtime = fmin(fld->dux_gtime, get_time(&start, &end));
}


void eulerian_derivatives2d_x(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->dux_call >= max_gcalls){
        eflx2d_dux_func(fld);
    } else if (fld->dux_lock < fld->dmns_n){
        eflx2d_dux_sing(fld);
    } else {
        eflx2d_dux_glob(fld);
        fld->dux_call += 1;

        if (fld->dux_gtime > fld->dux_stime) {
            eflx2d_dux_func = eflx2d_dux_sing;
            fld->dux_glob = 0;
        } else {
            eflx2d_dux_func = eflx2d_dux_glob;
            fld->dux_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->dux_gtime > 1.5 * fld->dux_stime || fld->dux_stime > 1.5 * fld->dux_gtime) {
            fld->dux_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d Euler derivative (y)
////////////////////////////////////////////////////////////////////////////////

void static inline eflx2d_duy_crt_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_yc_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_yc_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_yP_s(fld->r, fld->F, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->ru, fld->Ev, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->rv, fld->Fv, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->re, fld->Fe, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_yP_v(fld->r, fld->F, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->re, fld->Fe, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_yp_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_yp_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_ym_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_ym_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static inline eflx2d_duy_crv_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_yc_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_yc_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_yP_s(fld->r, fld->F, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->ru, fld->Fu, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->rv, fld->Fv, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->re, fld->Fe, *fld->odydtrk, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_yP_v(fld->r, fld->F, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->re, fld->Fe, fld->odydtrk_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_yp_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_yp_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_ym_s(fld->r, fld->F, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_ym_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static eflx2d_duy_sing(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx2d_duy_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_du, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->duy_stime = fmin(fld->duy_stime, get_time(&start_loop, &end_loop));
}


void static eflx2d_duy_glob(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx2d_duy_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->duy_gtime = fmin(fld->duy_gtime, get_time(&start, &end));
}


void eulerian_derivatives2d_y(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->duy_call >= max_gcalls){
        eflx2d_duy_func(fld);
    } else if (fld->duy_lock < fld->dmns_n){
        eflx2d_duy_sing(fld);
    } else {
        eflx2d_duy_glob(fld);
        fld->duy_call += 1;

        if (fld->duy_gtime > fld->duy_stime) {
            eflx2d_duy_func = eflx2d_duy_sing;
            fld->duy_glob = 0;
        } else {
            eflx2d_duy_func = eflx2d_duy_glob;
            fld->duy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->duy_gtime > 1.5 * fld->duy_stime || fld->duy_stime > 1.5 * fld->duy_gtime) {
            fld->duy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Euler derivatives (x)
////////////////////////////////////////////////////////////////////////////////

void static inline eflx3d_dux_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3cpy_xc_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_s(fld->rw, fld->Ew, fld->Kw, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3cpy_xc_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_v(fld->rw, fld->Ew, fld->Kw, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xc_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3cpy_xP_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_s(fld->rw, fld->Ew, fld->Kw, *fld->odxdtrk, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3cpy_xP_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_v(fld->rw, fld->Ew, fld->Kw, fld->odxdtrk_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xP_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3cpy_xp_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_s(fld->rw, fld->Ew, fld->Kw, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3cpy_xp_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_v(fld->rw, fld->Ew, fld->Kw, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xp_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3cpy_xm_s(fld->r, fld->E, fld->K, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_s(fld->ru, fld->Eu, fld->Ku, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_s(fld->rv, fld->Ev, fld->Kv, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_s(fld->rw, fld->Ew, fld->Kw, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_s(fld->re, fld->Ee, fld->Ke, *fld->odxdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3cpy_xm_v(fld->r, fld->E, fld->K, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_v(fld->ru, fld->Eu, fld->Ku, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_v(fld->rv, fld->Ev, fld->Kv, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_v(fld->rw, fld->Ew, fld->Kw, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3cpy_xm_v(fld->re, fld->Ee, fld->Ke, fld->odxdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static eflx3d_dux_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx3d_dux_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_du, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->dux_stime = fmin(fld->dux_stime, get_time(&start_loop, &end_loop));
}


void static eflx3d_dux_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx3d_dux_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->dux_gtime = fmin(fld->dux_gtime, get_time(&start, &end));
}


void eulerian_derivatives3d_x(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->dux_call >= max_gcalls){
        eflx3d_dux_func(fld);
    } else if (fld->dux_lock < fld->dmns_n){
        eflx3d_dux_sing(fld);
    } else {
        eflx3d_dux_glob(fld);
        fld->dux_call += 1;

        if (fld->dux_gtime > fld->dux_stime) {
            eflx3d_dux_func = eflx3d_dux_sing;
            fld->dux_glob = 0;
        } else {
            eflx3d_dux_func = eflx3d_dux_glob;
            fld->dux_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->dux_gtime > 1.5 * fld->dux_stime || fld->dux_stime > 1.5 * fld->dux_gtime) {
            fld->dux_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Euler derivative (y)
////////////////////////////////////////////////////////////////////////////////


void static inline eflx3d_duy_crt_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_yc_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_yc_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_yP_s(fld->r, fld->F, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->ru, fld->Ev, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rv, fld->Fv, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rw, fld->Fw, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->re, fld->Fe, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_yP_v(fld->r, fld->F, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->re, fld->Fe, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_yp_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_yp_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_ym_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->ru, fld->Ev, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_ym_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->ru, fld->Ev, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline eflx3d_duy_crv_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_yc_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_yc_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_yP_s(fld->r, fld->F, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->ru, fld->Fu, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rv, fld->Fv, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rw, fld->Fw, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->re, fld->Fe, *fld->odydtrk, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_yP_v(fld->r, fld->F, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->re, fld->Fe, fld->odydtrk_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_yp_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_yp_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_ym_s(fld->r, fld->F, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->ru, fld->Fu, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rv, fld->Fv, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rw, fld->Fw, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->re, fld->Fe, *fld->odydtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_ym_v(fld->r, fld->F, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->ru, fld->Fu, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rv, fld->Fv, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rw, fld->Fw, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->re, fld->Fe, fld->odydtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static eflx3d_duy_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx3d_duy_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_du, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->duy_stime = fmin(fld->duy_stime, get_time(&start_loop, &end_loop));
}


void static eflx3d_duy_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx3d_duy_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->duy_gtime = fmin(fld->duy_gtime, get_time(&start, &end));
}


void eulerian_derivatives3d_y(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->duy_call >= max_gcalls){
        eflx3d_duy_func(fld);
    } else if (fld->duy_lock < fld->dmns_n){
        eflx3d_duy_sing(fld);
    } else {
        eflx3d_duy_glob(fld);
        fld->duy_call += 1;

        if (fld->duy_gtime > fld->duy_stime) {
            eflx3d_duy_func = eflx3d_duy_sing;
            fld->duy_glob = 0;
        } else {
            eflx3d_duy_func = eflx3d_duy_glob;
            fld->duy_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->duy_gtime > 1.5 * fld->duy_stime || fld->duy_stime > 1.5 * fld->duy_gtime) {
            fld->duy_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d Euler derivative (z)
////////////////////////////////////////////////////////////////////////////////


void static inline eflx3d_duz_crt_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_zc_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->ru, fld->Ew, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rv, fld->Fw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_zc_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->ru, fld->Ew, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rv, fld->Fw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_zP_s(fld->r, fld->G, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->ru, fld->Ew, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rv, fld->Fw, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->re, fld->Ge, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_zP_v(fld->r, fld->G, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->ru, fld->Ew, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rv, fld->Fw, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_zp_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->ru, fld->Ew, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rv, fld->Fw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_zp_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->ru, fld->Ew, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rv, fld->Fw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_zm_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->ru, fld->Ew, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rv, fld->Fw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_zm_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->ru, fld->Ew, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rv, fld->Fw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline eflx3d_duz_crv_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_zc_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->ru, fld->Gu, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rv, fld->Gv, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_zc_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->ru, fld->Gu, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rv, fld->Gv, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_zP_s(fld->r, fld->G, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->ru, fld->Gu, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rv, fld->Gv, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->re, fld->Ge, *fld->odzdtrk, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_zP_v(fld->r, fld->G, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->ru, fld->Gu, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rv, fld->Gv, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_zp_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->ru, fld->Gu, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rv, fld->Gv, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_zp_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->ru, fld->Gu, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rv, fld->Gv, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_zm_s(fld->r, fld->G, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->ru, fld->Gu, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rv, fld->Gv, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rw, fld->Gw, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->re, fld->Ge, *fld->odzdtrk, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_zm_v(fld->r, fld->G, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->ru, fld->Gu, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rv, fld->Gv, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rw, fld->Gw, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->re, fld->Ge, fld->odzdtrk_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static eflx3d_duz_sing(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        eflx3d_duz_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_du, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->duz_stime = fmin(fld->duz_stime, get_time(&start_loop, &end_loop));
}


void static eflx3d_duz_glob(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            eflx3d_duz_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->duz_gtime = fmin(fld->duz_gtime, get_time(&start, &end));
}


void eulerian_derivatives3d_z(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->duz_call >= max_gcalls){
        eflx3d_duz_func(fld);
    } else if (fld->duz_lock < fld->dmns_n){
        eflx3d_duz_sing(fld);
    } else {
        eflx3d_duz_glob(fld);
        fld->duz_call += 1;

        if (fld->duz_gtime > fld->duz_stime) {
            eflx3d_duz_func = eflx3d_duz_sing;
            fld->duz_glob = 0;
        } else {
            eflx3d_duz_func = eflx3d_duz_glob;
            fld->duz_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->duz_gtime > 1.5 * fld->duz_stime || fld->duz_stime > 1.5 * fld->duz_gtime) {
            fld->duz_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// Set pointers
////////////////////////////////////////////////////////////////////////////////


void eulerian_fluxes2d_init(fields2d * fld) {

    if (fld->crv == 1) {
        eflx2d_dispatcher = eflx2d_crv_dispatcher;
        eflx2d_duy_dispatcher = eflx2d_duy_crv_dispatcher;
    } else {
        eflx2d_dispatcher = eflx2d_crt_dispatcher;
        eflx2d_duy_dispatcher = eflx2d_duy_crt_dispatcher;
    }
}


void eulerian_fluxes3d_init(fields3d * fld) {

    if (fld->crv == 1) {
        eflx3d_dispatcher = eflx3d_crv_dispatcher;
        eflx3d_duy_dispatcher = eflx3d_duy_crv_dispatcher;
        eflx3d_duz_dispatcher = eflx3d_duz_crv_dispatcher;
    } else {
        eflx3d_dispatcher = eflx3d_crt_dispatcher;
        eflx3d_duy_dispatcher = eflx3d_duy_crt_dispatcher;
        eflx3d_duz_dispatcher = eflx3d_duz_crt_dispatcher;
    }
}

