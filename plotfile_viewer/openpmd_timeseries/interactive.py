"""
This file is part of the plotfile-viewer.

It defines an interactive interface for the viewer,
based on the IPython notebook functionalities

Copyright 2015-2016, plotfile-viewer contributors
Authors: Remi Lehe, Axel Huebl
License: 3-Clause-BSD-LBNL
"""
import math
from functools import partial
try:
    from ipywidgets import widgets, __version__
    ipywidgets_version = int(__version__[0])
    from IPython.core.display import display, clear_output
    import matplotlib
    import matplotlib.pyplot as plt
    dependencies_installed = True
except ImportError:
    dependencies_installed = False

debug_view = widgets.Output(layout={'border': '1px solid black'})

class InteractiveViewer(object):

    def __init__(self):
        pass

    def slider(self, figsize=(6, 5), fields_figure=0, **kw):
        """
        Navigate the simulation using a slider

        Parameters
        ----------
        figsize: tuple
            Size of the figures

        fields_figure: ints
            The number of the matplotlib figure on which the fields
            will be plotted.
            (This is similar to calling `plt.figure(fields_figure)`)

        kw: dict
            Extra arguments to pass to matplotlib's imshow (e.g. cmap, etc.).
            Note that `kw` sets the initial plotting options, but the user
            can then still modify these options through the slider interface.
        """
        # Check that the dependencies have been installed
        if not dependencies_installed:
            raise RuntimeError("Failed to load the plotfile-viewer slider.\n"
                "(Make sure that ipywidgets and matplotlib are installed.)")

        # set flag for first plot
        self.is_first_plot = True

        #only for debugging
        #display(debug_view)

        # -----------------------
        # Define useful functions
        @debug_view.capture(clear_output=True)
        def refresh_field(change=None, force=False):
            """
            Refresh the current field figure

            Parameters :
            ------------
            change: dictionary
                Dictionary passed by the widget to a callback functions
                whenever a change of a widget happens
                (see docstring of ipywidgets.Widget.observe)
                This is mainline a place holder ; not used in this function

            force: bool
                Whether to force the update
            """
            print("refresh_field()")

            # Determine whether to do the refresh
            do_refresh = False
            if (self.avail_fields is not None):
                if force or fld_refresh_toggle.value:
                    do_refresh = True
            # Do the refresh
            if do_refresh:
                # save the old zoom for restoring later
                # (ref: https://stackoverflow.com/questions/70336467/keep-zoom-and-ability-to-zoom-out-to-current-data-extent-in-matplotlib-pyplot)
                old_ax = plt.gcf().gca()
                old_x_lim = old_ax.get_xlim()
                old_y_lim = old_ax.get_ylim()

                # create new figure and clear
                plt.figure(fld_figure_button.value, figsize=figsize)
                plt.clf()

                # When working in inline mode, in an ipython notebook,
                # clear the output (prevents the images from stacking
                # in the notebook)
                if 'inline' in matplotlib.get_backend():
                    if ipywidgets_version < 7:
                        clear_output()
                    else:
                        import warnings
                        warnings.warn(
                        "\n\nIt seems that you are using ipywidgets 7 and "
                        "`%matplotlib inline`. \nThis can cause issues when "
                        "using `slider`.\nIn order to avoid this, you "
                        "can either:\n- use `%matplotlib notebook`\n- or "
                        "downgrade to ipywidgets 6 (with `pip` or `conda`).",
                        UserWarning)

                # Handle plotting options
                kw_fld = kw.copy()
                vmin, vmax = fld_color_button.get_range()
                kw_fld['vmin'] = vmin
                kw_fld['vmax'] = vmax
                kw_fld['cmap'] = fld_color_button.cmap.value
                # Determine range of the plot from widgets
                plot_range = [ fld_hrange_button.get_range(),
                                fld_vrange_button.get_range() ]

                # Handle slicing direction
                if slice_across_button.value == 'None':
                    slice_across = None
                else:
                    slice_across = slice_across_button.value

                # Call the method get_field
                self.get_field( iteration=self.current_iteration, plot=True,
                    field=fieldtype_button.value, coord=coord_button.value,
                    m=convert_to_int(mode_button.value),
                    slice_relative_position=slicing_button.value,
                    theta=theta_button.value,
                    slice_across=slice_across,
                    plot_range=plot_range, **kw_fld )
                
                # restore the old zoom settings using the *new* figure
                # FIXME: this does not always work well for 1D plots...
                if self.is_first_plot is False:
                    toolbar = plt.gcf().canvas.manager.toolbar
                    toolbar.update()        # Clear the axes stack
                    toolbar.push_current()  # save the auto-view as home
                    ax = plt.gcf().gca()
                    ax.set_xlim(old_x_lim)  # restore zoom
                    ax.set_ylim(old_y_lim)
                else:
                    # we've made the first plot, so unset flag
                    self.is_first_plot = False

        @debug_view.capture(clear_output=True)
        def refresh_field_type(change):
            """
            Refresh the field type and disable the coordinates buttons
            if the field is scalar.

            Parameter
            ---------
            change: dictionary
                Dictionary passed by the widget to a callback functions
                whenever a change of a widget happens
                (see docstring of ipywidgets.Widget.observe)
            """
            print("refresh_field_type()")

            # Deactivate the field refreshing to avoid callback
            # while modifying the widgets
            saved_refresh_value = fld_refresh_toggle.value
            fld_refresh_toggle.value = False

            new_field = change['new']
            # Activate/deactivate vector fields
            if self.fields_metadata[new_field]['type'] == 'vector':
                coord_button.disabled = False
            else:
                coord_button.disabled = True
            # Activate/deactivate cylindrical-specific widgets
            if self.fields_metadata[new_field]['geometry'] == 'thetaMode':
                mode_button.disabled = False
                theta_button.disabled = False
            else:
                mode_button.disabled = True
                theta_button.disabled = True
            # Activate the right slicing options
            if self.fields_metadata[new_field]['geometry'] == '3dcartesian':
                slice_across_button.options = \
                    self.fields_metadata[new_field]['axis_labels']
                slice_across_button.value = 'y'
            else:
                slice_across_button.options = ['None'] + \
                    self.fields_metadata[new_field]['axis_labels']
                slice_across_button.value = 'None'

            # Put back the previous value of the refreshing button
            fld_refresh_toggle.value = saved_refresh_value

            # Show the fields
            refresh_field()

        @debug_view.capture(clear_output=True)
        def change_iteration(change):
            "Plot the result at the required iteration"
            print("change_iteration()")

            # Find the closest iteration
            self._current_i = abs(self.iterations - change['new']).argmin()
            self.current_iteration = self.iterations[ self._current_i ]
            refresh_field()

        @debug_view.capture(clear_output=True)
        def step_fw(b):
            "Plot the result one iteration further"
            print("step_fw()")
            
            if self._current_i < len(self.t) - 1:
                self.current_iteration = self.iterations[self._current_i + 1]
            else:
                self.current_iteration = self.iterations[self._current_i]
            slider.value = self.current_iteration

        @debug_view.capture(clear_output=True)
        def step_bw(b):
            "Plot the result one iteration before"
            print("step_bw()")

            if self._current_i > 0:
                self.current_iteration = self.iterations[self._current_i - 1]
            else:
                self.current_iteration = self.iterations[self._current_i]
            slider.value = self.current_iteration

        # ---------------
        # Define widgets
        # ---------------

        # used for both VCR and Slider
        iteration_min = self.iterations.min()
        iteration_max = self.iterations.max()
        step = max( int( (iteration_max - iteration_min) / 20. ), 1 )

        # "VCR" controls
        play = widgets.Play( description="VCR player",
            min=iteration_min, max=iteration_max + step, step=step )

        # Slider
        slider = widgets.IntSlider( description="iteration",
            min=iteration_min, max=iteration_max + step, step=step )
        slider.observe( change_iteration, names='value', type='change' )
        widgets.jslink((play, 'value'), (slider, 'value'))
        set_widget_dimensions( slider, width=500 )

        # Forward button
        button_p = widgets.Button(description="+")
        set_widget_dimensions( button_p, width=40 )
        button_p.on_click(step_fw)

        # Backward button
        button_m = widgets.Button(description="-")
        set_widget_dimensions( button_m, width=40 )
        button_m.on_click(step_bw)

        # Display the time widgets
        container = widgets.HBox(children=[play, button_m, button_p, slider])
        display(container)

        # Field widgets
        # -------------
        if (self.avail_fields is not None):

            # Field type
            # ----------
            # Field button
            fieldtype_button = create_toggle_buttons(
                description='Field:',
                options=sorted(self.avail_fields))
            fieldtype_button.observe( refresh_field_type, 'value', 'change' )

            # Coord button
            if "thetaMode" in self.avail_geom:
                coord_button = create_toggle_buttons(
                    description='Coord:', options=['x', 'y', 'z', 'r', 't'])
            else:
                coord_button = create_toggle_buttons(
                    description='Coord:', options=['x', 'y', 'z'])
            coord_button.observe( refresh_field, 'value', 'change')

            # Mode and theta button (for thetaMode)
            # (First find all available cylindrical modes, across all fields)
            avail_circ_modes = []
            for field in self.avail_fields:
                for m in self.fields_metadata[field]['avail_circ_modes']:
                    if m not in avail_circ_modes:
                        avail_circ_modes.append(m)
            mode_button = create_toggle_buttons(description='Mode:',
                                                options=avail_circ_modes)
            mode_button.observe( refresh_field, 'value', 'change')
            theta_button = widgets.FloatSlider( value=0.,
                    min=-math.pi / 2, max=math.pi / 2)
            set_widget_dimensions( theta_button, width=190 )
            theta_button.observe( refresh_field, 'value', 'change')

            # Slicing buttons
            axis_labels = self.fields_metadata[field]['axis_labels']
            if self.fields_metadata[field]['geometry'] == '3dcartesian':
                slice_across_button = create_toggle_buttons( value='y',
                    options=axis_labels )
            else:
                slice_across_button = create_toggle_buttons( value='None',
                    options=['None'] + axis_labels )
                
            slice_across_button.observe( refresh_field, 'value', 'change' )
            slicing_button = widgets.FloatSlider( min=-1., max=1., value=0.)
            set_widget_dimensions( slicing_button, width=180 )
            slicing_button.observe( refresh_field, 'value', 'change')

            # Plotting options
            # ----------------

            # Figure number
            fld_figure_button = widgets.IntText( value=fields_figure )
            set_widget_dimensions( fld_figure_button, width=50 )

            # Colormap button
            fld_color_button = ColorBarSelector( refresh_field,
                default_cmap=kw.get('cmap', 'RdBu'),
                default_vmin=kw.get('vmin', -5.e9),
                default_vmax=kw.get('vmax', 5.e9) )
            
            # Range buttons
            fld_hrange_button = RangeSelector( refresh_field,
                default_value=10., title='Horizontal axis:')
            fld_vrange_button = RangeSelector( refresh_field,
                default_value=10., title='Vertical axis:')
            
            # Refresh buttons
            fld_refresh_toggle = widgets.ToggleButton(
                description='Always refresh', value=True)
            fld_refresh_button = widgets.Button(
                description='Refresh now!')
            fld_refresh_button.on_click( partial(refresh_field, force=True) )

            # Containers
            # ----------

            # Field type container
            field_widget_list = [fieldtype_button, coord_button]
            container_fields = widgets.VBox( children=field_widget_list )
            set_widget_dimensions( container_fields, width=330 )

            # Slicing container
            slices_widget_list = [
                add_description("Slice normal:",
                    slice_across_button, width=100),
                add_description("Slicing position:", slicing_button) ]
            if "thetaMode" in self.avail_geom:
                # Add widgets specific to azimuthal modes
                slices_widget_list += [ mode_button,
                                add_description('Theta:', theta_button)]
            container_slicing = widgets.VBox( children=slices_widget_list )
            set_widget_dimensions( container_slicing, width=330 )

            # Plotting options container
            container_fld_cbar = fld_color_button.to_container()
            container_fld_hrange = fld_hrange_button.to_container()
            container_fld_vrange = fld_vrange_button.to_container()
            container_fld_plots = widgets.VBox( children=[
                add_description("<b>Figure:</b>", fld_figure_button),
                container_fld_cbar, container_fld_vrange,
                container_fld_hrange ])
            set_widget_dimensions( container_fld_plots, width=330 )

            # Accordion for the field widgets
            accord1 = widgets.Accordion( children=[container_fields,
                container_slicing, container_fld_plots])
            accord1.set_title(0, 'Field type')
            accord1.set_title(1, 'Slice selection')
            accord1.set_title(2, 'Plotting options')

            # Complete field container
            container_fld = widgets.VBox( children=[accord1, widgets.HBox(
                children=[fld_refresh_toggle, fld_refresh_button])])
            set_widget_dimensions( container_fld, width=370 )

        # Global container
        if (self.avail_fields is not None) and \
                (self.avail_species is not None):
            global_container = widgets.HBox(
                children=[container_fld])
            display(global_container)
        elif self.avail_species is None:
            display(container_fld)

        # When using %matplotlib widget, display the figures at the end
        if 'ipympl' in matplotlib.get_backend() or 'widget' in matplotlib.get_backend():
            # Disable interactive mode
            # This prevents the notebook from showing the figure
            # when calling `plt.figure` (unreliable with `%matplotlib widget`)
            # and we use `display` instead.
            plt.ioff()
            fig = plt.figure( fld_figure_button.value )
            display(fig.canvas)
            # Enable interactive mode again
            plt.ion()
        else:
            print("not using ipympl. using backend:", matplotlib.get_backend())


