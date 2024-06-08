"""
This file is part of the plotfile-viewer.

It defines a function that can read standard parameters from an plotfile file.

Copyright 2015-2016, plotfile-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""
import builtins
if hasattr(builtins, 'amrex_spacedim'):
    from builtins import amrex_spacedim
    if amrex_spacedim == 2:
        import amrex.space2d as amr
    elif amrex_spacedim == 3:
        import amrex.space3d as amr
else: # default case
    import amrex.space3d as amr

import numpy as np


def read_plotfile_params(filename, iteration, extract_parameters=True):
    """
    Extract the time and some plotfile parameters from a file

    Parameter
    ---------
    filename: string
        The path to the file from which parameters should be extracted

    iteration : int
        The iteration at which to obtain the data

    extract_parameters: bool, optional
        Whether to extract all parameters or only the time
        (Function execution is faster when extract_parameters is False)

    Returns
    -------
    A tuple with:
    - A float corresponding to the time of this iteration in SI units
    - A dictionary containing several parameters, such as the geometry, etc.
      When extract_parameters is False, the second argument returned is None.
    """
    # Open the file, and do a version check
    f = amr.PlotFileData(filename)

    # Extract the time
    t = f.time()

    # If the user did not request more parameters, close file and exit
    if not extract_parameters:
        f.close()
        return(t, None)

    # Otherwise, extract the rest of the parameters
    params = {}

    # Find out supported plotfile extensions claimed by this file
    params['extensions'] = []

    # Find out whether fields are present and extract their metadata
    fields_available = False
    if f.nComp() > 0:
        fields_available = True
    if fields_available:
        params['avail_fields'] = []
        params['fields_metadata'] = {}

        # Loop through the available fields
        for field_name in f.varNames():
            metadata = {}

            if f.coordSys() == amr.CoordSys.cartesian:
                metadata['geometry'] = "cartesian"
            else:
                # unsupported geometry
                raise Exception("unsupported coordinate system!")
            
            metadata['type'] = 'scalar' # assume scalar components
            components = []
            metadata['avail_components'] = components

            # Check if this a 1d, 2d or 3d Cartesian
            if metadata['geometry'] == "cartesian":
                dim = f.spaceDim()
                if dim == 1:
                    metadata['geometry'] = "1dcartesian"
                    metadata['axis_labels'] = [ 'x' ]
                elif dim == 2:
                    metadata['geometry'] = "2dcartesian"
                    metadata['axis_labels'] = [ 'x', 'y' ]
                elif dim == 3:
                    metadata['geometry'] = "3dcartesian"
                    metadata['axis_labels'] = [ 'x', 'y', 'z' ]
                metadata['avail_circ_modes'] = []

            params['avail_fields'].append( field_name )
            params['fields_metadata'][field_name] = metadata

    else:
        params['avail_fields'] = None

    # Particles are currently not supported
    params['avail_species'] = None
    params['avail_record_components'] = None

    print("plotfile params: ", params)

    # Close the file and return the parameters
    return(t, params)

