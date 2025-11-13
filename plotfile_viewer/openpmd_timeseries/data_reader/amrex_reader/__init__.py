import builtins
import importlib


def _load_amr_module():
    """Return the amrex space module matching the configured dimensionality."""
    spacedim = getattr(builtins, 'amrex_spacedim', 3)
    if spacedim not in (2, 3):
        raise ValueError(f'Unsupported amrex_spacedim={spacedim}')
    return importlib.import_module(f'amrex.space{spacedim}d')


amr = _load_amr_module()

from .params_reader import read_plotfile_params
from .field_reader import read_field_cartesian, get_grid_parameters
from .utilities import list_files

__all__ = ['amr', 'read_plotfile_params', 'list_files', 'read_field_cartesian', 'get_grid_parameters']