def convert_to_int(m):
    """
    Convert the string m to an int, except if m is 'all' or None
    """
    if (m == 'all') or (m is None):
        return(m)
    else:
        return(int(m))


class ColorBarSelector(object):
    """
    Class that allows to select a colorbar and the corresponding range.
    It features a widget for the exponent, in order to rapidly change
    the order of magnitude of the colorbar.
    """

    def __init__( self, callback_function, default_cmap,
                        default_vmin, default_vmax ):
        """
        Initialize a set of widgets that select a colorbar.

        Parameters:
        -----------
        callback_function: callable
            The function to call when activating/deactivating the range,
            or when changing the colormap
        default_cmap: string
            The name of the colormap that will be used when the widget is
            initialized
        default_vmin, default_vmax: float
            The default value for the initial value of vmin and vmax
        """
        # Create the colormap widget
        available_cmaps = sorted( plt.colormaps() )
        if default_cmap not in available_cmaps:
            default_cmap = 'jet'
        self.cmap = widgets.Select(options=available_cmaps, value=default_cmap)

        # Convert default_vmin, default vmax to scientific format
        max_abs = max( abs(default_vmin), abs(default_vmax) )
        default_exponent = math.floor( math.log10( max_abs ) )
        default_upbound = default_vmax * 10.**(-default_exponent)
        default_lowbound = default_vmin * 10.**(-default_exponent)

        # Create the widgets for the range
        self.active = create_checkbox( value=False )
        self.low_bound = widgets.FloatText( value=default_lowbound )
        self.up_bound = widgets.FloatText( value=default_upbound )
        self.exponent = widgets.FloatText( value=default_exponent )

        # Add the callback function
        self.active.observe( callback_function, 'value', 'change' )
        self.exponent.observe( callback_function, 'value', 'change' )
        self.cmap.observe( callback_function, 'value', 'change' )

    def to_container( self ):
        """
        Return a widget container, where all the widgets
        are placed properly, with respect to each other.
        """
        # Set the widget dimensions
        set_widget_dimensions( self.active, width=20 )
        set_widget_dimensions( self.low_bound, width=60 )
        set_widget_dimensions( self.up_bound, width=60 )
        set_widget_dimensions( self.exponent, width=45 )
        set_widget_dimensions( self.cmap, width=200 )
        # Gather the different widgets on two lines
        cmap_container = widgets.HBox( children=[
            widgets.HTML( "<b>Colorbar:</b>"), self.cmap ])
        if ipywidgets_version > 4:
            # For newer version of ipywidgets: add the "x10^" on same line
            range_container = widgets.HBox( children=[ self.active,
                add_description("from", self.low_bound, width=30 ),
                add_description("to", self.up_bound, width=20 ),
                add_description("x 10^", self.exponent, width=45 ) ] )
            final_container = widgets.VBox(
                children=[ cmap_container, range_container ])
        else:
            # For older version of ipywidgets: add the "x10^" on new line
            range_container = widgets.HBox( children=[ self.active,
                add_description("from", self.low_bound, width=30 ),
                add_description("to", self.up_bound, width=20 ) ] )
            final_container = widgets.VBox(
                children=[ cmap_container, range_container,
                add_description("x 10^", self.exponent, width=45 ) ])
        set_widget_dimensions( final_container, width=310 )
        return( final_container )

    def get_range( self ):
        """
        Return a list of 2 elements: the current lower bound and upper bound.
        When the widget is not active, None is returned instead of the bounds.
        """
        if self.active.value is True:
            return( [ self.low_bound.value * 10.**self.exponent.value,
                      self.up_bound.value * 10.**self.exponent.value ] )
        else:
            return( [ None, None ] )


