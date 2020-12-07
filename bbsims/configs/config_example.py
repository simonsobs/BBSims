#general configuration
parallel = False

#output maps parameters
nside = 256
gaussian_smooth = False
band_int = True
#save_coadd = False

#noise configuration
make_noise = True
sensitivity_mode = -1
one_over_f = 1
use_hits = False
#f_sky = 0.1
nmc_noise = 2
seed_noise = 6437
N_split = False

# #cmb configuration
make_cmb = True
#cmb_ps_file = ''
cmb_r = 0
nmc_cmb = 2
seed_cmb = 38198

# #foregrund configuration
make_fg = True
gaussian_fg = False
nmc_fg = 2
seed_fg = 3213
fg_models = {
    "dust": 'pysm_dust_0.cfg',
    "synch": 'pysm_synch_0.cfg',
    }

#output options
out_dir = './test_band'
file_string = 'test'
