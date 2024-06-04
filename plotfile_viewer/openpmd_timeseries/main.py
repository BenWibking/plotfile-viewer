"""
This file is part of the plotfile-viewer.

It defines the main OpenPMDTimeSeries class.

Copyright 2015-2016, plotfile-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""

import numpy as np
from tqdm import tqdm
from .utilities import try_array, sanitize_slicing
from .plotter import Plotter
from .data_reader import DataReader, available_backends
from .interactive import InteractiveViewer, debug_view

class OpenPMDException(Exception):
    @debug_view.capture(clear_output=True)
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(OpenPMDException, self).__init__(message)
        print(self)

class OpenPMDTimeSeries(InteractiveViewer):
    """
    Main class for the exploration of an plotfile timeseries

    For more details, see the docstring of the following methods:
    - get_field
    - slider
    """

    @debug_view.capture(clear_output=True)
    def __init__(self, path_to_dir, check_all_files=True, backend=None):
        """
        Initialize a plotfile time series

        More precisely, scan the directory and extract the plotfile files,
        as well as some useful plotfile parameters

        Parameters
        ----------
        path_to_dir: string
            The path to the directory where the plotfile files are.

        check_all_files: bool, optional
            Check that all the files in the timeseries are consistent
            (i.e. that they contain the same fields and particles,
            with the same metadata)
            For fast access to the files, this can be changed to False.

        backend: string
            Backend to be used for data reading. Can be `openpmd-api`
            or `h5py`. If not provided will use `openpmd-api` if available
            and `h5py` otherwise.
        """
        # Check backend
        if backend is None:
            backend = available_backends[0] #Pick openpmd-api first if available
        elif backend not in available_backends:
            raise RuntimeError("Invalid backend requested: {0}\n"
                    "The available backends are: {1}"
                    .format(backend, available_backends) )
        self.backend = backend

        # Initialize data reader
        self.data_reader = DataReader(backend)

        # Extract the iterations available in this timeseries
        self.iterations = self.data_reader.list_iterations(path_to_dir)

        # Check that there are files in this directory
        if len(self.iterations) == 0:
            print("Error: Found no valid files in the specified directory.\n"
                  "Please check that this is the path to the plotfile files.")
            return(None)

        # Go through the files of the series, extract the time
        # and a few parameters.
        N_iterations = len(self.iterations)
        self.t = np.zeros(N_iterations)

        # - Extract parameters from the first file
        t, params0 = self.data_reader.read_plotfile_params(self.iterations[0])
        self.t[0] = t
        self.extensions = params0['extensions']
        self.avail_fields = params0['avail_fields']
        if self.avail_fields is not None:
            self.fields_metadata = params0['fields_metadata']
            self.avail_geom = set( self.fields_metadata[field]['geometry']
                                for field in self.avail_fields )
        # Extract information of the particles
        self.avail_species = params0['avail_species']
        self.avail_record_components = \
            params0['avail_record_components']

        # - Extract the time for each file and, if requested, check
        #   that the other files have the same parameters
        for k in range(1, N_iterations):
            t, params = self.data_reader.read_plotfile_params(
                self.iterations[k], check_all_files)
            self.t[k] = t
            if check_all_files:
                for key in params0.keys():
                    if params != params0:
                        print("Warning: File %s has different plotfile "
                              "parameters than the rest of the time series."
                              % self.iterations[k])
                        break

        # - Set the current iteration and time
        self._current_i = 0
        self.current_iteration = self.iterations[0]
        self.current_t = self.t[0]
        # - Find the min and the max of the time
        self.tmin = self.t.min()
        self.tmax = self.t.max()

        # - Initialize a plotter object, which holds information about the time
        self.plotter = Plotter(self.t, self.iterations)

    @debug_view.capture(clear_output=True)
    def get_field(self, field=None, coord=None, t=None, iteration=None,
                  m='all', theta=0., slice_across=None,
                  slice_relative_position=None, plot=False,
                  plot_range=[[None, None], [None, None]], **kw):
        """
        Extract a given field from a file in the plotfile format.

        Parameters
        ----------

        field : string, optional
           Which field to extract

        coord : string, optional
           Which component of the field to extract

        m : int or str, optional
           Only used for thetaMode geometry
           Either 'all' (for the sum of all the modes)
           or an integer (for the selection of a particular mode)

        t : float (in seconds), optional
            Time at which to obtain the data (if this does not correspond to
            an existing iteration, the closest existing iteration will be used)
            Either `t` or `iteration` should be given by the user.

        iteration : int
            The iteration at which to obtain the data
            Either `t` or `iteration` should be given by the user.

        theta : float or None, optional
           Only used for thetaMode geometry
           The angle of the plane of observation, with respect to the x axis
           If `theta` is not None, then this function returns a 2D array
           corresponding to the plane of observation given by `theta` ;
           otherwise it returns a full 3D Cartesian array

        slice_across : str or list of str, optional
           Direction(s) across which the data should be sliced
           + In cartesian geometry, elements can be:
               - 1d: 'z'
               - 2d: 'x' and/or 'z'
               - 3d: 'x' and/or 'y' and/or 'z'
           + In cylindrical geometry, elements can be 'r' and/or 'z'
           Returned array is reduced by 1 dimension per slicing.
           If slicing is None, the full grid is returned.

        slice_relative_position : float or list of float, optional
           Number(s) between -1 and 1 that indicate where to slice the data,
           along the directions in `slice_across`
           -1 : lower edge of the simulation box
           0 : middle of the simulation box
           1 : upper edge of the simulation box
           Default: None, which results in slicing at 0 in all direction
           of `slice_across`.

        plot : bool, optional
           Whether to plot the requested quantity

        plot_range : list of lists
           A list containing 2 lists of 2 elements each
           Indicates the values between which to clip the plot,
           along the 1st axis (first list) and 2nd axis (second list)
           Default: plots the full extent of the simulation box

        **kw : dict, otional
           Additional options to be passed to matplotlib's imshow.

        Returns
        -------
        A tuple with
           F : a 2darray containing the required field
           info : a FieldMetaInformation object
           (see the corresponding docstring)
        """
        # Check that the field required is present
        if self.avail_fields is None:
            raise OpenPMDException('No field data in this time series')
        # Check the field type
        if field not in self.avail_fields:
            field_list = '\n - '.join(self.avail_fields)
            raise OpenPMDException(
                "The `field` argument is missing or erroneous.\n"
                "The available fields are: \n - %s\nPlease set the `field` "
                "argument accordingly." % field_list)
        # Check slicing
        slice_across, slice_relative_position = \
            sanitize_slicing(slice_across, slice_relative_position)
        if slice_across is not None:
            # Check that the elements are valid
            axis_labels = self.fields_metadata[field]['axis_labels']
            for axis in slice_across:
                if axis not in axis_labels:
                    axes_list = '\n - '.join(axis_labels)
                    raise OpenPMDException(
                    'The `slice_across` argument is erroneous: contains %s\n'
                    'The available axes are: \n - %s' % (axis, axes_list) )

        # Check the coordinate, for vector fields
        if self.fields_metadata[field]['type'] == 'vector':
            available_coord = ['x', 'y', 'z']
            if self.fields_metadata[field]['geometry'] == 'thetaMode':
                available_coord += ['r', 't']
            if coord not in available_coord:
                coord_list = '\n - '.join(available_coord)
                raise OpenPMDException(
                    "The field %s is a vector field, \nbut the `coord` "
                    "argument is missing or erroneous.\nThe available "
                    "coordinates are: \n - %s\nPlease set the `coord` "
                    "argument accordingly." % (field, coord_list))
        # Automatically set the coordinate to None, for scalar fields
        else:
            coord = None

        # Find the output that corresponds to the requested time/iteration
        # (Modifies self._current_i, self.current_iteration and self.current_t)
        self._find_output(t, iteration)
        # Get the corresponding iteration
        iteration = self.iterations[self._current_i]

        # Find the proper path for vector or scalar fields
        if self.fields_metadata[field]['type'] == 'scalar':
            field_label = field
        elif self.fields_metadata[field]['type'] == 'vector':
            field_label = field + coord

        # Get the field data
        geometry = self.fields_metadata[field]['geometry']
        axis_labels = self.fields_metadata[field]['axis_labels']

        # - For cartesian
        if geometry in ["1dcartesian", "2dcartesian", "3dcartesian"]:
            F, info = self.data_reader.read_field_cartesian(
                iteration, field, coord, axis_labels,
                slice_relative_position, slice_across)

        # Plot the resulting field
        # Deactivate plotting when there is no slice selection
        if plot:
            if F.ndim == 1:
                self.plotter.show_field_1d(F, info, field_label,
                self._current_i, plot_range=plot_range, **kw)
            elif F.ndim == 2:
                print("self.plotter.show_field_2d")
                self.plotter.show_field_2d(F, info, slice_across, m,
                    field_label, geometry, self._current_i,
                    plot_range=plot_range, **kw)
            else:
                raise OpenPMDException('Cannot plot %d-dimensional data.\n'
                    'Use the argument `slice_across`, or set `plot=False`' % F.ndim)

        print("get_field", F, info)
        print("F.ndim = ", F.ndim)

        # Return the result
        return(F, info)

    @debug_view.capture(clear_output=True)
    def iterate( self, called_method, *args, **kwargs ):
        """
        Repeated calls the method `called_method` for every iteration of this
        timeseries, with the arguments `*args` and `*kwargs`.

        The result of these calls is returned as a list, or, whenever possible
        as an array, where the first axis corresponds to the iterations.

        If `called_method` returns a tuple/list, then `iterate` returns a
        tuple/list of lists (or arrays).

        Parameters
        ----------
        *args, **kwargs: arguments and keyword arguments
            Arguments that would normally be passed to `called_method` for
            a single iteration. Do not pass the argument `t` or `iteration`.
        """
        # Add the iteration key in the keyword aguments
        kwargs['iteration'] = self.iterations[0]

        # Check the shape of results
        result = called_method(*args, **kwargs)
        result_type = type( result )
        if result_type in [tuple, list]:
            returns_iterable = True
            iterable_length = len(result)
            accumulated_result = [ [element] for element in result ]
        else:
            returns_iterable = False
            accumulated_result = [ result ]

        # Call the method for all iterations
        for iteration in tqdm(self.iterations[1:]):
            kwargs['iteration'] = iteration
            result = called_method( *args, **kwargs )
            if returns_iterable:
                for i in range(iterable_length):
                    accumulated_result[i].append( result[i] )
            else:
                accumulated_result.append( result )

        # Try to stack the arrays
        if returns_iterable:
            for i in range(iterable_length):
                accumulated_result[i] = try_array( accumulated_result[i] )
            if result_type == tuple:
                return tuple(accumulated_result)
            elif result_type == list:
                return accumulated_result
        else:
            accumulated_result = try_array( accumulated_result )
            return accumulated_result

    @debug_view.capture(clear_output=True)
    def _find_output(self, t, iteration):
        """
        Find the output that correspond to the requested `t` or `iteration`
        Modify self._current_i accordingly.

        Parameter
        ---------
        t : float (in seconds)
            Time requested

        iteration : int
            Iteration requested
        """
        # Check the arguments
        if (t is not None) and (iteration is not None):
            raise OpenPMDException(
                "Please pass either a time (`t`) \nor an "
                "iteration (`iteration`), but not both.")
        # If a time is requested
        elif (t is not None):
            # Make sure the time requested does not exceed the allowed bounds
            if t < self.tmin:
                self._current_i = 0
            elif t > self.tmax:
                self._current_i = len(self.t) - 1
            # Find the closest existing iteration
            else:
                self._current_i = abs(self.t - t).argmin()
        # If an iteration is requested
        elif (iteration is not None):
            if (iteration in self.iterations):
                # Get the index that corresponds to this iteration
                self._current_i = abs(iteration - self.iterations).argmin()
            else:
                iter_list = '\n - '.join([str(it) for it in self.iterations])
                raise OpenPMDException(
                      "The requested iteration '%s' is not available.\nThe "
                      "available iterations are: \n - %s\n" % (iteration, iter_list))
        else:
            raise OpenPMDException(
                "Please pass either a time (`t`) or an "
                "iteration (`iteration`).")

        # Register the value in the object
        self.current_t = self.t[self._current_i]
        self.current_iteration = self.iterations[self._current_i]
