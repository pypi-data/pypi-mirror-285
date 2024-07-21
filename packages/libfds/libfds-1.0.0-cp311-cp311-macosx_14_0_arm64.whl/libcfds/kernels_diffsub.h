#ifndef KERNEL_DIFFSUB_H
#define KERNEL_DIFFSUB_H

/*---------------------------------------------*/
/* Subdomain 2d differentiation with addition */
/*-------------------------------------------*/


void d2sub_xc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_xc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_yc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_yc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_xP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_xP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_yP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax, const unsigned int threads);

void d2sub_xp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_xp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_yp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_yp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_xm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_xm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_ym_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

void d2sub_ym_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int threads);

/*---------------------------------------------*/
/* Subdomain 3d differentiation with addition */
/*-------------------------------------------*/

void d3sub_xc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_xc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_yc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_yc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zc_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zc_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_xP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_xP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_yP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_yP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_zP_s(double *restrict dv, const double *restrict v,
                              const double odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_zP_v(double *restrict dv, const double *restrict v,
                              const double *restrict odn, const unsigned int *restrict P,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax, const unsigned int threads);

void d3sub_xp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_xp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_yp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_yp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zp_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zp_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_xm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_xm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_ym_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_ym_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zm_s(double *restrict dv, const double *restrict v, const double odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

void d3sub_zm_v(double *restrict dv, const double *restrict v, const double *restrict odn,
                              const unsigned int ny, const unsigned int nz,
                              const unsigned int ixmin, const unsigned int ixmax,
                              const unsigned int iymin, const unsigned int iymax,
                              const unsigned int izmin, const unsigned int izmax,
                              const unsigned int threads);

#endif