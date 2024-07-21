#ifndef KERNEL_SF_H
#define KERNEL_SF_H

////////////////////////////////////////////////////////////////////////////////
// 2d SF
////////////////////////////////////////////////////////////////////////////////

void sf2d_xc(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_yc(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_xP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_yP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_xp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_xm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sf2d_yp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);


void sf2d_ym(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// 3d SF
////////////////////////////////////////////////////////////////////////////////

void sf3d_xc(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_yc(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_zc(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_xP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_yP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_zP(double *restrict vf, const double *restrict v, double xnu_n,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_xp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_xm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_yp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_ym(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_zp(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sf3d_zm(double *restrict vf, const double *restrict v, double xnu_n, double xnu_0,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

#endif