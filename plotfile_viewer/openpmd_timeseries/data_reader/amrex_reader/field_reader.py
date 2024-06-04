"""
This file is part of the plotfile-viewer.

It defines functions that can read the fields from an HDF5 file.

Copyright 2015-2016, plotfile-viewer contributors
Author: Remi Lehe
License: 3-Clause-BSD-LBNL
"""

import amrex.space2d as amr

import numpy as np
from .utilities import get_data
from plotfile_viewer.openpmd_timeseries.field_metainfo import FieldMetaInformation


def read_field_cartesian( filename, iteration, field, coord, axis_labels,
                          slice_relative_position, slice_across ):
    """
    Extract a given field from an HDF5 file in the plotfile format,
    when the geometry is cartesian (1d, 2d or 3d).

    Parameters
    ----------
    filename : string
       The absolute path to the HDF5 file

    iteration : int
        The iteration at which to obtain the data

    field : string, optional
       Which field to extract

    coord : string, optional
       Which component of the field to extract (unused)

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
    # Open the plot file
    dfile = amr.PlotFileData(filename)

    # Dimensions of the grid
    shape = dfile.probDomain(0)
    grid_spacing = dfile.cellSize(0)
    global_offset = dfile.probLo()
    position = [0, 0]

    # Current simulation time
    time = dfile.time()

    # Slice selection
    if slice_across is not None:
        # Get the integer that correspond to the slicing direction
        list_slicing_index = []
        list_i_cell = []
        for count, slice_across_item in enumerate(slice_across):
            slicing_index = axis_labels.index(slice_across_item)
            list_slicing_index.append(slicing_index)
            # Number of cells along the slicing direction
            n_cells = shape[ slicing_index ]
            # Index of the slice (prevent stepping out of the array)
            i_cell = int( 0.5 * (slice_relative_position[count] + 1.) * n_cells )
            i_cell = max( i_cell, 0 )
            i_cell = min( i_cell, n_cells - 1)
            list_i_cell.append(i_cell)

        # Remove metainformation relative to the slicing index
        # Successive pops starting from last coordinate to slice
        shape = [ x for index, x in enumerate(shape)
                  if index not in list_slicing_index ]
        grid_spacing = [ x for index, x in enumerate(grid_spacing)
                         if index not in list_slicing_index ]
        global_offset = [ x for index, x in enumerate(global_offset)
                          if index not in list_slicing_index ]
        axis_labels = [ x for index, x in enumerate(axis_labels)
                         if index not in list_slicing_index ]

        axes = { i: axis_labels[i] for i in range(len(axis_labels)) }

        # Extract data
        F = get_data( dfile, field, list_i_cell, list_slicing_index )

        info = FieldMetaInformation( axes, shape, grid_spacing, global_offset,
                1.0, position,
                time, iteration, component_attrs={}, field_attrs={} )
    else:
        F = get_data( dfile, field )
        axes = { i: axis_labels[i] for i in range(len(axis_labels)) }

        info = FieldMetaInformation( axes, F.shape,
            dfile.cellSize(0), dfile.probLo(),
            1.0, position,
            time, iteration, component_attrs={}, field_attrs={} )

    return F, info


def get_grid_parameters( filename, iteration, avail_fields, metadata ):
    """
    Return the parameters of the spatial grid (grid size and grid range)
    in two dictionaries

    Parameters:
    -----------
    filename : string
       The absolute path to the HDF5 file

    iteration : int
        The iteration at which to obtain the data

    avail_fields: list
       A list of the available fields
       e.g. ['B', 'E', 'rho']

    metadata: dictionary
      A dictionary whose keys are the fields of `avail_fields` and
      whose values are dictionaries that contain metadata (e.g. geometry)

    Returns:
    --------
    A tuple with `grid_size_dict` and `grid_range_dict`
    Both objects are dictionaries, with their keys being the labels of the axis
    of the grid (e.g. 'x', 'y', 'z')
    The values of `grid_size_dict` are the number of gridpoints along each axis
    The values of `grid_range_dict` are lists of two floats, which correspond
    to the min and max of the grid, along each axis.
    """
    # Open the plot file
    dfile = amr.PlotFileData(filename)

    # Extract relevant quantities
    labels = ['x', 'y']
    grid_spacing = dfile.cellSize(0)
    grid_offset = dfile.probLo()
    grid_size = dfile.probDomain(0)

    # Build the dictionaries grid_size_dict and grid_range_dict
    grid_size_dict = {}
    grid_range_dict = {}

    for i in range(len(labels)):
        coord = labels[i].decode()
        grid_size_dict[coord] = grid_size[i]
        grid_range_dict[coord] = \
            [ grid_offset[i], grid_offset[i] + grid_size[i] * grid_spacing[i] ]

    print("get_grid_params", grid_size_dict, grid_range_dict)

    return grid_size_dict, grid_range_dict
