#include <stdio.h>
#include <omp.h>
#include <time.h>
#include <math.h>
#include "cfields.h"
#include "cviscousfluxes.h"
#include "kernels_diffraw.h"
#include "kernels_diffadd.h"

////////////////////////////////////////////////////////////////////////////////
// 2d viscous fluxes computation
////////////////////////////////////////////////////////////////////////////////


void static inline vflx_crt2d_s(fields2d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    unsigned int ny = fld->ny;
    double mu0 = fld->mu0;
    double cppr = fld->cppr;
    double Ssu = fld->Ssu;
    double Tref = fld->Tref;
    double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict Eu = fld->Eu;
    const double *restrict Ev = fld->Ev;
    const double *restrict F = fld->F;
    const double *restrict Fu = fld->Fu;
    const double *restrict Fv = fld->Fv;
    double *restrict Ee = fld->Ee;
    double *restrict Fe = fld->Fe;
    double *restrict tau11 = fld->tau11;
    double *restrict tau12 = fld->tau12;
    double *restrict tau22 = fld->tau22;
    double T, mu, mucppr, Stot;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            T = Tk[idy] / Tref;
            mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idy] + Ssu);
            Stot = (Eu[idy] + Fv[idy]) / 3.;
            tau11[idy] = 2 * mu * (Eu[idy] - Stot);
            tau22[idy] = 2 * mu * (Fv[idy] - Stot);
            tau12[idy] = mu * (Ev[idy] + Fu[idy]);

            // (Qu, Qv) = (Ee, Fe)
            mucppr = mu * cppr;
            Ee[idy] = E[idy] * tau11[idy] + F[idy] * tau12[idy] + mucppr * Ee[idy];
            Fe[idy] = E[idy] * tau12[idy] + F[idy] * tau22[idy] + mucppr * Fe[idy];
        }
    }
}


void static inline vflx_crt2d_p(fields2d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    unsigned int ny = fld->ny;
    double mu0 = fld->mu0;
    double cppr = fld->cppr;
    double Ssu = fld->Ssu;
    double Tref = fld->Tref;
    double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict Eu = fld->Eu;
    const double *restrict Ev = fld->Ev;
    const double *restrict F = fld->F;
    const double *restrict Fu = fld->Fu;
    const double *restrict Fv = fld->Fv;
    double *restrict Ee = fld->Ee;
    double *restrict Fe = fld->Fe;
    double *restrict tau11 = fld->tau11;
    double *restrict tau12 = fld->tau12;
    double *restrict tau22 = fld->tau22;
    double T, mu, mucppr, Stot;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, \
                                                            T, mu, mucppr, Stot)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                T = Tk[idy] / Tref;
                mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idy] + Ssu);
                Stot = (Eu[idy] + Fv[idy]) / 3.;
                tau11[idy] = 2 * mu * (Eu[idy] - Stot);
                tau22[idy] = 2 * mu * (Fv[idy] - Stot);
                tau12[idy] = mu * (Ev[idy] + Fu[idy]);

                // (Qu, Qv) = (Ee, Fe)
                mucppr = mu * cppr;
                Ee[idy] = E[idy] * tau11[idy] + F[idy] * tau12[idy] + mucppr * Ee[idy];
                Fe[idy] = E[idy] * tau12[idy] + F[idy] * tau22[idy] + mucppr * Fe[idy];
            }
        }
    }
}


void static inline vflx_crv2d_s(fields2d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax){

    unsigned int ix, iy, idx, idy;
    unsigned int ny = fld->ny;
    double mu0 = fld->mu0;
    double cppr = fld->cppr;
    double Ssu = fld->Ssu;
    double Tref = fld->Tref;
    double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict dx_du = fld->dx_du;
    const double *restrict dx_dv = fld->dx_dv;
    const double *restrict dy_du = fld->dy_du;
    const double *restrict dy_dv = fld->dy_dv;
    const double *restrict invJ = fld->invJ;
    double *restrict E = fld->E;
    double *restrict Eu = fld->Eu;
    double *restrict Ev = fld->Ev;
    double *restrict F = fld->F;
    double *restrict Fu = fld->Fu;
    double *restrict Fv = fld->Fv;
    double *restrict Ee = fld->Ee;
    double *restrict Fe = fld->Fe;
    double *restrict tau11 = fld->tau11;
    double *restrict tau12 = fld->tau12;
    double *restrict tau22 = fld->tau22;
    double T, mu, mu23, mucppr, tx, ty, Ee_s, Fe_s;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * ny;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy;
            T = Tk[idy] / Tref;
            mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idy] + Ssu);
            mu23 = 2 * mu / 3.;
            mucppr = mu * cppr;

            // Viscous stresses
            tx = Eu[idy] * dx_du[idy] + Ev[idy] * dy_du[idy];
            ty = Fu[idy] * dx_dv[idy] + Fv[idy] * dy_dv[idy];

            tau11[idy] = mu23 * (2 * tx - ty);
            tau22[idy] = mu23 * (2 * ty - tx);
            tau12[idy] = mu * (Eu[idy] * dx_dv[idy] +
                               Ev[idy] * dy_dv[idy] +
                               Fu[idy] * dx_du[idy] +
                               Fv[idy] * dy_du[idy]);
            // Heat Fluxes
            Ee[idy] = mucppr * (Ee[idy] * dx_du[idy] + Fe[idy] * dy_du[idy]);
            Fe[idy] = mucppr * (Ee[idy] * dx_dv[idy] + Fe[idy] * dy_dv[idy]);

            // Thermo-viscous fluxes
            Eu[idy] = (tau11[idy] * dx_du[idy] + tau12[idy] * dx_dv[idy]) * invJ[idy];
            Fu[idy] = (tau11[idy] * dy_du[idy] + tau12[idy] * dy_dv[idy]) * invJ[idy];
            Ev[idy] = (tau12[idy] * dx_du[idy] + tau22[idy] * dx_dv[idy]) * invJ[idy];
            Fv[idy] = (tau12[idy] * dy_du[idy] + tau22[idy] * dy_dv[idy]) * invJ[idy];

            Ee_s = (E[idy] * tau11[idy] + F[idy] * tau12[idy] + Ee[idy]);
            Fe_s = (E[idy] * tau12[idy] + F[idy] * tau22[idy] + Fe[idy]);

            Ee[idy] = (Ee_s * dx_du[idy] + Fe_s * dx_dv[idy]) * invJ[idy];
            Fe[idy] = (Ee_s * dy_du[idy] + Fe_s * dy_dv[idy]) * invJ[idy];
        }
    }
}


