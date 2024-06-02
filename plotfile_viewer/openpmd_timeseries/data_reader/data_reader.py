"""
This file is part of the plotfile-viewer

It routes the calls to the data reader to either
the h5py data reader, or to openpmd-api.

Copyright 2020, plotfile-viewer contributors
Authors: Remi Lehe
License: 3-Clause-BSD-LBNL
"""
import numpy as np
import os
import re

available_backends = []

try:
    from . import amrex_reader
    available_backends.append('amrex')
except ImportError:
    pass

if len(available_backends) == 0:
    raise ImportError('No pyAMReX backend found.\n'
        'Please install `pyAMReX`:\n'
        'e.g. with `pip install pyamrex`')

class DataReader( object ):
    """
    Class that performs various type of access the plotfile file.

    The methods of this class are agnostic of the actual backend package
    used in order to access the plotfile file (e.g. h5py or openpmd-api).
    The backend that is used in practice depends on which package is
    available on the current environment.
    """

    def __init__(self, backend):
        """
        Initialize the DataReader class.
        """
        self.backend = backend

        # Point to the correct reader module
        if self.backend == 'amrex':
            self.iteration_to_file = {}
        else:
            raise RuntimeError('Unknown backend: %s' % self.backend)

    def list_iterations(self, path_to_dir):
        """
        Return a list of the iterations that correspond to the files
        in this directory. (The correspondance between iterations and
        files is stored internally.)

        Parameter
        ---------
        path_to_dir : string
            The path to the directory where the hdf5 files are.

        Returns
        -------
        an array of integers which correspond to the iteration of each file
        (in sorted order)
        """
        if self.backend == 'amrex':
            iterations, iteration_to_file = \
                amrex_reader.list_files( path_to_dir )
            # Store dictionary of correspondence between iteration and file
            self.iteration_to_file = iteration_to_file
            if len(iterations) == 0:
                raise RuntimeError(
                    "Found no valid files in directory {0}.\n"
                    "Please check that this is the path to the plot files."
                    "Valid files must end with 'plt' followed by one or more digits."
                    .format(path_to_dir))

        return iterations

    def read_plotfile_params(self, iteration, extract_parameters=True):
        """
        Extract the time and some plotfile parameters from a file

        Parameter
        ---------
        iteration: int
            The iteration at which the parameters should be extracted

        extract_parameters: bool, optional
            Whether to extract all parameters or only the time
            (Function execution is faster when extract_parameters is False)

        Returns
        -------
        A tuple with:
        - A float corresponding to the time of this iteration in SI units
        - A dictionary containing several parameters, such as the geometry, etc
         When extract_parameters is False, the second argument returned is None
        """
        if self.backend == 'amrex':
            filename = self.iteration_to_file[iteration]
            return amrex_reader.read_plotfile_params(
                    filename, iteration, extract_parameters)

    def read_field_cartesian( self, iteration, field, coord, axis_labels,
                          slice_relative_position, slice_across ):
        """
        Extract a given field from an plotfile file in the plotfile format,
        when the geometry is cartesian (1d, 2d or 3d).

        Parameters
        ----------
        iteration : int
           The iteration at which to extract the fields

        field : string, optional
           Which field to extract

        coord : string, optional
           Which component of the field to extract

        axis_labels: list of strings
           The name of the dimensions of the array (e.g. ['x', 'y', 'z'])

        slice_across : list of str or None
           Direction(s) across which the data should be sliced
           Elements can be:
             - 1d: 'z'
             - 2d: 'x' and/or 'z'
             - 3d: 'x' and/or 'y' and/or 'z'
           Returned array is reduced by 1 dimension per slicing.

        slice_relative_position : list of float or None
           Number(s) between -1 and 1 that indicate where to slice the data,
           along the directions in `slice_across`
           -1 : lower edge of the simulation box
           0 : middle of the simulation box
           1 : upper edge of the simulation box

        Returns
        -------
        A tuple with
           F : a ndarray containing the required field
           info : a FieldMetaInformation object
           (contains information about the grid; see the corresponding docstring)
        """
        if self.backend == 'amrex':
            filename = self.iteration_to_file[iteration]
            return amrex_reader.read_field_cartesian(
                filename, iteration, field, coord, axis_labels,
                slice_relative_position, slice_across )


    def get_grid_parameters(self, iteration, avail_fields, metadata ):
        """
        Return the parameters of the spatial grid (grid size and grid range)
        in two dictionaries

        Parameters:
        -----------
        iteration: int
            The iteration at which to extract the parameters

        avail_fields: list
           A list of the available fields
           e.g. ['B', 'E', 'rho']

        metadata: dictionary
          A dictionary whose keys are the fields of `avail_fields` and
          whose values are dictionaries that contain metadata (e.g. geometry)

        Returns:
        --------
        A tuple with `grid_size_dict` and `grid_range_dict`
        Both objects are dictionaries, with their keys being the labels of
        the axis of the grid (e.g. 'x', 'y', 'z')
        The values of `grid_size_dict` are the number of gridpoints along
        each axis.
        The values of `grid_range_dict` are lists of two floats, which
        correspond to the min and max of the grid, along each axis.
        """
        if self.backend == 'amrex':
            filename = self.iteration_to_file[iteration]
            return amrex_reader.get_grid_parameters(
                filename, iteration, avail_fields, metadata )
 