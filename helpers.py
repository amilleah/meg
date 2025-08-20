'''
script: helpers.py
last-updated: 2025-08
author: amilleah
project: github.com/amilleah/meg
purpose: constants, helper functions for applying filtering, ICA, and epoching to raw MEG data
'''


from os.path import join
import os, mne, pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne import f_mway_rm

#--- filepath constants

expt = 'experiment'
ROOT = '/path/to/ROOT'
DATA = join(ROOT, 'data')

raw_dir = join(DATA, 'raw')
meg_dir = join(DATA, 'meg')
log_dir = join(ROOT, 'logs')
subjects_dir = join(DATA, 'mri')
stc_dir = join(DATA, 'stc')
stats_dir = join(ROOT, 'stats')

#--- condition info

colors = {
    "1": "tab:blue",
    "2": "tab:orange",
    "3": "tab:red",
    "4": "tab:green",
}

conditions = list(colors.keys())
inflection_map = {'1': 160, '2': 161, '3': 162, '4': 163}
condition_map = {'5': 165, '6': 166}


#--- source space constants

SNR = 3                         # Usually the rule of thumb has been to set to 3 for ANOVAs, 2 for single trial analyses. 
method = "dSPM"                 # dynamic statistical parameter mapping (see MNE documentation)
fixed = True                    # set to True if you want signed data. this will make this command run: mne.convert_forward_solution(fwd, surf_ori=True)
lambda2 = 1.0 / SNR ** 2.0      # (see wiki)

#--- helper functions

def get_meg_data(subj, ica):
    subj_dir = join(meg_dir, subj)
    raw_fname = join(subj_dir, f"{subj}_{expt}-{ica}.fif")
    return mne.io.read_raw_fif(raw_fname, preload=True)


def get_log_file(subj):
    log_filename = join(log_dir, subj, f"{subj}_{expt}_logfile.csv") # some participants may use logfile_1.csv, be wary!
    return pd.read_csv(log_filename)


def save_meg_data(subj, raw, ica):
    subj_dir = join(meg_dir, subj)
    raw_fname = join(subj_dir, f"{subj}_{expt}-{ica}.fif")  #note: ica here can be any string, please conform to MNE conventions or it will yell at you
    raw.save(raw_fname)


#--- photodiode plotting + event shifting
# author: alicia parrish, graham flick

def apply_photodiode(subj, raw, pd_channel="MISC 021", max_plots=10):
    if pd_channel not in raw.info["ch_names"]:
        raise RuntimeError(f"channel {pd_channel} not found in {raw.info['ch_names']}")

    pd_idx = raw.ch_names.index(pd_channel)
    pd_data = raw.get_data()[pd_idx]

    events = mne.find_events(raw, min_duration=0.002)
    shifted_events = events.copy()

    plot_count = 0
    for c, tw in enumerate(events[:, 0]):
        tw = tw - raw.first_samp
        # baseline 100 samples before event (with 50-sample buffer)
        baseline = pd_data[tw - 150:tw - 50]
        blmean, blsd = np.mean(baseline), np.std(baseline)
        upperR = blmean + 20 * blsd
        window = pd_data[tw:tw + 300]

        # onset relative to tw
        above = np.where(window > upperR)[0]
        if len(above) == 0:
            continue
        onset = above[0]
        shifted_events[c, 0] = events[c, 0] + onset

        subj_dir = join(meg_dir, subj)
        fig_dir = os.path.join(subj_dir, "figures", "PD_Shift")
        os.makedirs(fig_dir, exist_ok=True)

        # only make a few plots total
        if plot_count < max_plots:
            plt.figure()
            plt.plot(pd_data[tw:tw + 400])
            plt.axvline(onset, ls="--", color="r")
            plt.title(f"{subj} trial {c}: shift {onset} samples")
            outpath = os.path.join(fig_dir, f"{subj}_{c}.png")
            plt.savefig(outpath, dpi=150)
            plt.close()
            plot_count += 1

    mean_shift = np.mean(shifted_events[:, 0] - events[:, 0])
    sd_shift = np.std(shifted_events[:, 0] - events[:, 0])
    print(f"shift applied: mean={mean_shift:.2f} samples, sd={sd_shift:.2f}")

    return shifted_events

#--- source space helper functions

def get_evokeds(subj, epochs):
    evokeds = {}
    conditions = epochs.metadata.Condition.unique() # get conditions from epochs metadata
    for condition in conditions:
        ep = epochs[epochs.metadata["Condition"]==condition].copy() # get condition trials from epochs
        print(len(ep))
        if len(ep) == 0:
            print(f"[{subj}] No epochs found for condition: {condition}")
            continue
        ev = ep.average()
        fig = ev.plot_joint(title=f"{subj} - {condition}")
        fig.savefig(f'{meg_dir}/{subj}/figures/evoked_{condition}_{subj}.png', dpi=300)
        plt.close(fig)
        evokeds[condition] = ev # add ev to evokeds
    return evokeds


