
#ifndef EULER_H
#define EULER_H
#include "cfields.h"

////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////

void eulerian_fluxes2d_init(fields2d * fld);
void eulerian_fluxes3d_init(fields3d * fld);

void eulerian_fluxes2d(fields2d *fld);
void eulerian_fluxes3d(fields3d *fld);

void eulerian_derivatives2d_x(fields2d *fld);
void eulerian_derivatives2d_y(fields2d *fld);

void eulerian_derivatives3d_x(fields3d *fld);
void eulerian_derivatives3d_y(fields3d *fld);
void eulerian_derivatives3d_z(fields3d *fld);

////////////////////////////////////////////////////////////////////////////////
// Pointers 
////////////////////////////////////////////////////////////////////////////////

// has to be initialized using eulerian_fluxes3d_init/eulerian_fluxes3d_init
void (*eflx2d_dispatcher)(fields2d *, domain2d *dmns, const unsigned int);
void (*eflx2d_duy_dispatcher)(fields2d *, domain_ax2d *, const unsigned int);

void (*eflx3d_dispatcher)(fields3d *, domain3d *dmns, const unsigned int);
void (*eflx3d_duy_dispatcher)(fields3d *, domain_ax3d *, const unsigned int);
void (*eflx3d_duz_dispatcher)(fields3d *, domain_ax3d *, const unsigned int);

// initialized after some calls to eulerian_fluxes2d/eulerian_fluxes2d
void (*eflx2d_func)(fields2d *);
void (*eflx2d_dux_func)(fields2d *);
void (*eflx2d_duy_func)(fields2d *);

void (*eflx3d_func)(fields3d *);
void (*eflx3d_dux_func)(fields3d *);
void (*eflx3d_duy_func)(fields3d *);
void (*eflx3d_duz_func)(fields3d *);

#endif