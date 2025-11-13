"""
This file is part of the plotfile-viewer.

It defines a set of helper data and functions which
are used by the other files.

Copyright 2015-2016, plotfile-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""
import numpy as np
import pathlib
import glob
import re

def list_files(path_to_plotfiles):
    """
    Return a list of the AMReX plotfiles in this directory,
    and a list of the corresponding iterations

    Parameter
    ---------
    path_to_dir : string
        The path to the plotfile. Glob syntax is used to specify multiple plotfiles,
        e.g. plt* will load all files matching the glob pattern.
        (To correctly extract the cycle, each filename must end with "plt[0-9]*".)
    
    Returns
    -------
    A tuple with:
    - an array of integers which correspond to the iteration of each file
    - a dictionary that matches iterations to the corresponding filename
    """

    # Select the plot files, and fill dictionary of correspondence
    # between iterations and files
    iteration_to_file = {}

    # Match only the paths that end with "plt[0-9]*"
    my_regex = re.compile("plt[0-9]*$")  # compile the regular expression
    
    for path_string in glob.glob(path_to_plotfiles):
        plotfile_path = pathlib.Path(path_string)
        if plotfile_path.is_dir() and my_regex.search(plotfile_path.name):
            full_name = str(plotfile_path.absolute())
            # extract cycle count
            match = my_regex.search(plotfile_path.name)
            key_iteration = match[0][3:] # remove prefix "plt"
            # Add iteration to dictionary
            iteration_to_file[ int(key_iteration) ] = full_name

    # Extract iterations and sort them
    iterations = np.array( sorted( list( iteration_to_file.keys() ) ) )
    print(iteration_to_file)

    return iterations, iteration_to_file


def get_data(dfile, field=None, i_slice=None, pos_slice=None, output_type=None):
    """
    Extract the data from a (possibly constant) dataset
    Slice the data according to the parameters i_slice and pos_slice

    Parameters:
    -----------
    dset: a pyAMReX PlotFileData object
        The object from which the data is extracted

    pos_slice: int or list of int, optional
        Slice direction(s).
        When None, no slicing is performed

    i_slice: int or list of int, optional
       Indices of slices to be taken.

    output_type: a numpy type
       The type to which the returned array should be converted

    Returns:
    --------
    An np.ndarray (non-constant dataset) or a single double (constant dataset)
    """
    probDomain = dfile.probDomain(0)
    alldata = []

    if field is not None:
        mfdata = dfile.get(0, field)
        alldata = np.zeros((probDomain.big_end - probDomain.small_end + 1))
    else:
        mfdata = dfile.get(0)
        alldata = np.zeros((probDomain.big_end - probDomain.small_end + 1) + (dfile.nComp(),))

    for mfi in mfdata:
        bx = mfi.tilebox()
        marr = mfdata.array(mfi)
        marr_xp = marr.to_xp()
        
        if len(bx.small_end) == 2:
            # 2D plotfile
            i_s, j_s = tuple(bx.small_end)
            i_e, j_e = tuple(bx.big_end)
            if field is not None:
                alldata[i_s : i_e + 1, j_s : j_e + 1] = marr_xp[:, :, 0, 0]
            else:
                alldata[i_s : i_e + 1, j_s : j_e + 1, :] = marr_xp[:, :, 0, :]
        elif len(bx.small_end) == 3:
            # 3D plotfile
            i_s, j_s, k_s = tuple(bx.small_end)
            i_e, j_e, k_e = tuple(bx.big_end)
            if field is not None:
                alldata[i_s : i_e + 1, j_s : j_e + 1, k_s : k_e + 1] = marr_xp[:, :, :, 0]
            else:
                alldata[i_s : i_e + 1, j_s : j_e + 1, k_s : k_e + 1, :] = marr_xp[:, :, :, :]
        else:
            raise Exception("unsupported dimension!")

    data = []
    if pos_slice is None:
        data = alldata
    else:
        # Get largest element of pos_slice
        max_pos = max(pos_slice)
        # Create list of indices list_index of type
        # [:, :, :, ...] where Ellipsis starts at max_pos + 1
        list_index = [np.s_[:]] * (max_pos + 2)
        list_index[max_pos + 1] = np.s_[...]
        # Fill list_index with elements of i_slice
        for count, dir_index in enumerate(pos_slice):
            list_index[dir_index] = i_slice[count]
        # Convert list_index into a tuple
        tuple_index = tuple(list_index)
        # Slice dset according to tuple_index
        data = alldata[tuple_index]

    # Convert to the right type
    if (output_type is not None) and (data.dtype != output_type):
        data = data.astype( output_type )

    return data
