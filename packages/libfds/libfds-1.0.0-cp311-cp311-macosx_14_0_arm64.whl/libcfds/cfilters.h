#ifndef FILTER_H
#define FILTER_H
#include "cobjects.h"
#include "cfields.h"


////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////

void apply_filter2d_x(fields2d *fld);
void apply_filter2d_y(fields2d *fld);

void apply_capture2d_x(fields2d *fld);
void apply_capture2d_y(fields2d *fld);

void selective_filter2d_x(fields2d *fld);
void selective_filter2d_y(fields2d *fld);

void laplacian_filter2d_x(fields2d *fld);
void laplacian_filter2d_y(fields2d *fld);

void sigma2d_x(fields2d *fld);
void sigma2d_y(fields2d *fld);

void shock_capture2d_x(fields2d *fld);
void shock_capture2d_y(fields2d *fld);

void apply_filter3d_x(fields3d *fld);
void apply_filter3d_y(fields3d *fld);
void apply_filter3d_z(fields3d *fld);

void apply_capture3d_x(fields3d *fld);
void apply_capture3d_y(fields3d *fld);
void apply_capture3d_z(fields3d *fld);

void selective_filter3d_x(fields3d *fld);
void selective_filter3d_y(fields3d *fld);
void selective_filter3d_z(fields3d *fld);

void laplacian_filter3d_x(fields3d *fld);
void laplacian_filter3d_y(fields3d *fld);
void laplacian_filter3d_z(fields3d *fld);

void sigma3d_x(fields3d *fld);
void sigma3d_y(fields3d *fld);
void sigma3d_z(fields3d *fld);

void shock_capture3d_x(fields3d *fld);
void shock_capture3d_y(fields3d *fld);
void shock_capture3d_z(fields3d *fld);

void sf2d_x(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int threads);

void sf2d_y(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int threads);

void sf3d_x(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads);

void sf3d_y(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads);

void sf3d_z(double *restrict vf, double *restrict v, double xnu_n, double xnu_0,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned threads);

void lf2d_x(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int threads);

void lf2d_y(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int threads);

void lf3d_x(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads);

void lf3d_y(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned int threads);

void lf3d_z(double *restrict vf, double *restrict v,
            const unsigned int nx, const unsigned int ny, const unsigned int nz,
            const unsigned threads);

////////////////////////////////////////////////////////////////////////////////
// Pointers
////////////////////////////////////////////////////////////////////////////////

void (*fu2d_x_func)(fields2d *, domain_ax2d *);
void (*fu2d_y_func)(fields2d *, domain_ax2d *);
void (*lf2d_x_func)(fields2d *);
void (*lf2d_y_func)(fields2d *);
void (*sg2d_x_func)(fields2d *);
void (*sg2d_y_func)(fields2d *);
void (*sc2d_x_func)(fields2d *);
void (*sc2d_y_func)(fields2d *);

void (*fu3d_x_func)(fields3d *, domain_ax3d *);
void (*fu3d_y_func)(fields3d *, domain_ax3d *);
void (*fu3d_z_func)(fields3d *, domain_ax3d *);
void (*lf3d_x_func)(fields3d *);
void (*lf3d_y_func)(fields3d *);
void (*lf3d_z_func)(fields3d *);
void (*sg3d_x_func)(fields3d *);
void (*sg3d_y_func)(fields3d *);
void (*sg3d_z_func)(fields3d *);
void (*sc3d_x_func)(fields3d *);
void (*sc3d_y_func)(fields3d *);
void (*sc3d_z_func)(fields3d *);


#endif