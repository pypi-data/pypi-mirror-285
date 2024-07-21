#ifndef KERNEL_DIFFRAW_H
#define KERNEL_DIFFRAW_H

/*----------------------------*/
/* Global 1d differentiation */
/*--------------------------*/

void d1_s(double *restrict dvdx, const double *restrict v, const double odx, const unsigned int n);

/*-------*/
/* Test */
/*-----*/

void d2xc_s_naive(double *restrict dvdx, const double *restrict v, const double odx,
                           const unsigned int ny,
                           const unsigned int ixmin, const unsigned int ixmax,
                           const unsigned int iymin, const unsigned int iymax,
                           const unsigned int threads);

/*-------------------------------*/
/* Subdomain 2d differentiation */
/*-----------------------------*/

void d2xc_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2xc_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2yc_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2yc_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax, const unsigned int threads);


void d2xP_s(double *restrict dv, const double *restrict v,
                const double odn, const unsigned int *restrict P,
                const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads);


void d2xP_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int *restrict P,
                const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads);


void d2yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);


void d2yP_v(double *restrict dv, const double *restrict v,
                const double *restrict odn, const unsigned int *restrict P,
                const unsigned int ny,
                const unsigned int ixmin, const unsigned int ixmax,
                const unsigned int iymin, const unsigned int iymax, const unsigned int threads);


void d2xp_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2xp_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2yp_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2yp_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2xm_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2xm_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2ym_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

void d2ym_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int threads);

/*----------------------------*/
/* Global 2d differentiation */
/*--------------------------*/


void d2x_s(double *restrict dvdx, const double *restrict v, const double odx,
                         const unsigned int nx, const unsigned int ny, const unsigned int threads);

void d2x_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                         const unsigned int nx, const unsigned int ny, const unsigned int threads);

void d2y_s(double *restrict dvdy, const double *restrict v, const double ody,
                         const unsigned int nx, const unsigned int ny, const unsigned int threads);

void d2y_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                         const unsigned int nx, const unsigned int ny, const unsigned int threads);

/*-------------------------------*/
/* Subdomain 3d differentiation */
/*-----------------------------*/


void d3xc_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3xc_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3yc_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3yc_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zc_s(double *restrict dvdz, const double *restrict v, const double odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zc_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3xP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3xP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);


void d3yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3yP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3zP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3zP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3xp_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3xp_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3yp_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3yp_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zp_s(double *restrict dvdz, const double *restrict v, const double odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zp_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3xm_s(double *restrict dvdx, const double *restrict v, const double odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3xm_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3ym_s(double *restrict dvdy, const double *restrict v, const double ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3ym_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zm_s(double *restrict dvdz, const double *restrict v, const double odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

void d3zm_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
                          const unsigned int ny, const unsigned int nz,
                          const unsigned int ixmin, const unsigned int ixmax,
                          const unsigned int iymin, const unsigned int iymax,
                          const unsigned int izmin, const unsigned int izmax,
                          const unsigned int threads);

/*----------------------------*/
/* Global 3d differentiation */
/*--------------------------*/

void d3x_s(double *restrict dvdx, const double *restrict v, const double odx,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

void d3x_v(double *restrict dvdx, const double *restrict v, const double *restrict odx,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

void d3y_s(double *restrict dvdy, const double *restrict v, const double ody,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

void d3y_v(double *restrict dvdy, const double *restrict v, const double *restrict ody,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

void d3z_s(double *restrict dvdz, const double *restrict v, const double odz,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

void d3z_v(double *restrict dvdz, const double *restrict v, const double *restrict odz,
                         const unsigned int nx, const unsigned int ny, const unsigned int nz,
                         const unsigned int threads);

#endif