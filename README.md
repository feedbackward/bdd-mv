# bdd-mv: mean-variance minimization using bi-directional dispersion functions

In this repository, we provide software and demonstrations related to the following paper:

- <a href="https://arxiv.org/abs/2301.11584">Robust variance-regularized risk minimization with concomitant scaling</a>. Matthew J. Holland. Preprint.

This repository contains code which can be used to faithfully reproduce all the experimental results given in the above paper, and it can be easily applied to more general machine learning tasks outside the examples considered here.


A table of contents for this README file:

- <a href="#setup_init">Setup: initial software preparation</a>
- <a href="#setup_data">Setup: preparing the benchmark data sets</a>
- <a href="#start">Getting started</a>
- <a href="#demos">Demos and visualization</a>
- <a href="#safehash">Safe hash value</a>


<a id="setup_init"></a>
## Setup: initial software preparation

To begin, please ensure you have the <a href="https://github.com/feedbackward/mml#prerequisites">prerequisite software</a> used in the setup of our `mml` repository.

Next, make a local copy of the repository and create a virtual environment for working in as follows:

```
$ git clone https://github.com/feedbackward/mml.git
$ git clone https://github.com/feedbackward/bdd-mv.git
$ conda create -n bdd-mv python=3.9 jupyter matplotlib pip pytables scikit-learn scipy unzip
$ conda activate bdd-mv
```

Having made (and activated) this new environment, we would like to use `pip` to install the supporting libraries for convenient access. This is done easily, by simply running

```
(bdd-mv) $ cd [mml path]/mml
(bdd-mv) $ pip install -e ./
```

with the `[mml path]` placeholder replaced with the path to wherever you placed the repositories. If you desire a safe, tested version of `mml`, just run

```
(bdd-mv) $ git checkout [safe hash mml]
```

and then do the `pip install -e ./` command mentioned above. The `[safe hash mml]` placeholder is to be replaced using the safe hash value given at the end of this document.


<a id="setup_data"></a>
## Setup: preparing the benchmark data sets

Please follow the instructions under <a href="https://github.com/feedbackward/mml#data">"Acquiring benchmark datasets"</a> using our `mml` repository. The rest of this README assumes that the user has prepared any desired benchmark datasets, stored in a local data storage directory (default path is `[path to mml]/mml/mml/data` as specified by the variable `dir_data_towrite` in `mml/mml/config.py`.

One __important__ step is to ensure that once you've acquired the benchmark data using `mml`, you must ensure that `bdd` knows where that data is. To do this, set `dir_data_toread` in `setup_data.py` to the directory housing the HDF5 format data sub-directories (default setting: your home directory).


<a id="start"></a>
## Getting started

We have basically three types of files:

- __Setup files:__ these take the form `setup_*.py`.
  - Configuration for all elements of the learning process, with one setup file for each of the following major categories: learning algorithms, data preparation, learned model evaluation, loss functions, models, result processing, and general-purpose training functions.

- __Driver scripts:__ just one at present, called `learn_driver.py`.
  - This script controls the flow of the learning procedure and handle all the clerical tasks such as organizing, naming, and writing numerical results to disk. No direct modification to this file is needed to run the experiments in the above paper.

- __Execution scripts:__ all the files of the form `run_*.sh`.
  - The choice of algorithm, model, data generation protocol, among other key parameters is made within these simple shell scripts. Basically, parameters are specified explicitly, and these are then passed to the driver script as options.

The experiments using real-world datasets require the user to run the driver scripts themselves; all the other experiments are self-contained within Jupyter notebooks.


### A quick example

This example uses `run.sh` and `run_common.sh` to execute tests with pre-fixed settings for multiple risk classes and multiple datasets.

```
(bdd-mv) bash run.sh adult australian cifar10 fashion_mnist
```

Of course, the above examples assume the user has (via `mml` or some other route) already obtained the datasets (`adult`, `australian`, `cifar10`, `fashion_mnist`) being specified, and that `setup_data.py` has been modified such that the program knows where to find the data.


<a id="demos"></a>
## List of demos

This repository includes detailed demonstrations to walk the user through re-creating the results in the paper cited at the top of this document. Below is a list of demo links which give our demos (constructed in Jupyter notebook form) rendered using the useful <a href="https://github.com/jupyter/nbviewer">nbviewer</a> service.

- <a href="https://nbviewer.jupyter.org/github/feedbackward/bdd-mv/blob/main/bdd-mv/sun_huber.ipynb">Examining the Sun-Huber dispersion function</a> (sections 2 and 3 in paper)
- <a href="https://nbviewer.jupyter.org/github/feedbackward/bdd-mv/blob/main/bdd-mv/2D_classification.ipynb">2D classification tests using simulated data</a> (section 4.1 in paper)
- <a href="https://nbviewer.jupyter.org/github/feedbackward/bdd-mv/blob/main/bdd-mv/real_data.ipynb">Tests using real data benchmarks</a> (section 4.2 in paper)


<a id="safehash"></a>
## Safe hash value

- Replace `[safe hash mml]` with `30b0f2be3f4b755c4ac9b1170883d983dc93a5fd`.

__Date of safe hash test:__ 2023/01/27.
