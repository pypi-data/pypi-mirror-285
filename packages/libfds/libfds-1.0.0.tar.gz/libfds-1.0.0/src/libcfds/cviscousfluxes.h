#ifndef VISCOUS_H
#define VISCOUS_H
#include "cobjects.h"

////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////

void viscous_fluxes2d(fields2d *fld);
void viscous_fluxes3d(fields3d *fld);

void dtk2d_x(fields2d *fld);
void dtk2d_y(fields2d *fld);

void dtk3d_x(fields3d *fld);
void dtk3d_y(fields3d *fld);
void dtk3d_z(fields3d *fld);

void s11_2d_x(fields2d *fld);
void s11_2d_y(fields2d *fld);
void s22_2d_x(fields2d *fld);
void s22_2d_y(fields2d *fld);

void s11_3d_x(fields3d *fld);
void s11_3d_y(fields3d *fld);
void s11_3d_z(fields3d *fld);
void s22_3d_x(fields3d *fld);
void s22_3d_y(fields3d *fld);
void s22_3d_z(fields3d *fld);
void s33_3d_x(fields3d *fld);
void s33_3d_y(fields3d *fld);
void s33_3d_z(fields3d *fld);

void vfluxes_integration2d_x(fields2d *fld);
void vfluxes_integration2d_y(fields2d *fld);

void vfluxes_integration3d_x(fields3d *fld);
void vfluxes_integration3d_y(fields3d *fld);
void vfluxes_integration3d_z(fields3d *fld);

void viscous_fluxes2d_init(fields2d *fld);
void viscous_fluxes3d_init(fields3d *fld);

////////////////////////////////////////////////////////////////////////////////
// Pointers
////////////////////////////////////////////////////////////////////////////////

void (*vflx2d_func)(fields2d *);
void (*vflx2d_dispatcher)(fields2d *, domain2d *dmns, const unsigned int);
void (*vfi2d_x_dispatcher)(fields2d *, domain_ax2d *dmns, const unsigned int);
void (*vfi2d_y_dispatcher)(fields2d *, domain_ax2d *dmns, const unsigned int);

void (*vflx3d_func)(fields3d *);
void (*vflx3d_dispatcher)(fields3d *, domain3d *dmns, const unsigned int);
void (*vfi3d_x_dispatcher)(fields3d *, domain_ax3d *dmns, const unsigned int);
void (*vfi3d_y_dispatcher)(fields3d *, domain_ax3d *dmns, const unsigned int);
void (*vfi3d_z_dispatcher)(fields3d *, domain_ax3d *dmns, const unsigned int);

#endif