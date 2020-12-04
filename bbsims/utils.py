import healpy as hp
import numpy as np
import argparse
import importlib.util
import os
import math
import pysm3
import pysm3.units as u

def print_rnk0(text, rank):
    if rank==0:
        print(text)

def from_sens_to_rms(sens, nside):
    rms = sens/hp.nside2resol(nside, arcmin=True)
    return rms

def bandpass_unit_conversion(freqs, weights, output_unit):
    freqs = pysm3.check_freq_input(freqs)
    weights_to_rj = (weights * u.uK_RJ).to_value(
            (u.Jy / u.sr), equivalencies=u.cmb_equivalencies(freqs * u.GHz)
        )
    weights_to_out = (weights * output_unit).to_value(
            (u.Jy / u.sr), equivalencies=u.cmb_equivalencies(freqs * u.GHz)
        )
    factor = np.trapz(weights_to_rj, freqs)/np.trapz(weights_to_out, freqs)
    return factor * u.Unit(u.Unit(output_unit) / u.uK_RJ)