class RangeSelector(object):
    """
    Class that allows to select a range of (float) values.
    """

    def __init__( self, callback_function, default_value, title ):
        """
        Initialize a set of widgets that select a range of (float) values

        Parameters:
        -----------
        callback_function: callable
            The function to call when activating/deactivating the range
        default_value:
            The default value of the upper bound of the range at initialization
            (The default lower bound is the opposite of this value.)
        title:
            The title that is displayed on top of the widgets
        """
        # Register title
        self.title = title

        # Create the widgets
        self.active = create_checkbox( value=False )
        self.low_bound = widgets.FloatText( value=-default_value )
        self.up_bound = widgets.FloatText( value=default_value )

        # Add the callback function
        self.active.observe( callback_function, 'value', 'change' )

    def to_container( self ):
        """
        Return a widget container, where all the range widgets
        are placed properly, with respect to each other.
        """
        # Set the widget dimensions
        set_widget_dimensions( self.active, width=20 )
        set_widget_dimensions( self.low_bound, width=60 )
        set_widget_dimensions( self.up_bound, width=60 )
        # Gather the different widgets on one line
        container = widgets.HBox( children=[ self.active,
            add_description("from", self.low_bound, width=30 ),
            add_description("to", self.up_bound, width=20 ) ] )
        set_widget_dimensions( container, width=310 )
        # Add the title
        final_container = widgets.VBox( children=[
            widgets.HTML( "<b>%s</b>" % self.title ), container ] )
        return( final_container )

    def get_range( self ):
        """
        Return a list of 2 elements: the current lower bound and upper bound.
        When the widget is not active, None is returned instead of the bounds.
        """
        if self.active.value is True:
            return( [ self.low_bound.value, self.up_bound.value ] )
        else:
            return( [ None, None ] )

