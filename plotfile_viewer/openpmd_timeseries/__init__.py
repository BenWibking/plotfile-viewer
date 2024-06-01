# Make the OpenPMDTimeSeries accessible from outside the file main
from .main import OpenPMDTimeSeries
from .field_metainfo import FieldMetaInformation
__all__ = ['OpenPMDTimeSeries', 'FieldMetaInformation']
