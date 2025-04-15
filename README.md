### Scripts for MEG data collection, preprocessing, and visualization.

### Setup
1. Install [Anaconda](https://www.anaconda.com/) for environment management
2. Create environments:
    ```bash
    conda env create -f environments/eelbrain.yml  # Python 3.11.8, MNE 1.8.0, Eelbrain 0.39.11
    ```
### Usage examples
1. For all `.ipynb` files (In a new terminal):
    ```bash
    # in repository root
    conda activate eelbrain
    jupyter notebook "preprocessing/0_preprocessing.ipynb"
    ```

### Preprocessing and Analysis (What's included)
Please first refer to the MNE-Python documentation on [the typical workflow](https://mne.tools/stable/documentation/cookbook.html) and some introductory [tutorials](https://mne.tools/stable/auto_tutorials/intro/index.html) for MEG data handling. There's a lot you can do, this is just my typical workflow.

Everything must be done in the `eelbrain.yml` environment.

You can also check out our growing [wiki](https://stefanpophristic.github.io/wiki/) for troubleshooting and basic overviews of our preprocessing pipeline.

#### `preprocessing/0_preprocessing.ipynb`
1. 1-40 Hz band pass offline filtering
2. Consistently bad channels removed and interpolated
3. Data annotations for body movement or high-amplitude aperiodic noise
4. independent component analysis to remove biomagnetic components like heartbeat, eye blink
5. epoching of the data
6. visualization of sensor space data

This is the part where you can either stay in **sensor space** (i.e., MEG sensor activity) or you move to **source space** (model of brain activity).

#### `analysis/sensor_space.ipynb`
This is a simple script for visualizing **sensor-level data** and running spatiotemporal clustering with a repeated measures ANOVA
1. import epochs and reshape
2. plot evoked (averaged epochs)
3. from epochs data (not evoked), run spatiotemporal clustering and ANOVA
4. visualize results

#### `preprocessing/1_source_space.ipynb`
This calls a set of functions (Thanks, @nigelflower!) to compute **source time courses** or STCs for each condition in epoched data. 

#### `preprocessing/stc_plots.ipynb`
This is a plotting script for STCs. This is a good catch to make sure you've created stcs correctly (although, you should also visualize after creating epochs)

#### `analysis/source_space.ipynb`
Once you have created STCs for your data, you are ready to analyze them. This uses the exact same test as the `sensor_space.ipynb` analysis script in this repo, it just takes a larger adjacency matrix and a source space model (fsaverage). It loads an ROI (region of interest) for you to subset the data by using `spatial_exclude`. 
