import litebird_sim as lbs

def from_net_to_sensitivity(net):
    yr = 3.
    duty_cycle = 0.85
    cr_loss = 0.95
    margin = 0.95
    sens = np.sqrt(4*np.pi*2*net**2/(yr*365*24*60*60*duty_cycle*cr_loss*margin))*(10800./np.pi)
    return sens

def read_imo(dir, release):
    imoflatfile = dir
    imo = lbs.Imo(imoflatfile)
    instruments = ['HFT', 'MFT', 'LFT']
    LB_inst = {}
    for instr in instruments:
        channels = imo.query("/releases/"+release+"/Satellite/"+instr+"/info").metadata['channel_names']
        for ch in channels:
            data_file = imo.query("/releases/"+release+"/Satellite/"+instr+"/"+ch+"/info")
            freq = data_file.metadata['bandcenter']
            freq_band = data_file.metadata['bandwidth']
            fwhm_arcmin = data_file.metadata['fwhm_arcmin']
            P_sens = data_file.metadata['pol_sensitivity_channel_uKarcmin']
            LB_inst[ch] = {'freq':freq, 'freq_band': freq_band, 'beam': fwhm_arcmin, 'P_sens': P_sens }
    return LB_inst
