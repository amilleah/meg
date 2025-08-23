# MEG Data Processing Pipeline

Pipeline for KIT-NYU MEG data: preprocessing, source localization, and statistical testing.

## Analysis Pipeline

### Preprocessing Steps
1. **Filtering**: 1-40 Hz filter (method='iir')
2. **Bad Channel Interpolation**: Spherical spline interpolation
3. **ICA**: FastICA with 95% variance explained
4. **Epoching**: Event-locked time windows with metadata
5. **Artifact Rejection**: Amplitude-based epoch rejection (3 pT for magnetometers)

### Source Localization
1. **Source Space**: ico-4 surface source space
2. **Forward Model**: Boundary Element Method (BEM)
3. **Covariance**: Pre-stimulus noise covariance (-100 to 0 ms)
4. **Inverse Solution**: Minimum norm estimation with depth weighting
5. **Morphing**: Transform to fsaverage template

### Statistical Analysis
1. **ROI Definition**: Brodmann areas from PALS atlas
2. **Time Window**: Configurable analysis window
3. **Statistics**: Repeated measures ANOVA
4. **Clustering**: Spatio-temporal cluster permutation test
5. **Correction**: Family-wise error rate control

## Usage

### Installation

```bash
python -m venv meg_env
source meg_env/bin/activate
pip install -r requirements.txt
```

### Configuration and helper functions (`helpers.py`)
Used for preprocessing and source analysis 

### Preprocessing (`preproc.ipynb`)
Processes raw MEG data through filtering, artifact removal, and epoching

### Source Analysis (`rmANOVA.ipynb`)
Performs source localization and statistical analysis

**Source Parameters:**
- SNR: 3.0 (λ² = 0.111)
- Method: dynamic Statistical Parametric Mapping (dSPM)
- Source space: ico-4 (2562 vertices per hemisphere)

## Output

### Preprocessed Data
- `*-ica-raw.fif`: ICA-cleaned continuous data
- `*-ica-epo.fif`: Epoched data with metadata
- `*-cov.fif`: Noise covariance matrix

### Source Data
- `*_condition_dSPM`: Source time courses (STC files)
- `*-fwd.fif`: Forward solution
- `*-inv.fif`: Inverse model

### Statistical Results
- Cluster statistics (F-values, p-values)
- Significant spatio-temporal clusters
- Pickled results (`.pkl`) for further analysis and visualization

## Prerequisites

Before running this pipeline, ensure you have:
1. Converted KIT `.sqd` files to MNE-compatible `.fif` format
2. Applied CALM noise reduction
3. Performed coregistration with anatomical MRI
4. Set up FreeSurfer subjects directory

## Citation

If you use this pipeline, please cite:
- CALM Noise Reduction: Adachi, Y., Shimogawara, M., Higuchi, M., Haruta, Y., & Ochiai, M. (2001)
- MNE-Python: Gramfort et al. (2013, 2014)
- Cluster-based permutation testing: Maris & Oostenveld (2007)
