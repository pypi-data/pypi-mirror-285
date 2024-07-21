#ifndef KERNEL_SC_H
#define KERNEL_SC_H

////////////////////////////////////////////////////////////////////////////////
// LF 2d
////////////////////////////////////////////////////////////////////////////////

void lf2d_xc(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_yc(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_xP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_yP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_xp(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_xm(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_yp(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void lf2d_ym(double *restrict vf, const double *restrict v,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// LF 3d
////////////////////////////////////////////////////////////////////////////////

void lf3d_xc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_yc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_zc(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_xP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_yP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_zP(double *restrict vf, const double *restrict v,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_xp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_xm(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_yp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_ym(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_zp(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void lf3d_zm(double *restrict vf, const double *restrict v,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// SG 2d
////////////////////////////////////////////////////////////////////////////////

unsigned int sg2d_xc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_yc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_xP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_yP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_xp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_xm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_yp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

unsigned int sg2d_ym(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// SG 3d
////////////////////////////////////////////////////////////////////////////////

unsigned int sg3d_xc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_yc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_zc(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_xP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_yP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_zP(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_xp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_xm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_yp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_ym(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_zp(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

unsigned int sg3d_zm(double *restrict sg, const double *restrict v, const double *restrict p,
                     const unsigned int ny, const unsigned int nz,
                     const unsigned int ixmin, const unsigned int ixmax,
                     const unsigned int iymin, const unsigned int iymax,
                     const unsigned int izmin, const unsigned int izmax,
                     const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// SC 2d [checked and faster]
////////////////////////////////////////////////////////////////////////////////

void sc2d_xc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_yc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_xP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_yP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_xp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_xm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

void sc2d_yp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);


void sc2d_ym(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int threads);

////////////////////////////////////////////////////////////////////////////////
// SC 3d [checked and faster]
////////////////////////////////////////////////////////////////////////////////

void sc3d_xc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_yc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_zc(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_xP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_yP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_zP(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int *restrict P, const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_xp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_xm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_yp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_ym(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_zp(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

void sc3d_zm(double *restrict vf, const double *restrict v, const double *restrict sg,
             const unsigned int ny, const unsigned int nz,
             const unsigned int ixmin, const unsigned int ixmax,
             const unsigned int iymin, const unsigned int iymax,
             const unsigned int izmin, const unsigned int izmax,
             const unsigned int threads);

#endif