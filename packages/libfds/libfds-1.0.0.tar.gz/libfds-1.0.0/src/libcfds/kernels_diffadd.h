#ifndef KERNEL_DIFFADD_H
#define KERNEL_DIFFADD_H

/*---------------------------------------------*/
/* Subdomain 2d differentiation with addition */
/*-------------------------------------------*/


void d2add_xc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_xc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_yc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_yc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_xP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_xP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_yP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2add_xp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_xp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_yp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_yp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_xm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_xm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_ym_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2add_ym_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

/*---------------------------------------------*/
/* Subdomain 3d differentiation with addition */
/*-------------------------------------------*/

void d3add_xc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_xc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_yc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_yc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_xP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_xP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_yP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_zP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_zP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3add_xp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_xp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_yp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_yp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_xm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_xm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_ym_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_ym_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3add_zm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

#endif