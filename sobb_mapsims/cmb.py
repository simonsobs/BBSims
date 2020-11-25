import healpy as hp
import numpy as np
import argparse
import importlib.util
import os
import math
import pysm3
import pysm3.units as u
from sobb_mapsims.utils import *
import sobb_mapsims.V3_calc_public as sonc


def make_cmb_sims(params):
    """ Write cmb maps on disk

    Parameters
    ----------
    params: module contating all the simulation parameters

    """
    nmc_cmb = params.nmc_cmb
    nside = params.nside
    smooth = params.gaussian_smooth
    ch_name = ['SO_SAT_27', 'SO_SAT_39', 'SO_SAT_93', 'SO_SAT_145', 'SO_SAT_225', 'SO_SAT_280']
    freqs = sonc.Simons_Observatory_V3_SA_bands()
    beams = sonc.Simons_Observatory_V3_SA_beams()
    band_int = params.band_int
    parallel = params.parallel
    root_dir = params.out_dir
    out_dir = f'{root_dir}/cmb/'
    file_str = params.file_string
    seed_cmb = params.seed_cmb
    cmb_ps_file = params.cmb_ps_file
    rank = 0
    size = 1
    if params.parallel:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    if not os.path.exists(out_dir) and rank==0:
        os.makedirs(out_dir)
    if cmb_ps_file:
        print(cmb_ps_file)
        cl_cmb = hp.read_cl(cmb_ps_file)
    else:
        cmb_ps_scalar_file = os.path.join(
            os.path.dirname(__file__),
            'datautils/Cls_Planck2018_r0.fits')
        cl_cmb_scalar = hp.read_cl(cmb_ps_scalar_file)
        cmb_ps_tensor_r1_file = os.path.join(
            os.path.dirname(__file__),
            'datautils/Cls_Planck2018_tensor_r1.fits')
        cmb_r = params.cmb_r
        cl_cmb_tensor = hp.read_cl(cmb_ps_tensor_r1_file)*cmb_r
        cl_cmb = cl_cmb_scalar+cl_cmb_tensor
    nmc_cmb = math.ceil(nmc_cmb/size)*size
    if nmc_cmb!=params.nmc_cmb:
        print_rnk0(f'WARNING: setting nmc_cmb = {nmc_cmb}', rank)
    perrank = nmc_cmb//size
    for nmc in range(rank*perrank, (rank+1)*perrank):
        if seed_cmb:
            np.random.seed(seed_cmb+nmc)
        nmc_str = str(nmc).zfill(4)
        if not os.path.exists(out_dir+nmc_str):
            os.makedirs(out_dir+nmc_str)
        cmb_temp = hp.synfast(cl_cmb, nside, new=True, verbose=False)
        file_name = f'cmb_{nmc_str}_{file_str}.fits'
        file_tot_path = f'{out_dir}{nmc_str}/{file_name}'
        hp.write_map(file_tot_path, cmb_temp, overwrite=True, dtype=np.float32)
        os.environ["PYSM_LOCAL_DATA"] = f'{out_dir}'
        sky = pysm3.Sky(nside=nside, component_objects=[pysm3.CMBMap(nside, map_IQU=f'{nmc_str}/{file_name}')])
        for nch, chnl in enumerate(ch_name):
            freq = freqs[nch]
            fwhm = beams[nch]
            cmb_map = sky.get_emission(freq*u.GHz)
            cmb_map = cmb_map.to(u.uK_CMB, equivalencies=u.cmb_equivalencies(freq*u.GHz))
            if smooth:
                cmb_map_smt = hp.smoothing(cmb_map, fwhm = np.radians(fwhm/60.), verbose=False)
            else:
                cmb_map_smt = cmb_map
            file_name = f'{chnl}_cmb_{nmc_str}_{file_str}.fits'
            file_tot_path = f'{out_dir}{nmc_str}/{file_name}'
            hp.write_map(file_tot_path, cmb_map_smt, overwrite=True, dtype=np.float32)
