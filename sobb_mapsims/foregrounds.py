import healpy as hp
import numpy as np
import pysm3
import pysm3.units as u
import argparse
import importlib.util
import os
import sobb_mapsims.instrument
from sobb_mapsims.utils import *
import toml

def fg_pawlaw(A, alpha, l0=80., lmax=512*3., return_cl=True):
    ell = np.arange(lmax-1)
    Dl = A*(ell/l0)**(alpha)
    if return_cl:
        Cl = Dl*2.*np.pi/ell/(ell+1)
        Cl[0:2] = 0
        return Cl
    else:
        Dl[0:2] = 0
        return Dl

def make_gaussian_fg(A_EE_BB, alpha_EE_BB, lmax=512*3, l0=80, Nside=512, seed=None):
    if seed:
        np.random.seed(seed)
    Cl_EE = fg_pawlaw(A_EE_BB[0], alpha_EE_BB[0])
    Cl_BB = fg_pawlaw(A_EE_BB[1], alpha_EE_BB[1])
    Cl = [Cl_EE*0., Cl_EE, Cl_BB, Cl_EE*0.]
    map_fg = hp.synfast(Cl, Nside, new=True)
    return map_fg

def write_gaussian_config_file(component, map_Q, map_U, file_name):
    print(file_name)
    if component == 'dust':
        fg_config = {}
        fg_config['dust_QUgaussian'] = {}
        fg_config['dust_QUgaussian']['class'] = "ModifiedBlackBody"
        fg_config['dust_QUgaussian']['map_I'] = "pysm_2/dust_t_new.fits"
        fg_config['dust_QUgaussian']['map_Q'] = map_Q
        fg_config['dust_QUgaussian']['map_U'] = map_U
        fg_config['dust_QUgaussian']['unit_I'] = "uK_RJ"
        fg_config['dust_QUgaussian']['unit_Q'] = "uK_RJ"
        fg_config['dust_QUgaussian']['unit_U'] = "uK_RJ"
        fg_config['dust_QUgaussian']['map_mbb_index'] = 1.54
        fg_config['dust_QUgaussian']['map_mbb_temperature'] = 20
        fg_config['dust_QUgaussian']['unit_mbb_temperature'] = "K"
        fg_config['dust_QUgaussian']['freq_ref_I'] = "545 GHz"
        fg_config['dust_QUgaussian']['freq_ref_P'] = "353 GHz"
    if component == 'synch':
        fg_config = {}
        fg_config['synch_QUgaussian'] = {}
        fg_config['synch_QUgaussian']['class'] = "PowerLaw"
        fg_config['synch_QUgaussian']['map_I'] = "pysm_2/synch_t_new.fits"
        fg_config['synch_QUgaussian']['map_Q'] = map_Q
        fg_config['synch_QUgaussian']['map_U'] = map_U
        fg_config['synch_QUgaussian']['unit_I'] = "uK_RJ"
        fg_config['synch_QUgaussian']['unit_Q'] = "uK_RJ"
        fg_config['synch_QUgaussian']['unit_U'] = "uK_RJ"
        fg_config['synch_QUgaussian']['map_pl_index'] = -3
        fg_config['synch_QUgaussian']['freq_ref_I'] = "408 MHz"
        fg_config['synch_QUgaussian']['freq_ref_P'] = "23 GHz"
    with open(file_name, 'w') as f:
        new_toml_string = toml.dump(fg_config, f)

