"""
This file is part of the plotfile-viewer.

It defines a set of methods which are useful for plotting
(and labeling the plots).

Copyright 2015-2016, plotfile-viewer contributors
Author: Remi Lehe
License: 3-Clause-BSD-LBNL
"""
import numpy as np
import math

from .interactive import debug_view

try:
    import warnings
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib_installed = True
except ImportError:
    matplotlib_installed = False

class Plotter(object):

    """
    Class which is used for plotting particles and fields
    (and labeling the plots)
    """

    @debug_view.capture(clear_output=False)
    def __init__(self, t, iterations):
        """
        Initialize the object

        Parameters
        ----------
        t: 1darray of floats (seconds)
           Time for each available iteration of the timeseries

        iterations: 1darray of ints
           Iteration number for each available iteration of the timeseries
        """
        # Default fontsize
        self.fontsize = 12

        # Register the time array and iterations array
        # (Useful when labeling the figures)
        self.t = t
        self.iterations = iterations
    
    @debug_view.capture(clear_output=False)
    def show_field_1d( self, F, info, field_label, current_i, plot_range,
                            vmin=None, vmax=None, **kw ):
        """
        Plot the given field in 1D

        Parameters
        ----------
        F: 1darray of floats
            Contains the field to be plotted

        info: a FieldMetaInformation object
            Contains the information about the plotted field

        field_label: string
           The name of the field plotted (for labeling purposes)

        vmin, vmax: floats or None
           The amplitude of the field

        plot_range : list of lists
           Indicates the values between which to clip the plot,
           along the 1st axis (first list) and 2nd axis (second list)
        """
        # Check if matplotlib is available
        check_matplotlib()

        # Find the iteration and time
        iteration = self.iterations[current_i]
        time = self.t[current_i]

        # Get the x axis
        xaxis = getattr( info, info.axes[0] )
        # Plot the data
        if np.issubdtype(F.dtype, np.complexfloating):
            plot_data = abs(F) # For complex numbers, plot the absolute value
            title = "|%s|" %field_label
        else:
            plot_data = F
            title = "%s" %field_label

        # Get the title and labels
        title += " at %.2e s   (iteration %d)" % (time, iteration)
        plt.title(title, fontsize=self.fontsize)
        # Add the name of the axes
        plt.xlabel(f'${info.axes[0]}$', fontsize=self.fontsize)

        plt.plot( xaxis, plot_data )
        # Get the limits of the plot
        # - Along the first dimension
        if (plot_range[0][0] is not None) and (plot_range[0][1] is not None):
            plt.xlim( plot_range[0][0], plot_range[0][1] )
        else:
            plt.xlim( xaxis.min(), xaxis.max() )  # Full extent of the box
        # - Along the second dimension
        if (plot_range[1][0] is not None) and (plot_range[1][1] is not None):
            plt.ylim( plot_range[1][0], plot_range[1][1] )


    @debug_view.capture(clear_output=False)
    def show_field_2d(self, F, info, slice_across, m, field_label, geometry,
                        current_i, plot_range, **kw):
        """
        Plot the given field in 2D

        Parameters
        ----------
        F: 2darray of floats
            Contains the field to be plotted

        info: a FieldMetaInformation object
            Contains the information about the plotted field

        slice_across : str, optional
           Only used for 3dcartesian geometry
           The direction across which the data is sliced

        m: int
           Only used for thetaMode geometry
           The azimuthal mode used when plotting the fields

        field_label: string
           The name of the field plotted (for labeling purposes)

        geometry: string
           Either "2dcartesian", "3dcartesian" or "thetaMode"

        plot_range : list of lists
           Indicates the values between which to clip the plot,
           along the 1st axis (first list) and 2nd axis (second list)
        """
        print("show_field_2d()")
        # Check if matplotlib is available
        check_matplotlib()

        # Find the iteration and time
        iteration = self.iterations[current_i]
        time = self.t[current_i]

        # Plot the data
        if np.issubdtype(F.dtype, np.complexfloating):
            plot_data = abs(F)
            title = "|%s|" %field_label
        else:
            plot_data = F
            title = "%s" %field_label
        
        oldex = info.imshow_extent
        extents=[oldex[2], oldex[3], oldex[0], oldex[1]]
        plt.imshow(plot_data.T, extent=extents, origin='lower',
                   interpolation='nearest', aspect='equal', **kw)
        plt.colorbar()
        print("extents:", extents)

        # Get the title and labels
        title += " at %.2e s   (iteration %d)" % (time, iteration)
        plt.title(title, fontsize=self.fontsize)

        # Add the name of the axes
        plt.xlabel(f'${info.axes[0]}$', fontsize=self.fontsize)
        plt.ylabel(f'${info.axes[1]}$', fontsize=self.fontsize)

        # Get the limits of the plot
        # - Along the first dimension
        if (plot_range[0][0] is not None) and (plot_range[0][1] is not None):
            plt.ylim( plot_range[0][0], plot_range[0][1] )
        # - Along the second dimension
        if (plot_range[1][0] is not None) and (plot_range[1][1] is not None):
            plt.xlim( plot_range[1][0], plot_range[1][1] )


@debug_view.capture(clear_output=False)
def check_matplotlib():
    """Raise error messages or warnings when potential issues when
    potenial issues with matplotlib are detected."""

    if not matplotlib_installed:
        raise RuntimeError( "Failed to import the plotfile-viewer plotter.\n"
            "(Make sure that matplotlib is installed.)")

    elif ('MacOSX' in matplotlib.get_backend()):
        warnings.warn("\n\nIt seems that you are using the matplotlib MacOSX "
        "backend. \n(This typically obtained when typing `%matplotlib`.)\n"
        "With recent version of Jupyter, the plots might not appear.\nIn this "
        "case, switch to `%matplotlib notebook` and restart the notebook.")
