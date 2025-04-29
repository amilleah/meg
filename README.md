### Scripts for MEG data collection, preprocessing, and visualization.

### Setup
1. Install [Anaconda](https://www.anaconda.com/) for environment management
2. Create environments:
    ```bash
    conda env create -f environments/eelbrain.yml  # Python 3.11.8, MNE 1.8.0, Eelbrain 0.39.11
    ```

### Preprocessing (What's included)
Please first refer to the MNE-Python documentation on [the typical workflow](https://mne.tools/stable/documentation/cookbook.html) and some introductory [tutorials](https://mne.tools/stable/auto_tutorials/intro/index.html) for MEG data handling. There's a lot you can do, this is just my typical workflow.

Everything must be done in the `eelbrain.yml` environment.

You can also check out our growing [wiki](https://stefanpophristic.github.io/wiki/) for troubleshooting and basic overviews of a typical preprocessing pipeline.

#### `preprocessing/0_preprocessing.ipynb`
1. 1-40 Hz band pass offline filtering
2. Consistently bad channels removed and interpolated
3. Data annotations for body movement or high-amplitude aperiodic noise
4. independent component analysis to remove biomagnetic components like heartbeat, eye blink
5. epoching of the data
6. visualization of sensor space data

#### `preprocessing/1_source_space.ipynb`
This calls a set of functions (Thanks, @nigelflower!) to compute **source time courses** or STCs for each condition in evoked data. It generates inverse operators based on a noise covariance matrix, estimated anatomical structures and a forward solution of dipole-generated sensor activity---please see [this link]() or [the wiki]() for more details. This script generally should not change aside from which evoked data you are turning into STCs (so paths, condition labels, epoch timing). 

#### `preprocessing/stc_plots.ipynb`
This is a plotting script for STCs. This is a good catch to make sure you've created stcs correctly (although, you should also visualize after creating epochs). This script should function as a walkthrough of language-related Brodmann areas that can help motivate ROI searches and statistical tests. 

### Analysis
#### sensor space
The `sensor_space.ipynb` includes basic visualization and clustering permutation test of epoched sensor data. It calculates global field power (GFP) across all sensors and runs 


#### source space
These are some very basic examples of how to analyze MEG data. I've written a paired t-test `ttests.ipynb` and a repeated measures ANOVA `rmANOVA.ipynb` script that each subset STCs by Brodmann areas and run their respective stats. In practice, these tests would be run on motivated ROIs and time windows (that can be larger), but I chose some language-related areas that work for a good first pass. 

You can generate results plots with `plot_clusters.ipynb`, but this is a somewhat bloated notebook. It loops through all significant clusters (or clusters below `p_thresh`) and generates the following:
1. cluster info printout 
2. cluster label with input to save to mri folder
3. timecourse from cluster label with `extract_label_timecourse`
4. barplots for average STCs within cluster time window
5. brain figure with lateral and ventral view, search area highlighted, and cluster spatial extent plotted
6. cluster F-statistic legend for brain plot
into a nicely formatted figure.

This generates everything you'd typically need when reporting MEG results by providing both spatial and time extents for clusters returned from statistical tests. It could easily be refactored into functions, but this has been good enough for my usage. Allows for quick visualization.