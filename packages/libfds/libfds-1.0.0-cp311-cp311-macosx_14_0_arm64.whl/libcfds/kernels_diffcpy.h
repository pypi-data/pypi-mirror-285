#ifndef KERNEL_DIFFCPY_H
#define KERNEL_DIFFCPY_H

/*-------------------------------*/
/* Subdomain 2d differentiation */
/*-----------------------------*/


void d2cpy_xc_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2cpy_xc_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2cpy_xP_s(double *restrict dv, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2cpy_xP_v(double *restrict dv, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2cpy_xp_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2cpy_xp_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2cpy_xm_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2cpy_xm_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

/*-------------------------------*/
/* Subdomain 3d differentiation */
/*-----------------------------*/

void d3cpy_xc_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3cpy_xc_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3cpy_xP_s(double *restrict dv, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3cpy_xP_v(double *restrict dv, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3cpy_xp_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);


void d3cpy_xp_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);


void d3cpy_xm_s(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3cpy_xm_v(double *restrict dvdx, const double *restrict v, const double *restrict vc,
                              const double *restrict odn, const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

#endif