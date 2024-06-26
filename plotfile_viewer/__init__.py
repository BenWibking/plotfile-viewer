"""
plotfile-viewer

Usage
-----
See the class OpenPMDTimeSeries to open a set of plotfile files
"""
# Make the OpenPMDTimeSeries object accessible from outside the package
from .openpmd_timeseries import OpenPMDTimeSeries, FieldMetaInformation

# Define the version number
from .__version__ import __version__
__all__ = ['OpenPMDTimeSeries', 'FieldMetaInformation', '__version__']
