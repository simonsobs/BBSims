import healpy as hp
import numpy as np
import argparse
import importlib.util
import os
import math
from bbsims.utils import *
import bbsims.V3_calc_public as sonc

def make_noise_sims(params):
    """ Write noise maps on disk

    Parameters
    ----------
    params: module contating all the simulation parameters

    """
    nmc_noise = params.nmc_noise
    nside = params.nside
    npix = hp.nside2npix(nside)
    root_dir = params.out_dir
    out_dir = f'{root_dir}/noise/'
    seed_noise = params.seed_noise
    ch_name = ['SO_SAT_27', 'SO_SAT_39', 'SO_SAT_93', 'SO_SAT_145', 'SO_SAT_225', 'SO_SAT_280']
    freqs = sonc.Simons_Observatory_V3_SA_bands()
    N_split = params.N_split
    file_str = params.file_string
    parallel = params.parallel
    one_over_f = params.one_over_f
    use_hits = params.use_hits
    sensitivity_mode = params.sensitivity_mode
    f_sky = params.f_sky
    rank = 0
    size = 1
    if parallel:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    if not os.path.exists(out_dir) and rank==0:
            os.makedirs(out_dir)
    nmc_noise = math.ceil(nmc_noise/size)*size
    if nmc_noise!=params.nmc_noise:
        print_rnk0(f'WARNING: setting nmc_noise = {nmc_noise}', rank)
    perrank = nmc_noise//size
    chnl_seed = 12
    if (use_hits==True) or (f_sky==False):
        hits_file = os.path.join(
            os.path.dirname(__file__),
            'datautils/norm_nHits_SA_35FOV_nside512.fits')
        hits_map = hp.read_map(hits_file)
        hits_map = hp.ud_grade(hits_map, nside)
        f_sky = np.mean(hits_map)
    if not use_hits:
        hits_map_sort = np.copy(hits_map)
        hits_map_sort = np.sort(hits_map_sort)
        hits_map_sort = hits_map_sort[::-1]
        el_thrs = round(len(hits_map_sort)*f_sky)
        min_hits = hits_map_sort[el_thrs]
        mask_binary = np.copy(hits_map)
        mask_binary[hits_map<min_hits] = 0
        mask_binary[hits_map>=min_hits] = 1
        f_sky = np.mean(mask_binary)
    ell, n_ell = sonc.Simons_Observatory_V3_SA_noise(sensitivity_mode,one_over_f,2,f_sky,nside*3,1)
    for nch, chnl in enumerate(ch_name):
            np.savez(f'{out_dir}/{chnl}_ell_n_ell_FULL_{file_str}.npz', ell=ell, n_ell=n_ell[nch])
            hp.write_map(f'{out_dir}/binary_mask.fits', mask_binary, overwrite=True, dtype=np.float32)
            chnl_seed += 67
            n_ell_ch_P = n_ell[nch]
            n_ell_ch_T = n_ell_ch_P/2.
            n_ell_ch = [n_ell_ch_T, n_ell_ch_P, n_ell_ch_P, n_ell_ch_P*0.]
            for nmc in range(rank*perrank, (rank+1)*perrank):
                if seed_noise:
                    np.random.seed(seed_noise+nmc+chnl_seed)
                nmc_str = str(nmc).zfill(4)
                if not os.path.exists(out_dir+nmc_str):
                        os.makedirs(out_dir+nmc_str)
                if N_split:
                    n_ell_ch_split = n_ell_ch*N_split
                    for hm in range(N_split):
                        noise_map_split = hp.synfast(n_ell_ch_split, nside, pol=True,new=True,verbose=False)
                        if use_hits:
                            noise_map_split /= np.sqrt(hits_map/np.amax(hits_map))
                        else:
                            noise_map_split = noise_map_split*mask_binary
                        noise_map += noise_map_split
                        file_name = f'{chnl}_noise_SPLIT_{hm+1}of{N_split}_{nmc_str}_{file_str}.fits'
                        file_tot_path = f'{out_dir}{nmc_str}/{file_name}'
                        noise_map_split[np.where(np.abs(noise_map_split)==float("inf"))] = 0
                        hp.write_map(file_tot_path, noise_map_split, overwrite=True, dtype=np.float32)
                else:
                    noise_map = hp.synfast(n_ell_ch, nside, pol=True,new=True,verbose=False)
                    if use_hits:
                        noise_map /= np.sqrt(hits_map/np.amax(hits_map))
                noise_map[np.where(np.abs(noise_map)==float("inf"))] = 0
                file_name = f'{chnl}_noise_FULL_{nmc_str}_{file_str}.fits'
                file_tot_path = f'{out_dir}{nmc_str}/{file_name}'
                hp.write_map(file_tot_path, noise_map, overwrite=True, dtype=np.float32)
