#ifndef OBJECTS
#define OBJECTS

typedef struct {
    unsigned int cpu;
    unsigned int calls;
    unsigned int lock;
    unsigned int *glock;
    unsigned int *cpus;
    unsigned int ncpus;
    unsigned int means;
    unsigned int cycles;
    double *timings;
} ThreadInfo;


typedef struct {
    unsigned int ixmin, ixmax, iymin, iymax, size_d;
    unsigned int *n;
    ThreadInfo thread_info_eul;
    ThreadInfo thread_info_vsc;
    ThreadInfo thread_info_n2p;
    ThreadInfo thread_info_vup;
    ThreadInfo thread_info_pup;
    ThreadInfo thread_info_rsd;
    ThreadInfo thread_info_cpy;
    ThreadInfo thread_info_tes;
} domain2d;


typedef struct {
    unsigned int ixmin, ixmax, iymin, iymax, izmin, izmax, size_d;
    unsigned int *n;
    ThreadInfo thread_info_eul;
    ThreadInfo thread_info_vsc;
    ThreadInfo thread_info_n2p;
    ThreadInfo thread_info_vup;
    ThreadInfo thread_info_pup;
    ThreadInfo thread_info_rsd;
    ThreadInfo thread_info_cpy;
    ThreadInfo thread_info_tes;
} domain3d;


typedef struct {
    unsigned int ixmin, ixmax, iymin, iymax, size_d;
    int dscm, fscm;
    unsigned int sc_flag;
    unsigned int *n;
    double *fu_gtime;
    double *fu_stime;
    ThreadInfo thread_info_du;
    ThreadInfo thread_info_lf;
    ThreadInfo thread_info_sc;
    ThreadInfo thread_info_sg;
    ThreadInfo thread_info_fu;
} domain_ax2d;


typedef struct {
    unsigned int ixmin, ixmax, iymin, iymax, izmin, izmax, size_d;
    int dscm, fscm;
    unsigned int sc_flag;
    unsigned int *n;
    double *fu_gtime;
    double *fu_stime;
    ThreadInfo thread_info_du;
    ThreadInfo thread_info_lf;
    ThreadInfo thread_info_sc;
    ThreadInfo thread_info_sg;
    ThreadInfo thread_info_fu;
} domain_ax3d;


typedef struct {
   double * profile;
   double * evolution;
} monopole;


typedef struct {
    unsigned int nx, ny, size, dmns_n, dmns_x_n, dmns_y_n;
    unsigned int crv, vsc;
    domain2d * dmns;
    domain_ax2d * dmns_x;
    domain_ax2d * dmns_y;

    double eul_gtime, vsc_gtime, pup_gtime, vup_gtime, n2p_gtime, tes_gtime, cpy_gtime;
    double eul_stime, vsc_stime, pup_stime, vup_stime, n2p_stime, tes_stime, cpy_stime;

    unsigned int eul_call, vsc_call, pup_call, vup_call, n2p_call, tes_call, cpy_call;
    unsigned int eul_glob, vsc_glob, pup_glob, vup_glob, n2p_glob, tes_glob, cpy_glob;
    unsigned int eul_lock, vsc_lock, pup_lock, vup_lock, n2p_lock, tes_lock, cpy_lock, rsd_lock;

    double dux_gtime, lfx_gtime, scx_gtime, sgx_gtime, fux_gtime;
    double duy_gtime, lfy_gtime, scy_gtime, sgy_gtime, fuy_gtime;
    double dux_stime, lfx_stime, scx_stime, sgx_stime, fux_stime;
    double duy_stime, lfy_stime, scy_stime, sgy_stime, fuy_stime;

    unsigned int dux_glob, lfx_glob, scx_glob, sgx_glob, fux_glob;
    unsigned int duy_glob, lfy_glob, scy_glob, sgy_glob, fuy_glob;
    unsigned int dux_call, lfx_call, scx_call, sgx_call, fux_call;
    unsigned int duy_call, lfy_call, scy_call, sgy_call, fuy_call;
    unsigned int dux_lock, lfx_lock, scx_lock, sgx_lock, fux_lock;
    unsigned int duy_lock, lfy_lock, scy_lock, sgy_lock, fuy_lock;

    double p0, mu0, cppr, cpmcv, Tref, Ssu, SsuTref;
    double gm1, gm1_over_c, gm1_over_cpmcv;
    double xnu_n, xnu_0, rsd;

    double * odx;
    double * ody;
    double * odx_v;
    double * ody_v;
    double * odxdt;
    double * odydt;
    double * odxdt_v;
    double * odydt_v;
    double * odxdtrk;
    double * odydtrk;
    double * odxdtrk_v;
    double * odydtrk_v;
    unsigned int * P3x;
    unsigned int * P3y;
    unsigned int * P5x;
    unsigned int * P5y;
    unsigned int * P11x;
    unsigned int * P11y;

    double * r;
    double * ru;
    double * rv;
    double * re;
    double * p;
    double * Tk;
    double * E;
    double * Eu;
    double * Ev;
    double * Ee;
    double * F;
    double * Fu;
    double * Fv;
    double * Fe;
    double * K;
    double * Ku;
    double * Kv;
    double * Ke;
    double * invJ;
    double * dx_du;
    double * dx_dv;
    double * dy_du;
    double * dy_dv;
    double * tau11;
    double * tau22;
    double * tau12;
    double * wz;
} fields2d;


