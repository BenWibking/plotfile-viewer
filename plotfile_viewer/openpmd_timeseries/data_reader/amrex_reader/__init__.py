import builtins
if hasattr(builtins, 'amrex_spacedim'):
    from builtins import amrex_spacedim
    if amrex_spacedim == 2:
        import amrex.space2d as amr
    elif amrex_spacedim == 3:
        import amrex.space3d as amr
else: # default case
    import amrex.space3d as amr

from .params_reader import read_plotfile_params
from .field_reader import read_field_cartesian, get_grid_parameters
from .utilities import list_files

__all__ = ['read_plotfile_params', 'list_files', 'read_field_cartesian', 'get_grid_parameters']