void static inline vflx_crv2d_p(fields2d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int threads){

    unsigned int ix, iy, idx, idy;
    unsigned int ny = fld->ny;
    double mu0 = fld->mu0;
    double cppr = fld->cppr;
    double Ssu = fld->Ssu;
    double Tref = fld->Tref;
    double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict dx_du = fld->dx_du;
    const double *restrict dx_dv = fld->dx_dv;
    const double *restrict dy_du = fld->dy_du;
    const double *restrict dy_dv = fld->dy_dv;
    const double *restrict invJ = fld->invJ;
    double *restrict E = fld->E;
    double *restrict Eu = fld->Eu;
    double *restrict Ev = fld->Ev;
    double *restrict F = fld->F;
    double *restrict Fu = fld->Fu;
    double *restrict Fv = fld->Fv;
    double *restrict Ee = fld->Ee;
    double *restrict Fe = fld->Fe;
    double *restrict tau11 = fld->tau11;
    double *restrict tau12 = fld->tau12;
    double *restrict tau22 = fld->tau22;
    double T, mu, mu23, mucppr, tx, ty, Ee_s, Fe_s;

    #pragma omp parallel num_threads(threads) private(ix, iy, idx, idy, \
                                        T, mu, mu23, mucppr, tx, ty, Ee_s, Fe_s)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * ny;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy;
                T = Tk[idy] / Tref;
                mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idy] + Ssu);
                mu23 = 2 * mu / 3.;
                mucppr = mu * cppr;

                // Viscous stresses
                tx = Eu[idy] * dx_du[idy] + Ev[idy] * dy_du[idy];
                ty = Fu[idy] * dx_dv[idy] + Fv[idy] * dy_dv[idy];

                tau11[idy] = mu23 * (2 * tx - ty);
                tau22[idy] = mu23 * (2 * ty - tx);
                tau12[idy] = mu * (Eu[idy] * dx_dv[idy] +
                                   Ev[idy] * dy_dv[idy] +
                                   Fu[idy] * dx_du[idy] +
                                   Fv[idy] * dy_du[idy]);
                // Heat Fluxes
                Ee[idy] = mucppr * (Ee[idy] * dx_du[idy] + Fe[idy] * dy_du[idy]);
                Fe[idy] = mucppr * (Ee[idy] * dx_dv[idy] + Fe[idy] * dy_dv[idy]);

                // Thermo-viscous fluxes
                Eu[idy] = (tau11[idy] * dx_du[idy] + tau12[idy] * dx_dv[idy]) * invJ[idy];
                Fu[idy] = (tau11[idy] * dy_du[idy] + tau12[idy] * dy_dv[idy]) * invJ[idy];
                Ev[idy] = (tau12[idy] * dx_du[idy] + tau22[idy] * dx_dv[idy]) * invJ[idy];
                Fv[idy] = (tau12[idy] * dy_du[idy] + tau22[idy] * dy_dv[idy]) * invJ[idy];

                Ee_s = (E[idy] * tau11[idy] + F[idy] * tau12[idy] + Ee[idy]);
                Fe_s = (E[idy] * tau12[idy] + F[idy] * tau22[idy] + Fe[idy]);

                Ee[idy] = (Ee_s * dx_du[idy] + Fe_s * dx_dv[idy]) * invJ[idy];
                Fe[idy] = (Ee_s * dy_du[idy] + Fe_s * dy_dv[idy]) * invJ[idy];
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d viscous fluxes computation
////////////////////////////////////////////////////////////////////////////////


void static inline vflx_crt3d_s(fields3d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int ny = fld->ny;
    const unsigned int nz = fld->nz;
    const unsigned int nynz = ny * nz;
    const double mu0 = fld->mu0;
    const double cppr = fld->cppr;
    const double Ssu = fld->Ssu;
    const double Tref = fld->Tref;
    const double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict Eu = fld->Eu;
    const double *restrict Ev = fld->Ev;
    const double *restrict Ew = fld->Ew;
    const double *restrict F = fld->F;
    const double *restrict Fu = fld->Fu;
    const double *restrict Fv = fld->Fv;
    const double *restrict Fw = fld->Fw;
    const double *restrict G = fld->G;
    const double *restrict Gu = fld->Gu;
    const double *restrict Gv = fld->Gv;
    const double *restrict Gw = fld->Gw;
    double * Ee = fld->Ee;
    double * Fe = fld->Fe;
    double * Ge = fld->Ge;
    double *restrict tau11 = fld->tau11;
    double *restrict tau22 = fld->tau22;
    double *restrict tau33 = fld->tau33;
    double *restrict tau12 = fld->tau12;
    double *restrict tau13 = fld->tau13;
    double *restrict tau23 = fld->tau23;
    double T, mu, mucppr, Stot;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;
                T = Tk[idz] / Tref;
                mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idz] + Ssu);

                Stot = (Eu[idz] + Fv[idz] + Gw[idz]) / 3.;
                tau11[idz] = 2 * mu * (Eu[idz] - Stot);
                tau22[idz] = 2 * mu * (Fv[idz] - Stot);
                tau33[idz] = 2 * mu * (Gw[idz] - Stot);
                tau12[idz] = mu * (Ev[idz] + Fu[idz]);
                tau13[idz] = mu * (Ew[idz] + Gu[idz]);
                tau23[idz] = mu * (Fw[idz] + Gv[idz]);

                // (Qu, Qv, Qw) = (Ee, Fe, Ge)
                mucppr = mu * cppr;
                Ee[idz] = E[idz] * tau11[idz] + \
                          F[idz] * tau12[idz] + \
                          G[idz] * tau13[idz] + \
                          mucppr * Ee[idz];
                Fe[idz] = E[idz] * tau12[idz] + \
                          F[idz] * tau22[idz] + \
                          G[idz] * tau23[idz] + \
                          mucppr * Fe[idz];
                Ge[idz] = E[idz] * tau13[idz] + \
                          F[idz] * tau23[idz] + \
                          G[idz] * tau33[idz] + \
                          mucppr * Ge[idz];
            }
        }
    }
}


