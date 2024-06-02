"""
This file is part of the plotfile-viewer.

It defines a number of helper functions that are used in main.py

Copyright 2015-2017, plotfile-viewer contributors
Authors: Remi Lehe, Richard Pausch
License: 3-Clause-BSD-LBNL
"""

import copy
import numpy as np

def sanitize_slicing(slice_across, slice_relative_position):
    """
    Return standardized format for `slice_across` and `slice_relative_position`:
    - either `slice_across` and `slice_relative_position` are both `None` (no slicing)
    - or `slice_across` and `slice_relative_position` are both lists,
    with the same number of elements

    Parameters
    ----------
    slice_relative_position : float, or list of float, or None

    slice_across : str, or list of str, or None
       Direction(s) across which the data should be sliced
    """
    # Skip None and empty lists
    if slice_across is None or slice_across == []:
        return None, None

    # Convert to lists
    if not isinstance(slice_across, list):
        slice_across = [slice_across]
    if slice_relative_position is None:
        slice_relative_position = [0]*len(slice_across)
    if not isinstance(slice_relative_position, list):
        slice_relative_position = [slice_relative_position]
    # Check that the length are matching
    if len(slice_across) != len(slice_relative_position):
        raise ValueError(
            'The argument `slice_relative_position` is erroneous: \nIt should have'
            'the same number of elements as `slice_across`.')

    # Return a copy. This is because the rest of the `plotfile-viewer` code
    # sometimes modifies the objects returned by `sanitize_slicing`.
    # Using a copy avoids directly modifying objects that the user may pass
    # to this function (and live outside of plotfile-viewer, e.g. directly in
    # a user's notebook)
    return copy.copy(slice_across), copy.copy(slice_relative_position)

def apply_selection(iteration, data_reader, data_list,
                    select, species, extensions):
    """
    Select the elements of each particle quantities in data_list,
    based on the selection rules in `select`

    Parameters
    ----------
    iteration: int
        The iteration at which to apply the selection

    data_reader: a DataReader object
        Contains the method that read particle data

    data_list: list of 1darrays
        A list of arrays with one element per macroparticle, that represent
        different particle quantities

    select: dict
        A dictionary of rules to select the particles
        'x' : [-4., 10.]   (Particles having x between -4 and 10)
        'ux' : [-0.1, 0.1] (Particles having ux between -0.1 and 0.1 mc)
        'uz' : [5., None]  (Particles with uz above 5 mc)

    species: string
       Name of the species being requested

    extensions: list of strings
        The extensions that the current OpenPMDTimeSeries complies with

    Returns
    -------
    A list of 1darrays that correspond to data_list, but were only the
    macroparticles that meet the selection rules are kept
    """
    # Create the array that determines whether the particle
    # should be selected or not.
    Ntot = len(data_list[0])
    select_array = np.ones(Ntot, dtype='bool')

    # Loop through the selection rules, and aggregate results in select_array
    for quantity in select.keys():
        q = data_reader.read_species_data(
            iteration, species, quantity, extensions)
        # Check lower bound
        if select[quantity][0] is not None:
            select_array = np.logical_and(
                select_array,
                q > select[quantity][0])
        # Check upper bound
        if select[quantity][1] is not None:
            select_array = np.logical_and(
                select_array,
                q < select[quantity][1])

    # Use select_array to reduce each quantity
    for i in range(len(data_list)):
        if len(data_list[i]) > 1:  # Do not apply selection on scalar records
            data_list[i] = data_list[i][select_array]

    return(data_list)


def try_array( L ):
    """
    Attempt to convert L to a single array.
    """
    try:
        # Stack the arrays
        return np.stack( L, axis=0 )
    except ValueError:
        # Do not stack
        return L


def fit_bins_to_grid( hist_size, grid_size, grid_range ):
    """
    Given a tentative number of bins `hist_size` for a histogram over
    the range `grid_range`, return a modified number of bins `hist_size`
    and a modified range `hist_range` so that the spacing of the histogram
    bins is an integer multiple (or integer divisor) of the grid spacing.

    Parameters:
    ----------
    hist_size: integer
        The number of bins in the histogram along the considered direction

    grid_size: integer
        The number of cells in the grid

    grid_range: list of floats (in)
        The extent of the grid

    Returns:
    --------
    hist_size: integer
        The new number of bins

    hist_range: list of floats
        The new range of the histogram
    """
    # The new histogram range is the same as the grid range
    hist_range = grid_range

    # Calculate histogram tentative spacing, and grid spacing
    hist_spacing = ( hist_range[1] - hist_range[0] ) * 1. / hist_size
    grid_spacing = ( grid_range[1] - grid_range[0] ) * 1. / grid_size

    # Modify the histogram spacing, so that either:
    if hist_spacing >= grid_spacing:
        # - The histogram spacing is an integer multiple of the grid spacing
        hist_spacing = int( hist_spacing / grid_spacing ) * grid_spacing
    else:
        # - The histogram spacing is an integer divisor of the grid spacing
        hist_spacing = grid_spacing / int( grid_spacing / hist_spacing )

    # Get the corresponding new number of bins, and the new range
    hist_size = int( ( hist_range[1] - hist_range[0] ) / hist_spacing )
    hist_range[1] = hist_range[0] + hist_size * hist_spacing

    return( hist_size, hist_range )

