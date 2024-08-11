salt_per_phosphate = -0.944;
salt_per_phosphate_hack = (0.368 * salt_per_phosphate) / 1000.;

dH_AA = -7.6;
dH_AT = -7.2;
dH_TA = -7.2;
dH_CA = -8.5;
dH_GT = -8.4;
dH_CT = -7.8;
dH_GA = -8.2;
dH_CG = -10.6;
dH_GC = -9.8;
dH_GG = -8.0;

dS_AA = -21.3 * 0.001;
dS_AT = -20.4 * 0.001;
dS_TA = -21.3 * 0.001;
dS_CA = -22.7 * 0.001;
dS_GT = -22.4 * 0.001;
dS_CT = -21.0 * 0.001;
dS_GA = -22.2 * 0.001;
dS_CG = -27.2 * 0.001;
dS_GC = -24.2 * 0.001;
dS_GG = -19.9 * 0.001;

dH_average = ( 2.*(dH_AA + dH_CA + dH_GT + dH_CT + dH_GA + dH_GG) + (dH_AT + dH_TA + dH_CG + dH_GC) ) / 16.;
dS_average = ( 2.*(dS_AA + dS_CA + dS_GT + dS_CT + dS_GA + dS_GG) + (dS_AT + dS_TA + dS_CG + dS_GC) ) / 16.;

dH_termAT = 2.2;
dS_termAT = 6.9 * 0.001;
dH_termCG = 0.0;
dS_termCG = 0.0 * 0.001;

dH_init = 0.2;
dS_init = -5.7 * 0.001;