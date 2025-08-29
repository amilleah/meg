## MEG data processing pipeline

Pipeline for KIT-NYU MEG data: preprocessing, source localization, and statistical testing.

### what's included

```
#--- data handling
preproc.ipynb                       # general MEG preprocessing script
rmANOVA.ipynb                       # uses condition mean source estimates

#--- miscellaneous
README.md                           # this document
helpers.py                          # functions for data handling and analysis
pyproject.toml                      # Python 3.11 and install requirements
```

### how to install

From the meg/ directory, you need a Python 3.11 env and requirements as defined in the `pyproject.toml`. 

Note: Python 3.11 is for eelbrain compatibility (used for `mne-kit-gui`, epoch rejection via gui, and single-trial regression analyses), preprocessing and rmANOVA only use MNE, but my workflow involves both interchangeably.

```
python3.11 -m venv .venv   
source .venv/bin/activate

pip install .
```

### preprocessing workflow

These scripts assume steps 1-3 are done through NYU's MEG system using `.sqd` recordings. 

1. 157-channel acquisition from KIT-NYU MEG system
2. Noise-reduction using CALM method (Adachi et al., 2001) in KIT-NYU MEG software application
3. `mne kit2fiff` GUI or command line to coregister fiducials and digitization with MEG recording 

The following steps use scripts in `meg/` and rely on MNE-compatible `.fif` format. For a more detailed description, you can look on our [lab wiki](https://stefanpophristic.github.io/wiki/).

4. 1-40 Hz filter (method='iir')
5. Bad channel interpolation and data annotation
6. ICA (method='fastica', n_components = 0.95) 

ICA components account for 95% of explained variance in sensor data.

7. Event-locked time windows with event metadata
8. Amplitude-based epoch rejection (3 pT for magnetometers), annotations also rejected

The following steps move from sensor space (MEG recording) to source space (source estimates of brain activity). These next steps assume you also have an MRI coregistered to the MEG data. This can also be with a template brain (like `fsaverage`). You need a Boundary Element Model (BEM) of your subject to proceed. 

9. Icosahedron (ico-4) surface source space
10. Forward model computation using a BEM of skull/brain boundary (one conduction layer for MEG)
11. Noise covariance matrix calculated from 100 ms of prestimulus blank screen (-100ms to 0 ms)
12. Inverse solution using minimum norm estimation with depth weighting of signal (method='dSPM')
13. Morphing subject data to fsaverage template space for comparison

Once the subject has an inverse solution, you can create evoked responses (by condition, by trial, by session) and save them as source estimates of brain activity, which can be used for statistical analysis.

### statistical analysis

We frequently conduct **spatiotemporal clustering** to MEG source estimate data. The MNE functions are interchangable for sensor and source data. The shape of the data is usually `(n_obs, n_time, n_space)`, where observations (obs) are subjects, conditions, or trials.

Ideally, you'd motivate your searches. You can change the spatial and time extent of the search. 

1. ROI Definition using Brodmann areas from PALS atlas as examples
2. Configurable analysis window

#### rmANOVA

1. Read source estimate data by condition into object X
2. Spatiotemporal clustering permutation test
3. rmANOVA on spatial/time extent
4. Visualization of significant clusters

### citation

If you use this pipeline, please cite:

* CALM Noise Reduction: Adachi, Y., Shimogawara, M., Higuchi, M., Haruta, Y., & Ochiai, M. (2001)
* MNE-Python: Gramfort et al. (2013, 2014)
* Cluster-based permutation testing: Maris & Oostenveld (2007)