void static inline vflx_crt3d_p(fields3d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int ny = fld->ny;
    const unsigned int nz = fld->nz;
    const unsigned int nynz = ny * nz;
    const double mu0 = fld->mu0;
    const double cppr = fld->cppr;
    const double Ssu = fld->Ssu;
    const double Tref = fld->Tref;
    const double SsuTref = fld->SsuTref;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict Eu = fld->Eu;
    const double *restrict Ev = fld->Ev;
    const double *restrict Ew = fld->Ew;
    const double *restrict F = fld->F;
    const double *restrict Fu = fld->Fu;
    const double *restrict Fv = fld->Fv;
    const double *restrict Fw = fld->Fw;
    const double *restrict G = fld->G;
    const double *restrict Gu = fld->Gu;
    const double *restrict Gv = fld->Gv;
    const double *restrict Gw = fld->Gw;
    double * Ee = fld->Ee;
    double * Fe = fld->Fe;
    double * Ge = fld->Ge;
    double *restrict tau11 = fld->tau11;
    double *restrict tau22 = fld->tau22;
    double *restrict tau33 = fld->tau33;
    double *restrict tau12 = fld->tau12;
    double *restrict tau13 = fld->tau13;
    double *restrict tau23 = fld->tau23;
    double T, mu, mucppr, Stot;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, \
                                                            T, mu, mucppr, Stot)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;
                    T = Tk[idz] / Tref;
                    mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idz] + Ssu);

                    Stot = (Eu[idz] + Fv[idz] + Gw[idz]) / 3.;
                    tau11[idz] = 2 * mu * (Eu[idz] - Stot);
                    tau22[idz] = 2 * mu * (Fv[idz] - Stot);
                    tau33[idz] = 2 * mu * (Gw[idz] - Stot);
                    tau12[idz] = mu * (Ev[idz] + Fu[idz]);
                    tau13[idz] = mu * (Ew[idz] + Gu[idz]);
                    tau23[idz] = mu * (Fw[idz] + Gv[idz]);

                    // (Qu, Qv, Qw) = (Ee, Fe, Ge)
                    mucppr = mu * cppr;
                    Ee[idz] = E[idz] * tau11[idz] + \
                              F[idz] * tau12[idz] + \
                              G[idz] * tau13[idz] + \
                              mucppr * Ee[idz];
                    Fe[idz] = E[idz] * tau12[idz] + \
                              F[idz] * tau22[idz] + \
                              G[idz] * tau23[idz] + \
                              mucppr * Fe[idz];
                    Ge[idz] = E[idz] * tau13[idz] + \
                              F[idz] * tau23[idz] + \
                              G[idz] * tau33[idz] + \
                              mucppr * Ge[idz];
                }
            }
        }
    }
}


void static inline vflx_crv3d_s(fields3d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax){


    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int ny = fld->ny;
    const unsigned int nz = fld->nz;
    const unsigned int nynz = ny * nz;
    const double mu0 = fld->mu0;
    const double cppr = fld->cppr;
    const double Ssu = fld->Ssu;
    const double Tref = fld->Tref;
    const double SsuTref = fld->SsuTref;
    const double *restrict dx_du = fld->dx_du;
    const double *restrict dx_dv = fld->dx_dv;
    const double *restrict dx_dw = fld->dx_dw;
    const double *restrict dy_du = fld->dy_du;
    const double *restrict dy_dv = fld->dy_dv;
    const double *restrict dy_dw = fld->dy_dw;
    const double *restrict dz_du = fld->dz_du;
    const double *restrict dz_dv = fld->dz_dv;
    const double *restrict dz_dw = fld->dz_dw;
    const double *restrict invJ = fld->invJ;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict F = fld->F;
    const double *restrict G = fld->G;
    double *restrict Eu = fld->Eu;
    double *restrict Ev = fld->Ev;
    double *restrict Ew = fld->Ew;
    double * Ee = fld->Ee;
    double *restrict Fu = fld->Fu;
    double *restrict Fv = fld->Fv;
    double *restrict Fw = fld->Fw;
    double * Fe = fld->Fe;
    double *restrict Gu = fld->Gu;
    double *restrict Gv = fld->Gv;
    double *restrict Gw = fld->Gw;
    double * Ge = fld->Ge;
    double *restrict tau11 = fld->tau11;
    double *restrict tau22 = fld->tau22;
    double *restrict tau33 = fld->tau33;
    double *restrict tau12 = fld->tau12;
    double *restrict tau13 = fld->tau13;
    double *restrict tau23 = fld->tau23;
    double T, mu, mu23, mucppr, tx, ty, tz, Ee_s, Fe_s, Ge_s;

    for (ix = ixmin; ix <= ixmax; ix++) {
        idx = ix * nynz;

        for (iy = iymin; iy <= iymax; iy++) {
            idy = idx + iy * nz;

            for (iz = izmin; iz <= izmax; iz++) {
                idz = idy + iz;

                T = Tk[idz] / Tref;
                mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idz] + Ssu);
                mu23 = 2 * mu / 3.;
                mucppr = mu * cppr;

                // Viscous stresses
                tx = (Eu[idz] * dx_du[idz] + Ev[idz] * dy_du[idz] + Ew[idz] * dz_du[idz]);
                ty = (Fu[idz] * dx_dv[idz] + Fv[idz] * dy_dv[idz] + Fw[idz] * dz_dv[idz]);
                tz = (Gu[idz] * dx_dw[idz] + Gv[idz] * dy_dw[idz] + Gw[idz] * dz_dw[idz]);

                tau11[idz] = mu23 * (2 * tx - ty - tz);
                tau22[idz] = mu23 * (2 * ty - tx - tz);
                tau33[idz] = mu23 * (2 * tz - tx - ty);
                tau12[idz] = mu * (Eu[idz] * dx_dv[idz] +
                                   Ev[idz] * dy_dv[idz] +
                                   Ew[idz] * dz_dv[idz] +
                                   Fu[idz] * dx_du[idz] +
                                   Fv[idz] * dy_du[idz] +
                                   Fw[idz] * dz_du[idz]);
                tau13[idz] = mu * (Eu[idz] * dx_dw[idz] +
                                   Ev[idz] * dy_dw[idz] +
                                   Ew[idz] * dz_dw[idz] +
                                   Gu[idz] * dx_du[idz] +
                                   Gv[idz] * dy_du[idz] +
                                   Gw[idz] * dz_du[idz]);
                tau23[idz] = mu * (Fu[idz] * dx_dw[idz] +
                                   Fv[idz] * dy_dw[idz] +
                                   Fw[idz] * dz_dw[idz] +
                                   Gu[idz] * dx_dv[idz] +
                                   Gv[idz] * dy_dv[idz] +
                                   Gw[idz] * dz_dv[idz]);
                // Heat Fluxes
                Ee[idz] = mucppr * (Ee[idz] * dx_du[idz] +
                                    Fe[idz] * dy_du[idz] +
                                    Ge[idz] * dz_du[idz]);
                Fe[idz] = mucppr * (Ee[idz] * dx_dv[idz] +
                                    Fe[idz] * dy_dv[idz] +
                                    Ge[idz] * dz_dv[idz]);
                Ge[idz] = mucppr * (Ee[idz] * dx_dw[idz] +
                                    Fe[idz] * dy_dw[idz] +
                                    Ge[idz] * dz_dw[idz]);

                // Thermo-viscous Fluxes
                Eu[idz] = (tau11[idz] * dx_du[idz] +
                           tau12[idz] * dx_dv[idz] +
                           tau13[idz] * dx_dw[idz]) * invJ[idz];
                Fu[idz] = (tau11[idz] * dy_du[idz] +
                           tau12[idz] * dy_dv[idz] +
                           tau13[idz] * dy_dw[idz]) * invJ[idz];
                Gu[idz] = (tau11[idz] * dz_du[idz] +
                           tau12[idz] * dz_dv[idz] +
                           tau13[idz] * dz_dw[idz]) * invJ[idz];

                Ev[idz] = (tau12[idz] * dx_du[idz] +
                           tau22[idz] * dx_dv[idz] +
                           tau23[idz] * dx_dw[idz]) * invJ[idz];
                Fv[idz] = (tau12[idz] * dy_du[idz] +
                           tau22[idz] * dy_dv[idz] +
                           tau23[idz] * dy_dw[idz]) * invJ[idz];
                Gv[idz] = (tau12[idz] * dz_du[idz] +
                           tau22[idz] * dz_dv[idz] +
                           tau23[idz] * dz_dw[idz]) * invJ[idz];

                Ew[idz] = (tau13[idz] * dx_du[idz] +
                           tau23[idz] * dx_dv[idz] +
                           tau33[idz] * dx_dw[idz]) * invJ[idz];
                Fw[idz] = (tau13[idz] * dy_du[idz] +
                           tau23[idz] * dy_dv[idz] +
                           tau33[idz] * dy_dw[idz]) * invJ[idz];
                Gw[idz] = (tau13[idz] * dz_du[idz] +
                           tau23[idz] * dz_dv[idz] +
                           tau33[idz] * dz_dw[idz]) * invJ[idz];

                Ee_s = (E[idz] * tau11[idz] + F[idz] * tau12[idz] +
                        G[idz] * tau13[idz] + Ee[idz]);
                Fe_s = (E[idz] * tau12[idz] + F[idz] * tau22[idz] +
                        G[idz] * tau23[idz] + Fe[idz]);
                Ge_s = (E[idz] * tau13[idz] + F[idz] * tau23[idz] +
                        G[idz] * tau33[idz] + Ge[idz]);

                Ee[idz] = (Ee_s * dx_du[idz] + Fe_s * dx_dv[idz] + Ge_s * dx_dw[idz]) * invJ[idz];
                Fe[idz] = (Ee_s * dy_du[idz] + Fe_s * dy_dv[idz] + Ge_s * dy_dw[idz]) * invJ[idz];
                Ge[idz] = (Ee_s * dz_du[idz] + Fe_s * dz_dv[idz] + Ge_s * dz_dw[idz]) * invJ[idz];
            }
        }
    }
}