def get_source_space(subj, src_fname, force_new=False):
    print ('generating source space...')
    if (not os.path.isfile(src_fname)) or force_new:
        print ('src for subj = %s does not exist, creating file...' % (subj))
        src = mne.setup_source_space(subject=subj, spacing='ico4', subjects_dir=subjects_dir)
        src.save(src_fname, overwrite=True)
        print ('done. file saved.')
    else:
        print('src for subj = %s already exists, loading file...' %subj)
        src = mne.read_source_spaces(src_fname)
        print('done.')
    return src      
    

def get_BEM(subj, bem_fname, force_new=False):
    bem = None
    print('getting bem')
    if (not os.path.isfile(bem_fname)) or force_new:
        print ('BEM for subj = %s does not exist, creating...' % (subj))
        conductivity = (0.3,) # for single layer (MEG)
        model = mne.make_bem_model(subject=subj, ico=4, conductivity=conductivity, subjects_dir=subjects_dir)
        bem = mne.make_bem_solution(model)
        mne.write_bem_solution(bem_fname, bem, overwrite=True)
        print ('done. file saved.')
    return bem


def get_forward_solution(subj, info, src, trans, bem_fname, force_new=False):
    print('getting forward solution')
    fwd_path = os.path.join(meg_dir, subj)
    fwd_fname = os.path.join(fwd_path, '%s-fwd.fif' %subj)
    if not os.path.exists(fwd_path):
        os.makedirs(fwd_path)
    if (not os.path.isfile(fwd_fname)) or force_new:
        print ('forward solution for subj = %s does not exist, creating file.' % (subj))
        fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem_fname, ignore_ref=True)
        mne.write_forward_solution(fwd_fname, fwd, overwrite=True)
        fwd = mne.read_forward_solution(fwd_fname)
        print ('done.')
    else:
        print('fwd for subj = %s already exists, loading file...' %subj)
        fwd = mne.read_forward_solution(fwd_fname)
        print('done.')
    return fwd


def get_covariance_matrix(subj, epochs, force_new=False):
    cov_fname = os.path.join(meg_dir, subj, '%s-cov.fif' %(subj))
    print ('Getting covariance')
    if (not os.path.isfile(cov_fname)) or force_new:
        print('cov for subj = %s does not exist, creating file.' % (subj))
        cov = None
        cov = mne.compute_covariance(epochs, tmin=-0.1, tmax=0, 
                                         method=['shrunk', 'diagonal_fixed', 'empirical'])
        cov.save(cov_fname, overwrite=True)
        print ('done. file saved.')
    else:
        print('cov for subj = %s exists, loading file...' % (subj))
        cov = mne.read_cov(cov_fname)
        print('done.')
    return cov


def get_inverse_operator(info, fwd, cov):
    print ('getting inverse operator')
    if fixed == True:
        fwd = mne.convert_forward_solution(fwd, surf_ori=True) # set surf_ori=False for unsigned data, the forward solution has a few different configs and assumptions... 
    # (see MNE documentation)
    # fixed=False: ignoring dipole direction, unsigned data
    inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=0.8, loose='auto', fixed=fixed) 
    lambda2 = 1.0 / SNR ** 2.0
    return inv, lambda2


def save_STC(stc_fsaverage, condition):
    stc_path = os.path.join(stc_dir, condition)
    if not os.path.exists(stc_path):
        os.mkdir(stc_path)
    stc_filename = os.path.join(stc_path, '%s_%s_dSPM' % (subj, condition))
    print(os.path.join(stc_dir, stc_filename))
    stc_fsaverage.save(os.path.join(stc_dir, stc_filename), overwrite=True)


def create_and_save_STCs(subj, evokeds, inv, lambda2):
    print ('%s: creating STCs...' % subj)
    morph = mne.compute_source_morph(src=inv["src"], subject_from=subj, subject_to="fsaverage", subjects_dir=subjects_dir)
    items = evokeds.items()
    for condition, evoked in items:
        stc = mne.minimum_norm.apply_inverse(evoked, inv, lambda2=lambda2, method="dSPM")
        stc_fsavg = morph.apply(stc)
        save_STC(stc_fsavg, condition)
    print(f"DONE CREATING STCS FOR {subj}")

#--- statistics helpers 

def get_stc(subject_id, condition):
    stc_fname = os.path.join(stc_dir, condition, f'{subject_id}_{condition}_dSPM')
    stc = mne.read_source_estimate(stc_fname, subject='fsaverage')
    return stc

def stat_fun(*args):
    return f_mway_rm(
        np.swapaxes(args, 1, 0), 
        factor_levels=factor_levels,
        effects=effects, 
        return_pvals=True
    )[0]
