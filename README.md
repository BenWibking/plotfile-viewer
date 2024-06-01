# plotfile-viewer

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/BenWibking/plotfile-viewer/main?filepath=docs/source/tutorials%2F)

## Overview

The intended use case is to view a timeseries of 2D slices
produced by the [DiagFramePlane diagnostic](https://github.com/AMReX-Combustion/PelePhysics/blob/development/Source/Utility/Diagnostics/DiagFramePlane.cpp) output by [PeleLMeX](https://amrex-combustion.github.io/PeleLMeX/manual/html/LMeXControls.html#run-time-diagnostics) and [Quokka](https://quokka-astro.github.io/quokka/insitu_analysis.html#d-slices).

This package contains a set of tools to load and visualize the
contents of a timeseries of AMReX plotfiles (currently, 2D Cartesian plotfiles only).
We hope to support 3D Cartesian plotfiles in the future.

The routines of `plotfile-viewer` can be used in two ways :

- Use the **Python API**, in order to write a script that loads the
  data and produces a set of pre-defined plots.

- Use the **interactive GUI inside the Jupyter Notebook**, in order to interactively
visualize the data.

## Usage

### Tutorials

The notebooks in the folder `tutorials/` demonstrate how to use both
the API and the interactive GUI. You can view these notebooks online
[here](https://github.com/BenWibking/plotfile-viewer/tree/main/docs/source/tutorials).

Alternatively, you can even
[*run* our tutorials online](https://mybinder.org/v2/gh/BenWibking/plotfile-viewer/main?filepath=docs/source/tutorials%2F)!

You can also download and run these notebooks on your local computer
(when viewing the notebooks with the above link, click on `Raw` to be able to
save them to your local computer). In order to run the notebook on
your local computer, please install `plotfile-viewer` first (see
below), as well as `wget` (`pip install wget`).

### Notebook quick-starter

If you wish to use the **interactive GUI**, the installation of
`plotfile-viewer` provides a convenient executable which automatically
**creates a new pre-filled notebook** and **opens it in a
browser**. To use this executable, simply type in a regular terminal:

`plotfile_notebook`

(This executable is installed by default, when installing `plotfile-viewer`.)

## Installation

#### Installation with pip

You can also install `plotfile-viewer` using `pip`
```
git clone https://github.com/BenWibking/plotfile-viewer.git
cd plotfile-viewer
pip install -e .
```
In addition, if you wish to use the interactive GUI, please type
```
pip install jupyter
```