def make_fg_sims(params):
    """ Write foreground maps on disk

    Parameters
    ----------
    params: module contating all the simulation parameters

    """
    parallel = params.parallel
    instr = getattr(sobb_mapsims.instrument, params.inst)
    nside = params.nside
    smooth = params.gaussian_smooth
    root_dir = params.out_dir
    if root_dir[0]=='.':
        pwd = os.getcwd()
        root_dir = root_dir.replace('.', pwd)
    out_dir = f'{root_dir}/foregrounds/'
    file_str = params.file_string
    channels = instr.keys()
    gaussian_fg = params.gaussian_fg
    nmc_fg = params.nmc_fg
    seed_fg = params.seed_fg
    if not nmc_fg:
        parallel = False
    fg_models = params.fg_models
    components = list(fg_models.keys())
    ncomp = len(components)
    rank = 0
    size = 1
    if parallel:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        rank_to_use = list(range(ncomp))
    if not os.path.exists(out_dir) and rank==0:
        os.makedirs(out_dir)
    if gaussian_fg and nmc_fg:
        nmc_fg = math.ceil(nmc_fg/size)*size
        if nmc_fg!=params.nmc_fg:
            print_rnk0(f'WARNING: setting nmc_fg = {nmc_fg}', rank)
        perrank = nmc_fg//size
    else:
        perrank = 1
    for ncp, cmp in enumerate(components):
        if not os.path.exists(out_dir+cmp) and rank==0:
            os.makedirs(out_dir+cmp)
        write_dir = out_dir+cmp+'/'
        fg_config_file_name = fg_models[cmp]
        if ('so' in fg_config_file_name) or ('pysm' in fg_config_file_name):
            fg_config_file_path = os.path.join(
                os.path.dirname(__file__), 'fg_models/')
            fg_config_file = f'{fg_config_file_path}/{fg_config_file_name}'
        else:
            fg_config_file = f'{fg_config_file_name}'
        for nmc in range(rank*perrank, (rank+1)*perrank):
            if gaussian_fg:
                nmc_str = str(nmc).zfill(4)
                if seed_fg:
                    seed_fg_mc = seed_fg+nmc+ncp*1002
                    print(cmp, nmc, seed_fg_mc)
                if nmc_fg:
                    if not os.path.exists(out_dir+cmp+'/'+nmc_str):
                        os.makedirs(out_dir+cmp+'/'+nmc_str)
                    write_dir = out_dir+cmp+'/'+nmc_str
                    if cmp=='dust':
                        A_EE_BB=[56., 28]
                        alpha_EE_BB=[-0.32, -0.16]
                    if cmp=='synch':
                        A_EE_BB=[9., 1.6]
                        alpha_EE_BB=[-0.7, -0.93]
                    fg_temp = make_gaussian_fg(A_EE_BB, alpha_EE_BB, Nside=nside, seed=seed_fg_mc)
                    file_name_Q = f'{cmp}_{nmc_str}_{file_str}_Q.fits'
                    file_name_U = f'{cmp}_{nmc_str}_{file_str}_U.fits'
                    file_path_Q = f'{write_dir}/{file_name_Q}'
                    file_path_U = f'{write_dir}/{file_name_U}'
                    hp.write_map(file_path_Q, fg_temp[1], overwrite=True, dtype=np.float32)
                    hp.write_map(file_path_U, fg_temp[2], overwrite=True, dtype=np.float32)
                    fg_config_file_name =  f'{write_dir}/{cmp}_{nmc_str}_gauss.cfg'
                    write_gaussian_config_file(cmp, file_path_Q, file_path_U, fg_config_file_name)
                    fg_config_file = fg_config_file_name
            sky = pysm3.Sky(nside=nside, component_config=fg_config_file)
            for chnl in channels:
                freq = instr[chnl]['freq']
                fwhm = instr[chnl]['beam']
                if params.band_int:
                    band = instr[chnl]['freq_band']
                    fmin = freq-band/2.
                    fmax = freq+band/2.
                    fsteps = fmax-fmin+1
                    bandpass_frequencies = np.linspace(fmin, fmax, fsteps) * u.GHz
                    weights = np.ones(len(bandpass_frequencies))
                    sky_extrap = sky.get_emission(bandpass_frequencies, weights)
                    sky_extrap = sky_extrap*bandpass_unit_conversion(bandpass_frequencies, weights, u.uK_CMB)
                else:
                    sky_extrap = sky.get_emission(freq*u.GHz)
                    sky_extrap = sky_extrap.to(u.uK_CMB, equivalencies=u.cmb_equivalencies(freq*u.GHz))
                if smooth:
                    sky_extrap_smt = hp.smoothing(sky_extrap, fwhm = np.radians(fwhm/60.), verbose=False)
                else:
                    sky_extrap_smt = sky_extrap
                file_name = f'{chnl}_{cmp}_{file_str}.fits'
                if nmc_fg:
                    file_name = f'{chnl}_{cmp}_{nmc_str}_{file_str}.fits'
                file_tot_path = f'{write_dir}/{file_name}'
                hp.write_map(file_tot_path, sky_extrap_smt, overwrite=True, dtype=np.float32)
