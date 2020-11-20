import numpy as np

def sens(net):
    sens = np.sqrt(4*np.pi*2.*net**2./(3*365.*24*60*60*0.85*0.95*0.95))*(10800/np.pi)
    return sens


SAT_nominal = {}
SAT_nominal['SAT_40'] = {'freq': 40., 'freq_band': 12., 'beam': 70.5, 'P_sens': 37.42}
SAT_nominal['SAT_50'] = {'freq': 50., 'freq_band': 15., 'beam': 58.5, 'P_sens': 33.46}
SAT_nominal['SAT_60'] = {'freq': 60., 'freq_band': 14., 'beam': 51.1, 'P_sens': 21.31}
