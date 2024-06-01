.. plotfile-viewer documentation master file, created by
   sphinx-quickstart on Thu Jan 30 10:48:39 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

plotfile-viewer documentation
============================

``plotfile-viewer`` contains a set of tools to load and visualize the
contents of a set of `plotfile <http://www.openpmd.org/#/start>`_ files
(typically, a timeseries).

The routines of ``plotfile-viewer`` can be used in two ways:

   - Using the **Python API**, in order to write a script that loads the data and produces a set of pre-defined plots.

   - Using the **interactive GUI inside a Jupyter Notebook**, in order to interactively visualize the data.


Installation
------------

You can install plotfile-viewer with ``pip`` using:
::

   pip install openpmd-viewer

or alternatively with ``conda`` using:
::

   conda install -c conda-forge openpmd-viewer

Usage
-----

The notebooks in the section :doc:`tutorials/tutorials` demonstrate how to use both
the API and the interactive GUI.

If you wish to use the **interactive GUI**, the installation of
``plotfile-viewer`` provides a convenient executable which automatically
**creates a new pre-filled notebook** and **opens it in a
browser**. To use this executable, simply type in a regular terminal:

::

   plotfile_notebook

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   tutorials/tutorials
   api_reference/api_reference