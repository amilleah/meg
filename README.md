# MEG Data Processing Pipeline

This pipeline processes KIT-NYU MEG data from raw recordings through source space analysis and statistical testing. It includes preprocessing with artifact removal, aligment with metadata, source reconstruction using dynamic Statistical Parametric Mapping (dSPM), and spatio-temporal cluster analysis for group-level statistics.

## Analysis Pipeline

### Preprocessing Steps
1. **Filtering**: 1-40 Hz bandpass filter
2. **Bad Channel Interpolation**: Spherical spline interpolation
3. **ICA**: FastICA with 95% variance explained
4. **Epoching**: Event-locked time windows with metadata
5. **Artifact Rejection**: Amplitude-based epoch rejection

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
# Create virtual environment
python -m venv meg_env
source meg_env/bin/activate  # On Windows: meg_env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Preprocessing (`preprocessing.ipynb`)
Processes raw MEG data through filtering, artifact removal, and epoching

**Parameters:**
- Bandpass filter: 1-40 Hz
- Epoch window: -900 to 800 ms
- Baseline: -900 to -800 ms
- Rejection threshold: 3 pT for magnetometers

### Source Analysis (`rmANOVA.ipynb`)
Performs source localization and statistical analysis

**Source Parameters:**
- SNR: 3.0 (λ² = 0.111)
- Method: dynamic Statistical Parametric Mapping (dSPM)
- Source space: ico-4 (2562 vertices per hemisphere)

## Configuration

Key parameters can be modified in the configuration cells:

```python
# Experiment settings
EXPERIMENT_NAME = 'experiment'
subjects = [f'subject_{i:03d}' for i in range(1, 21)]

# Event mapping
EVENT_MAPPING = {
    'condition_1': 160,
    'condition_2': 161,
    'condition_3': 162,
    'condition_4': 163,
}

# Analysis parameters
SEARCH_TMIN = 0      # Analysis start (ms)
SEARCH_TMAX = 400    # Analysis end (ms)
HEMI = 'lh'          # Hemisphere ('lh', 'rh', or 'both')
USE_ROI = True       # ROI-based analysis
```

## Output

### Preprocessed Data
- `*-ica-raw.fif`: ICA-cleaned continuous data
- `*-ica-epo.fif`: Epoched data with metadata
- `*-cov.fif`: Noise covariance matrix

### Source Data
- `*_condition_dSPM`: Source time courses (STC files)
- Forward solutions, inverse operators

### Statistical Results
- Cluster statistics (F-values, p-values)
- Significant spatio-temporal clusters
- Pickled results for further analysis

## Prerequisites

Before running this pipeline, ensure you have:
1. Converted KIT .sqd files to MNE-compatible .fif format
2. Applied CALM noise reduction
3. Performed coregistration with anatomical MRI
4. Set up FreeSurfer subjects directory

## Citation

If you use this pipeline, please cite:
- MNE-Python: Gramfort et al. (2013, 2014)
- Cluster-based permutation testing: Maris & Oostenveld (2007)