typedef struct {
    unsigned int nx, ny, nz, size, dmns_n, dmns_x_n, dmns_y_n, dmns_z_n;
    unsigned int crv, vsc;
    domain3d * dmns;
    domain_ax3d * dmns_x;
    domain_ax3d * dmns_y;
    domain_ax3d * dmns_z;

    double eul_gtime, vsc_gtime, pup_gtime, vup_gtime, n2p_gtime, tes_gtime, cpy_gtime;
    double eul_stime, vsc_stime, pup_stime, vup_stime, n2p_stime, tes_stime, cpy_stime;

    unsigned int eul_call, vsc_call, pup_call, vup_call, n2p_call, tes_call, cpy_call;
    unsigned int eul_glob, vsc_glob, pup_glob, vup_glob, n2p_glob, tes_glob, cpy_glob;
    unsigned int eul_lock, vsc_lock, pup_lock, vup_lock, n2p_lock, tes_lock, cpy_lock, rsd_lock;

    double dux_gtime, lfx_gtime, scx_gtime, sgx_gtime, fux_gtime;
    double duy_gtime, lfy_gtime, scy_gtime, sgy_gtime, fuy_gtime;
    double duz_gtime, lfz_gtime, scz_gtime, sgz_gtime, fuz_gtime;

    double dux_stime, lfx_stime, scx_stime, sgx_stime, fux_stime;
    double duy_stime, lfy_stime, scy_stime, sgy_stime, fuy_stime;
    double duz_stime, lfz_stime, scz_stime, sgz_stime, fuz_stime;

    unsigned int dux_glob, lfx_glob, scx_glob, sgx_glob, fux_glob;
    unsigned int duy_glob, lfy_glob, scy_glob, sgy_glob, fuy_glob;
    unsigned int duz_glob, lfz_glob, scz_glob, sgz_glob, fuz_glob;

    unsigned int dux_call, lfx_call, scx_call, sgx_call, fux_call;
    unsigned int duy_call, lfy_call, scy_call, sgy_call, fuy_call;
    unsigned int duz_call, lfz_call, scz_call, sgz_call, fuz_call;

    unsigned int dux_lock, lfx_lock, scx_lock, sgx_lock, fux_lock;
    unsigned int duy_lock, lfy_lock, scy_lock, sgy_lock, fuy_lock;
    unsigned int duz_lock, lfz_lock, scz_lock, sgz_lock, fuz_lock;

    double p0, mu0, cppr, cpmcv, Tref, Ssu, SsuTref;
    double gm1, gm1_over_c, gm1_over_cpmcv;
    double xnu_n, xnu_0, rsd;

    double * odx;
    double * ody;
    double * odz;
    double * odx_v;
    double * ody_v;
    double * odz_v;
    double * odxdt;
    double * odydt;
    double * odzdt;
    double * odxdt_v;
    double * odydt_v;
    double * odzdt_v;
    double * odxdtrk;
    double * odydtrk;
    double * odzdtrk;
    double * odxdtrk_v;
    double * odydtrk_v;
    double * odzdtrk_v;
    unsigned int * P3x;
    unsigned int * P3y;
    unsigned int * P3z;
    unsigned int * P5x;
    unsigned int * P5y;
    unsigned int * P5z;
    unsigned int * P11x;
    unsigned int * P11y;
    unsigned int * P11z;

    double * r;
    double * ru;
    double * rv;
    double * rw;
    double * re;
    double * p;
    double * Tk;
    double * E;
    double * Eu;
    double * Ev;
    double * Ew;
    double * Ee;
    double * F;
    double * Fu;
    double * Fv;
    double * Fw;
    double * Fe;
    double * G;
    double * Gu;
    double * Gv;
    double * Gw;
    double * Ge;
    double * K;
    double * Ku;
    double * Kv;
    double * Kw;
    double * Ke;
    double * invJ;
    double * dx_du;
    double * dx_dv;
    double * dx_dw;
    double * dy_du;
    double * dy_dv;
    double * dy_dw;
    double * dz_du;
    double * dz_dv;
    double * dz_dw;
    double * tau11;
    double * tau22;
    double * tau33;
    double * tau12;
    double * tau13;
    double * tau23;
    double * wx;
    double * wy;
    double * wz;
} fields3d;

#endif