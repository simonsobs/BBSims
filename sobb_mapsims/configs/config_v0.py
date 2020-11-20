##### general configuration
parallel = False

##### define LiteBIRD instrument
inst = 'LB_v28'

##### output maps parameters
nside = 16
gaussian_smooth = True
save_coadd = False

##### noise configuration
make_noise = True
nmc_noise = 1
seed_noise = 9876
N_split = 3

##### cmb configuration
make_cmb = True
cmb_ps_file = False
cmb_r = 0.01
nmc_cmb = 1
seed_cmb = 1234

##### foregrund configuration
make_fg = True
fg_models = {
    "dust": 'lb_dust_0.cfg',
    "synch": 'lb_synch_0.cfg',
    "freefree": 'lb_freefree_0.cfg'
    }

##### output options
out_dir = '/Users/niki/Workspace/LiteBIRD/sky_sims/test'
file_string = 'test_v0'