void static inline vflx_crv3d_p(fields3d *fld,
                                const unsigned int ixmin, const unsigned int ixmax,
                                const unsigned int iymin, const unsigned int iymax,
                                const unsigned int izmin, const unsigned int izmax,
                                const unsigned int threads){

    unsigned int ix, iy, iz, idx, idy, idz;
    const unsigned int ny = fld->ny;
    const unsigned int nz = fld->nz;
    const unsigned int nynz = ny * nz;
    const double mu0 = fld->mu0;
    const double cppr = fld->cppr;
    const double Ssu = fld->Ssu;
    const double Tref = fld->Tref;
    const double SsuTref = fld->SsuTref;
    const double *restrict dx_du = fld->dx_du;
    const double *restrict dx_dv = fld->dx_dv;
    const double *restrict dx_dw = fld->dx_dw;
    const double *restrict dy_du = fld->dy_du;
    const double *restrict dy_dv = fld->dy_dv;
    const double *restrict dy_dw = fld->dy_dw;
    const double *restrict dz_du = fld->dz_du;
    const double *restrict dz_dv = fld->dz_dv;
    const double *restrict dz_dw = fld->dz_dw;
    const double *restrict invJ = fld->invJ;
    const double *restrict Tk = fld->Tk;
    const double *restrict E = fld->E;
    const double *restrict F = fld->F;
    const double *restrict G = fld->G;
    double *restrict Eu = fld->Eu;
    double *restrict Ev = fld->Ev;
    double *restrict Ew = fld->Ew;
    double * Ee = fld->Ee;
    double *restrict Fu = fld->Fu;
    double *restrict Fv = fld->Fv;
    double *restrict Fw = fld->Fw;
    double * Fe = fld->Fe;
    double *restrict Gu = fld->Gu;
    double *restrict Gv = fld->Gv;
    double *restrict Gw = fld->Gw;
    double * Ge = fld->Ge;
    double *restrict tau11 = fld->tau11;
    double *restrict tau22 = fld->tau22;
    double *restrict tau33 = fld->tau33;
    double *restrict tau12 = fld->tau12;
    double *restrict tau13 = fld->tau13;
    double *restrict tau23 = fld->tau23;
    double T, mu, mu23, mucppr, tx, ty, tz, Ee_s, Fe_s, Ge_s;

    #pragma omp parallel num_threads(threads) private(ix, iy, iz, idx, idy, idz, \
                                T, mu, mu23, mucppr, tx, ty, tz, Ee_s, Fe_s, Ge_s)
    {
        #pragma omp for nowait
        for (ix = ixmin; ix <= ixmax; ix++) {
            idx = ix * nynz;

            for (iy = iymin; iy <= iymax; iy++) {
                idy = idx + iy * nz;

                for (iz = izmin; iz <= izmax; iz++) {
                    idz = idy + iz;

                    T = Tk[idz] / Tref;
                    mu = mu0 * T * sqrt(T) * SsuTref / (Tk[idz] + Ssu);
                    mu23 = 2 * mu / 3.;
                    mucppr = mu * cppr;

                    // Viscous stresses
                    tx = (Eu[idz] * dx_du[idz] + Ev[idz] * dy_du[idz] + Ew[idz] * dz_du[idz]);
                    ty = (Fu[idz] * dx_dv[idz] + Fv[idz] * dy_dv[idz] + Fw[idz] * dz_dv[idz]);
                    tz = (Gu[idz] * dx_dw[idz] + Gv[idz] * dy_dw[idz] + Gw[idz] * dz_dw[idz]);

                    tau11[idz] = mu23 * (2 * tx - ty - tz);
                    tau22[idz] = mu23 * (2 * ty - tx - tz);
                    tau33[idz] = mu23 * (2 * tz - tx - ty);
                    tau12[idz] = mu * (Eu[idz] * dx_dv[idz] +
                                       Ev[idz] * dy_dv[idz] +
                                       Ew[idz] * dz_dv[idz] +
                                       Fu[idz] * dx_du[idz] +
                                       Fv[idz] * dy_du[idz] +
                                       Fw[idz] * dz_du[idz]);
                    tau13[idz] = mu * (Eu[idz] * dx_dw[idz] +
                                       Ev[idz] * dy_dw[idz] +
                                       Ew[idz] * dz_dw[idz] +
                                       Gu[idz] * dx_du[idz] +
                                       Gv[idz] * dy_du[idz] +
                                       Gw[idz] * dz_du[idz]);
                    tau23[idz] = mu * (Fu[idz] * dx_dw[idz] +
                                       Fv[idz] * dy_dw[idz] +
                                       Fw[idz] * dz_dw[idz] +
                                       Gu[idz] * dx_dv[idz] +
                                       Gv[idz] * dy_dv[idz] +
                                       Gw[idz] * dz_dv[idz]);
                    // Heat Fluxes
                    Ee[idz] = mucppr * (Ee[idz] * dx_du[idz] +
                                        Fe[idz] * dy_du[idz] +
                                        Ge[idz] * dz_du[idz]);
                    Fe[idz] = mucppr * (Ee[idz] * dx_dv[idz] +
                                        Fe[idz] * dy_dv[idz] +
                                        Ge[idz] * dz_dv[idz]);
                    Ge[idz] = mucppr * (Ee[idz] * dx_dw[idz] +
                                        Fe[idz] * dy_dw[idz] +
                                        Ge[idz] * dz_dw[idz]);

                    // Thermo-viscous Fluxes
                    Eu[idz] = (tau11[idz] * dx_du[idz] +
                               tau12[idz] * dx_dv[idz] +
                               tau13[idz] * dx_dw[idz]) * invJ[idz];
                    Fu[idz] = (tau11[idz] * dy_du[idz] +
                               tau12[idz] * dy_dv[idz] +
                               tau13[idz] * dy_dw[idz]) * invJ[idz];
                    Gu[idz] = (tau11[idz] * dz_du[idz] +
                               tau12[idz] * dz_dv[idz] +
                               tau13[idz] * dz_dw[idz]) * invJ[idz];

                    Ev[idz] = (tau12[idz] * dx_du[idz] +
                               tau22[idz] * dx_dv[idz] +
                               tau23[idz] * dx_dw[idz]) * invJ[idz];
                    Fv[idz] = (tau12[idz] * dy_du[idz] +
                               tau22[idz] * dy_dv[idz] +
                               tau23[idz] * dy_dw[idz]) * invJ[idz];
                    Gv[idz] = (tau12[idz] * dz_du[idz] +
                               tau22[idz] * dz_dv[idz] +
                               tau23[idz] * dz_dw[idz]) * invJ[idz];

                    Ew[idz] = (tau13[idz] * dx_du[idz] +
                               tau23[idz] * dx_dv[idz] +
                               tau33[idz] * dx_dw[idz]) * invJ[idz];
                    Fw[idz] = (tau13[idz] * dy_du[idz] +
                               tau23[idz] * dy_dv[idz] +
                               tau33[idz] * dy_dw[idz]) * invJ[idz];
                    Gw[idz] = (tau13[idz] * dz_du[idz] +
                               tau23[idz] * dz_dv[idz] +
                               tau33[idz] * dz_dw[idz]) * invJ[idz];

                    Ee_s = (E[idz] * tau11[idz] + F[idz] * tau12[idz] +
                            G[idz] * tau13[idz] + Ee[idz]);
                    Fe_s = (E[idz] * tau12[idz] + F[idz] * tau22[idz] +
                            G[idz] * tau23[idz] + Fe[idz]);
                    Ge_s = (E[idz] * tau13[idz] + F[idz] * tau23[idz] +
                            G[idz] * tau33[idz] + Ge[idz]);

                    Ee[idz] = (Ee_s * dx_du[idz] + Fe_s * dx_dv[idz] + Ge_s * dx_dw[idz]) * invJ[idz];
                    Fe[idz] = (Ee_s * dy_du[idz] + Fe_s * dy_dv[idz] + Ge_s * dy_dw[idz]) * invJ[idz];
                    Ge[idz] = (Ee_s * dz_du[idz] + Fe_s * dz_dv[idz] + Ge_s * dz_dw[idz]) * invJ[idz];
                }
            }
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d viscous fluxes computation dispatchers
////////////////////////////////////////////////////////////////////////////////


void static inline vflx2d_crt_dispatcher(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            vflx_crt2d_s(fld, ixmin, ixmax, iymin, iymax);
            break;
        default:
            vflx_crt2d_p(fld, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static inline vflx2d_crv_dispatcher(fields2d *fld, domain2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;

    switch(threads){
        case 1:
            vflx_crv2d_s(fld, ixmin, ixmax, iymin, iymax);
            break;
        default:
            vflx_crv2d_p(fld, ixmin, ixmax, iymin, iymax, threads);
    }
}


void static vflx2d_glob(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            vflx2d_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->vsc_gtime = fmin(fld->vsc_gtime, get_time(&start, &end));
}


void static vflx2d_sing(fields2d *fld){

    unsigned int c;
    domain2d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        vflx2d_dispatcher(fld, &dmns[c], dmns[c].thread_info_vsc.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_vsc, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->vsc_stime = fmin(fld->vsc_stime, get_time(&start_loop, &end_loop));
}


void viscous_fluxes2d(fields2d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->vsc_call >= max_gcalls){
        vflx2d_func(fld);
    } else if (fld->vsc_lock < fld->dmns_n){
        vflx2d_sing(fld);
    } else {
        vflx2d_glob(fld);
        fld->vsc_call += 1;

        if (fld->vsc_gtime > fld->vsc_stime) {
            vflx2d_func = vflx2d_sing;
            fld->vsc_glob = 0;
        } else {
            vflx2d_func = vflx2d_glob;
            fld->vsc_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->vsc_gtime > 1.5 * fld->vsc_stime || fld->vsc_stime > 1.5 * fld->vsc_gtime) {
            fld->vsc_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d viscous fluxes computation dispatcher
////////////////////////////////////////////////////////////////////////////////


void static inline vflx3d_crt_dispatcher(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            vflx_crt3d_s(fld, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            vflx_crt3d_p(fld, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static inline vflx3d_crv_dispatcher(fields3d *fld, domain3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;

    switch(threads){
        case 1:
            vflx_crv3d_s(fld, ixmin, ixmax, iymin, iymax, izmin, izmax);
            break;
        default:
            vflx_crv3d_p(fld, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
    }
}


void static vflx3d_glob(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    #pragma omp parallel private(c)
    {
        #pragma omp for nowait schedule(dynamic, 1)
        for (c = 0; c < size; c++) {
            vflx3d_dispatcher(fld, &dmns[c], 1);
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    fld->vsc_gtime = fmin(fld->vsc_gtime, get_time(&start, &end));
}


void static vflx3d_sing(fields3d *fld){

    unsigned int c;
    domain3d *dmns = fld->dmns;
    const unsigned int size = fld->dmns_n;
    struct timespec start, end, start_loop, end_loop;

    clock_gettime(CLOCK_MONOTONIC, &start_loop);
    for (c = 0; c < size; c++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        vflx3d_dispatcher(fld, &dmns[c], dmns[c].thread_info_vsc.cpu);
        clock_gettime(CLOCK_MONOTONIC, &end);
        set_thread_number(&dmns[c].thread_info_vsc, get_time(&start, &end));
    }
    clock_gettime(CLOCK_MONOTONIC, &end_loop);
    fld->vsc_stime = fmin(fld->vsc_stime, get_time(&start_loop, &end_loop));
}


void viscous_fluxes3d(fields3d *fld){

    const unsigned int max_gcalls = 2;

    if (fld->vsc_call >= max_gcalls){
        vflx3d_func(fld);
    } else if (fld->vsc_lock < fld->dmns_n){
        vflx3d_sing(fld);
    } else {
        vflx3d_glob(fld);
        fld->vsc_call += 1;

        if (fld->vsc_gtime > fld->vsc_stime) {
            vflx3d_func = vflx3d_sing;
            fld->vsc_glob = 0;
        } else {
            vflx3d_func = vflx3d_glob;
            fld->vsc_glob = 1;
        }
        // stop testing global dispatch if difference is too high.
        if (fld->vsc_gtime > 1.5 * fld->vsc_stime || fld->vsc_stime > 1.5 * fld->vsc_gtime) {
            fld->vsc_call = max_gcalls;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d temperature derivative (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline dtk2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2xc_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2xc_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2xP_s(fld->Ee, fld->Tk, *fld->odx, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2xP_v(fld->Ee, fld->Tk, fld->odx_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2xp_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2xp_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2xm_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2xm_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void dtk2d_x(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                dtk2d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            dtk2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d temperature derivative (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline dtk2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2yc_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2yc_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2yP_s(fld->Fe, fld->Tk, *fld->ody, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2yP_v(fld->Fe, fld->Tk, fld->ody_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2yp_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2yp_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2ym_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2ym_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void dtk2d_y(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                dtk2d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            dtk2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d temperature derivative (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline dtk3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3xc_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3xc_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3xP_s(fld->Ee, fld->Tk, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3xP_v(fld->Ee, fld->Tk, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3xp_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3xp_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3xm_s(fld->Ee, fld->Tk, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3xm_v(fld->Ee, fld->Tk, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void dtk3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                dtk3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            dtk3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d temperature derivative (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline dtk3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3yc_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3yc_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3yP_s(fld->Fe, fld->Tk, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3yP_v(fld->Fe, fld->Tk, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3yp_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3yp_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3ym_s(fld->Fe, fld->Tk, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3ym_v(fld->Fe, fld->Tk, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void dtk3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                dtk3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            dtk3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d temperature derivative (z)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline dtk3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3zc_s(fld->Ge, fld->Tk, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3zc_v(fld->Ge, fld->Tk, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3zP_s(fld->Ge, fld->Tk, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3zP_v(fld->Ge, fld->Tk, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3zp_s(fld->Ge, fld->Tk, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3zp_v(fld->Ge, fld->Tk, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3zm_s(fld->Ge, fld->Tk, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3zm_v(fld->Ge, fld->Tk, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void dtk3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                dtk3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            dtk3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d strain tensor (s11) (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s11_2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2xc_s(fld->Eu, fld->E, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2xc_v(fld->Eu, fld->E, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2xP_s(fld->Eu, fld->E, *fld->odx, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2xP_v(fld->Eu, fld->E, fld->odx_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2xp_s(fld->Eu, fld->E, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2xp_v(fld->Eu, fld->E, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2xm_s(fld->Eu, fld->E, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2xm_v(fld->Eu, fld->E, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void s11_2d_x(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s11_2d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s11_2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d strain tensor (s11) (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s11_2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2yc_s(fld->Ev, fld->E, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2yc_v(fld->Ev, fld->E, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2yP_s(fld->Ev, fld->E, *fld->ody, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2yP_v(fld->Ev, fld->E, fld->ody_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2yp_s(fld->Ev, fld->E, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2yp_v(fld->Ev, fld->E, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2ym_s(fld->Ev, fld->E, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2ym_v(fld->Ev, fld->E, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void s11_2d_y(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s11_2d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s11_2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d strain tensor (s22) (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s22_2d_x_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2xc_s(fld->Fu, fld->F, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2xc_v(fld->Fu, fld->F, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2xP_s(fld->Fu, fld->F, *fld->odx, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2xP_v(fld->Fu, fld->F, fld->odx_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2xp_s(fld->Fu, fld->F, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2xp_v(fld->Fu, fld->F, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2xm_s(fld->Fu, fld->F, *fld->odx, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2xm_v(fld->Fu, fld->F, fld->odx_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void s22_2d_x(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s22_2d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s22_2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d strain tensor (s22) (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s22_2d_y_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2yc_s(fld->Fv, fld->F, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2yc_v(fld->Fv, fld->F, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2yP_s(fld->Fv, fld->F, *fld->ody, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2yP_v(fld->Fv, fld->F, fld->ody_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2yp_s(fld->Fv, fld->F, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2yp_v(fld->Fv, fld->F, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2ym_s(fld->Fv, fld->F, *fld->ody, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2ym_v(fld->Fv, fld->F, fld->ody_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void s22_2d_y(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s22_2d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s22_2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}



////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s11) (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s11_3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3xc_s(fld->Eu, fld->E, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3xc_v(fld->Eu, fld->E, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3xP_s(fld->Eu, fld->E, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3xP_v(fld->Eu, fld->E, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3xp_s(fld->Eu, fld->E, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3xp_v(fld->Eu, fld->E, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3xm_s(fld->Eu, fld->E, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3xm_v(fld->Eu, fld->E, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s11_3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s11_3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s11_3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s11) (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s11_3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3yc_s(fld->Ev, fld->E, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3yc_v(fld->Ev, fld->E, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3yP_s(fld->Ev, fld->E, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3yP_v(fld->Ev, fld->E, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3yp_s(fld->Ev, fld->E, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3yp_v(fld->Ev, fld->E, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3ym_s(fld->Ev, fld->E, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3ym_v(fld->Ev, fld->E, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s11_3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s11_3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s11_3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s11) (z)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s11_3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3zc_s(fld->Ew, fld->E, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3zc_v(fld->Ew, fld->E, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3zP_s(fld->Ew, fld->E, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3zP_v(fld->Ew, fld->E, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3zp_s(fld->Ew, fld->E, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3zp_v(fld->Ew, fld->E, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3zm_s(fld->Ew, fld->E, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3zm_v(fld->Ew, fld->E, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s11_3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s11_3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s11_3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s22) (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s22_3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3xc_s(fld->Fu, fld->F, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3xc_v(fld->Fu, fld->F, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3xP_s(fld->Fu, fld->F, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3xP_v(fld->Fu, fld->F, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3xp_s(fld->Fu, fld->F, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3xp_v(fld->Fu, fld->F, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3xm_s(fld->Fu, fld->F, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3xm_v(fld->Fu, fld->F, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s22_3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s22_3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s22_3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s22) (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s22_3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3yc_s(fld->Fv, fld->F, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3yc_v(fld->Fv, fld->F, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3yP_s(fld->Fv, fld->F, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3yP_v(fld->Fv, fld->F, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3yp_s(fld->Fv, fld->F, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3yp_v(fld->Fv, fld->F, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3ym_s(fld->Fv, fld->F, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3ym_v(fld->Fv, fld->F, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s22_3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s22_3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s22_3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}



////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s22) (z)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s22_3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3zc_s(fld->Fw, fld->F, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3zc_v(fld->Fw, fld->F, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3zP_s(fld->Fw, fld->F, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3zP_v(fld->Fw, fld->F, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3zp_s(fld->Fw, fld->F, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3zp_v(fld->Fw, fld->F, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3zm_s(fld->Fw, fld->F, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3zm_v(fld->Fw, fld->F, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s22_3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s22_3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s22_3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s33) (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s33_3d_x_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3xc_s(fld->Gu, fld->G, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3xc_v(fld->Gu, fld->G, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3xP_s(fld->Gu, fld->G, *fld->odx, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3xP_v(fld->Gu, fld->G, fld->odx_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3xp_s(fld->Gu, fld->G, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3xp_v(fld->Gu, fld->G, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3xm_s(fld->Gu, fld->G, *fld->odx, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3xm_v(fld->Gu, fld->G, fld->odx_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s33_3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s33_3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s33_3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s33) (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s33_3d_y_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3yc_s(fld->Gv, fld->G, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3yc_v(fld->Gv, fld->G, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3yP_s(fld->Gv, fld->G, *fld->ody, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3yP_v(fld->Gv, fld->G, fld->ody_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3yp_s(fld->Gv, fld->G, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3yp_v(fld->Gv, fld->G, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3ym_s(fld->Gv, fld->G, *fld->ody, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3ym_v(fld->Gv, fld->G, fld->ody_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s33_3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s33_3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s33_3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d strain tensor (s33) (z)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline s33_3d_z_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3zc_s(fld->Gw, fld->G, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3zc_v(fld->Gw, fld->G, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3zP_s(fld->Gw, fld->G, *fld->odz, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3zP_v(fld->Gw, fld->G, fld->odz_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3zp_s(fld->Gw, fld->G, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3zp_v(fld->Gw, fld->G, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3zm_s(fld->Gw, fld->G, *fld->odz, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3zm_v(fld->Gw, fld->G, fld->odz_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void s33_3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                s33_3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            s33_3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d viscous fluxes integration (x)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline vfi2d_x_crt_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_xc_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_xc_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_xP_s(fld->ru, fld->tau11, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_s(fld->rv, fld->tau12, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_s(fld->re, fld->Ee, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_xP_v(fld->ru, fld->tau11, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_v(fld->rv, fld->tau12, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_v(fld->re, fld->Ee, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_xp_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_xp_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_xm_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_xm_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static inline vfi2d_x_crv_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_xc_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_xc_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xc_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_xP_s(fld->ru, fld->Eu, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_s(fld->rv, fld->Ev, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_s(fld->re, fld->Ee, *fld->odxdt, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_xP_v(fld->ru, fld->Eu, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_v(fld->rv, fld->Ev, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xP_v(fld->re, fld->Ee, fld->odxdt_v, fld->P11x, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_xp_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_xp_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xp_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_xm_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_xm_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_xm_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void vfluxes_integration2d_x(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vfi2d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vfi2d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 2d viscous fluxes integration (y)  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline vfi2d_y_crt_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_yc_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_yc_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_yP_s(fld->ru, fld->tau12, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->rv, fld->tau22, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->re, fld->Fe, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_yP_v(fld->ru, fld->tau12, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->rv, fld->tau22, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->re, fld->Fe, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_yp_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_yp_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_ym_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_ym_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void static inline vfi2d_y_crv_dispatcher(fields2d *fld, domain_ax2d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d2add_yc_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 12:
            d2add_yc_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yc_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 0:
            d2add_yP_s(fld->ru, fld->Fu, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->rv, fld->Fv, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_s(fld->re, fld->Fe, *fld->odydt, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 1:
            d2add_yP_v(fld->ru, fld->Fu, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->rv, fld->Fv, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yP_v(fld->re, fld->Fe, fld->odydt_v, fld->P11y, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 5:
            d2add_yp_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case 6:
            d2add_yp_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_yp_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -5:
            d2add_ym_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_s(fld->re, fld->Fe, *fld->odydt, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
        case -4:
            d2add_ym_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            d2add_ym_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, ixmin, ixmax, iymin, iymax, threads);
            break;
    }
}


void vfluxes_integration2d_y(fields2d *fld){

    unsigned int c;
    domain_ax2d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vfi2d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vfi2d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d viscous fluxes integration (x) [checked]  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline vfi3d_x_crt_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_xc_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->rw, fld->tau13, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_xc_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->rw, fld->tau13, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_xP_s(fld->ru, fld->tau11, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->rv, fld->tau12, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->rw, fld->tau13, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->re, fld->Ee, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_xP_v(fld->ru, fld->tau11, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->rv, fld->tau12, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->rw, fld->tau13, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->re, fld->Ee, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_xp_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->rw, fld->tau13, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_xp_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->rw, fld->tau13, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_xm_s(fld->ru, fld->tau11, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->rv, fld->tau12, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->rw, fld->tau13, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_xm_v(fld->ru, fld->tau11, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->rv, fld->tau12, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->rw, fld->tau13, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vfi3d_x_crv_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_xc_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->rw, fld->Ew, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_xc_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->rw, fld->Ew, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xc_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_xP_s(fld->ru, fld->Eu, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->rv, fld->Ev, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->rw, fld->Ew, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_s(fld->re, fld->Ee, *fld->odxdt, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_xP_v(fld->ru, fld->Eu, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->rv, fld->Ev, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->rw, fld->Ew, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xP_v(fld->re, fld->Ee, fld->odxdt_v, fld->P11x, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_xp_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->rw, fld->Ew, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_xp_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->rw, fld->Ew, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xp_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_xm_s(fld->ru, fld->Eu, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->rv, fld->Ev, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->rw, fld->Ew, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_s(fld->re, fld->Ee, *fld->odxdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_xm_v(fld->ru, fld->Eu, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->rv, fld->Ev, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->rw, fld->Ew, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_xm_v(fld->re, fld->Ee, fld->odxdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void vfluxes_integration3d_x(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_x;
    const unsigned int size = fld->dmns_x_n;

    if (fld->dux_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vfi3d_x_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vfi3d_x_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d viscous fluxes integration (y) [checked]  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline vfi3d_y_crt_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_yc_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rw, fld->tau23, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_yc_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rw, fld->tau23, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_yP_s(fld->ru, fld->tau12, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rv, fld->tau22, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rw, fld->tau23, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->re, fld->Fe, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_yP_v(fld->ru, fld->tau12, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rv, fld->tau22, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rw, fld->tau23, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->re, fld->Fe, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_yp_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rw, fld->tau23, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_yp_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rw, fld->tau23, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_ym_s(fld->ru, fld->tau12, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rv, fld->tau22, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rw, fld->tau23, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_ym_v(fld->ru, fld->tau12, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rv, fld->tau22, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rw, fld->tau23, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vfi3d_y_crv_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_yc_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->rw, fld->Fw, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_yc_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->rw, fld->Fw, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yc_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_yP_s(fld->ru, fld->Fu, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rv, fld->Fv, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->rw, fld->Fw, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_s(fld->re, fld->Fe, *fld->odydt, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_yP_v(fld->ru, fld->Fu, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rv, fld->Fv, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->rw, fld->Fw, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yP_v(fld->re, fld->Fe, fld->odydt_v, fld->P11y, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_yp_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->rw, fld->Fw, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_yp_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->rw, fld->Fw, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_yp_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_ym_s(fld->ru, fld->Fu, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rv, fld->Fv, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->rw, fld->Fw, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_s(fld->re, fld->Fe, *fld->odydt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_ym_v(fld->ru, fld->Fu, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rv, fld->Fv, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->rw, fld->Fw, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_ym_v(fld->re, fld->Fe, fld->odydt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void vfluxes_integration3d_y(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_y;
    const unsigned int size = fld->dmns_y_n;

    if (fld->duy_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vfi3d_y_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vfi3d_y_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// 3d viscous fluxes integration (z) [checked]  [use du thread]
////////////////////////////////////////////////////////////////////////////////


void static inline vfi3d_z_crt_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_zc_s(fld->ru, fld->tau13, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rv, fld->tau23, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rw, fld->tau33, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_zc_v(fld->ru, fld->tau13, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rv, fld->tau23, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rw, fld->tau33, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_zP_s(fld->ru, fld->tau13, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rv, fld->tau23, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rw, fld->tau33, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->re, fld->Ge, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_zP_v(fld->ru, fld->tau13, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rv, fld->tau23, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rw, fld->tau33, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->re, fld->Ge, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_zp_s(fld->ru, fld->tau13, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rv, fld->tau23, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rw, fld->tau33, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_zp_v(fld->ru, fld->tau13, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rv, fld->tau23, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rw, fld->tau33, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_zm_s(fld->ru, fld->tau13, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rv, fld->tau23, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rw, fld->tau33, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_zm_v(fld->ru, fld->tau13, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rv, fld->tau23, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rw, fld->tau33, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void static inline vfi3d_z_crv_dispatcher(fields3d *fld, domain_ax3d *dmns, const unsigned int threads){

    const unsigned int ixmin = dmns->ixmin;
    const unsigned int ixmax = dmns->ixmax;
    const unsigned int iymin = dmns->iymin;
    const unsigned int iymax = dmns->iymax;
    const unsigned int izmin = dmns->izmin;
    const unsigned int izmax = dmns->izmax;
    const int scm = dmns->dscm;

    switch(scm){
        case 11:
            d3add_zc_s(fld->ru, fld->Gu, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rv, fld->Gv, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->rw, fld->Gw, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 12:
            d3add_zc_v(fld->ru, fld->Gu, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rv, fld->Gv, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->rw, fld->Gw, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zc_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 0:
            d3add_zP_s(fld->ru, fld->Gu, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rv, fld->Gv, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->rw, fld->Gw, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_s(fld->re, fld->Ge, *fld->odzdt, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 1:
            d3add_zP_v(fld->ru, fld->Gu, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rv, fld->Gv, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->rw, fld->Gw, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zP_v(fld->re, fld->Ge, fld->odzdt_v, fld->P11z, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 5:
            d3add_zp_s(fld->ru, fld->Gu, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rv, fld->Gv, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->rw, fld->Gw, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case 6:
            d3add_zp_v(fld->ru, fld->Gu, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rv, fld->Gv, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->rw, fld->Gw, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zp_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -5:
            d3add_zm_s(fld->ru, fld->Gu, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rv, fld->Gv, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->rw, fld->Gw, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_s(fld->re, fld->Ge, *fld->odzdt, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
        case -4:
            d3add_zm_v(fld->ru, fld->Gu, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rv, fld->Gv, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->rw, fld->Gw, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            d3add_zm_v(fld->re, fld->Ge, fld->odzdt_v, fld->ny, fld->nz, ixmin, ixmax, iymin, iymax, izmin, izmax, threads);
            break;
    }
}


void vfluxes_integration3d_z(fields3d *fld){

    unsigned int c;
    domain_ax3d *dmns = fld->dmns_z;
    const unsigned int size = fld->dmns_z_n;

    if (fld->duz_glob) {
        #pragma omp parallel private(c)
        {
            #pragma omp for nowait schedule(dynamic, 1)
            for (c = 0; c < size; c++) {
                vfi3d_z_dispatcher(fld, &dmns[c], 1);
            }
        }
    } else {
        for (c = 0; c < size; c++) {
            vfi3d_z_dispatcher(fld, &dmns[c], dmns[c].thread_info_du.cpu);
        }
    }
}


////////////////////////////////////////////////////////////////////////////////
// Set pointers
////////////////////////////////////////////////////////////////////////////////


void viscous_fluxes2d_init(fields2d *fld) {

    if (fld->crv == 1) {
        vflx2d_dispatcher = vflx2d_crv_dispatcher;
        vfi2d_x_dispatcher = vfi2d_x_crv_dispatcher;
        vfi2d_y_dispatcher = vfi2d_y_crv_dispatcher;
    } else {
        vflx2d_dispatcher = vflx2d_crt_dispatcher;
        vfi2d_x_dispatcher = vfi2d_x_crt_dispatcher;
        vfi2d_y_dispatcher = vfi2d_y_crt_dispatcher;
    }
}


void viscous_fluxes3d_init(fields3d *fld) {

    if (fld->crv == 1) {
        vflx3d_dispatcher = vflx3d_crv_dispatcher;
        vfi3d_x_dispatcher = vfi3d_x_crv_dispatcher;
        vfi3d_y_dispatcher = vfi3d_y_crv_dispatcher;
        vfi3d_z_dispatcher = vfi3d_z_crv_dispatcher;
    } else {
        vflx3d_dispatcher = vflx3d_crt_dispatcher;
        vfi3d_x_dispatcher = vfi3d_x_crt_dispatcher;
        vfi3d_y_dispatcher = vfi3d_y_crt_dispatcher;
        vfi3d_z_dispatcher = vfi3d_z_crt_dispatcher;
    }
}