def set_widget_dimensions( widget, height=None, width=None, left_margin=None ):
    """
    Set the dimensions of the widget, using the proper API
    (which depends on the version of ipywidgets)

    Parameters
    ----------
    widget: an ipywidget object

    height, width: integer, optional
        The height and width in number of points

    left_margin: integer, optional
        Only used for ipywidgets version > 5
        The left margin of a widget (avoids collisions with other widgets)
    """
    if ipywidgets_version >= 5:
        if height is not None:
            widget.layout.height = str(height) + 'px'
        if width is not None:
            widget.layout.width = str(width) + 'px'
        if left_margin is not None:
            widget.layout.margin = "0px 0px 0px " + str(left_margin) + "px"
    else:
        if height is not None:
            widget.height = height
        if width is not None:
            widget.width = width


def add_description( text, annotated_widget, width=50 ):
    """
    Add a description (as an HTML widget) to the left of `annotated_widget`

    Parameters
    ----------
    text: string
        The text to be added
    annotated_widget: an ipywidgets widget
        The widget to which the description will be added
    width: int
        The width of the description
    """
    html_widget = widgets.HTML(text)
    set_widget_dimensions( html_widget, width=width )
    return( widgets.HBox( children=[ html_widget, annotated_widget] ) )


def create_toggle_buttons( **kwargs ):
    """
    Initialize a ToggleButtons widget, in such a way that
    its buttons are sized proportionally to the text content, when possible.

    Parameters:
    -----------
    **kwargs: keyword arguments
        Arguments to be passed to the ToggleButtons constructor
    """
    t = widgets.ToggleButtons( **kwargs )
    # Set the style attribute of the widgets, so that buttons
    # automatically adapt to the size of their content
    if ipywidgets_version >= 7:
        t.style.button_width = 'initial'
    return(t)


def create_checkbox( **kwargs ):
    """
    Create a Checkbox widget, in such a way that it displays correctly
    with all versions of ipywidgets

    Parameters:
    -----------
    **kwargs: keyword arguments
        Arguments to be passed to the ToggleButtons constructor
    """
    if ipywidgets_version >= 7:
        c = widgets.Checkbox( indent=False, **kwargs )
    else:
        c = widgets.Checkbox( **kwargs )
    return(c)
