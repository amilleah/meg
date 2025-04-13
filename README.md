### Scripts for MEG data collection, preprocessing, and visualization.

### Setup
1. Install [Anaconda](https://www.anaconda.com/) for environment management
2. Create environments:
    ```bash
    conda env create -f environments/eelbrain.yml  # Python 3.11.8, MNE 1.8.0, Eelbrain 0.39.11
    conda env create -f environments/py37.yml      # Python 3.7.11 for PsychoPy
    ```
### Usage examples
1. To run experiment `.py` scripts:
    ```bash
    # in repository root
    conda activate py37
    python "experiments/color_green/color_green.py"
    ```
    Enter GUI inputs, select OK \
    Follow instructions, use keyboard inputs 1 or 2 to respond.

2. For all `.ipynb` files (In a new terminal):
    ```bash
    # in repository root
    conda activate eelbrain
    jupyter notebook "preprocessing/0_preprocessing.ipynb"
    ```

### To-do:
Add `/analysis/` scripts
    - sensor space 
    - source space


