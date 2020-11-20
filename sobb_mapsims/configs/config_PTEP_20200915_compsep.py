#general configuration
parallel = True

#define LiteBIRD instrument
inst = 'LB_IMOv1'

#output maps parameters
nside = 512
gaussian_smooth = False
band_int = False
save_coadd = False

#noise configuration
make_noise = True
nmc_noise = 100
seed_noise = 6437
hm_split = True

# #cmb configuration
make_cmb = True
#cmb_ps_file = 'Cls_Planck2018_for_PTEP_2020_r0.fits'
cmb_r = 0
nmc_cmb = 100
seed_cmb = 38198

# #foregrund configuration
make_fg = True
gaussian_fg = True
nmc_fg = 2
seed_fg = 3213
fg_models = {
    "dust": 'so_dust_gauss.cfg',
    "synch": 'so_synch_gauss.cfg',
    }

#output options
out_dir = './'
file_string = 'PTEP_20200915_compsep'
