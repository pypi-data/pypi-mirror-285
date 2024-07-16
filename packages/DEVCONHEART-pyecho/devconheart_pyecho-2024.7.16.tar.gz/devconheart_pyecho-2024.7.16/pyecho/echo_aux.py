"""
-----------------------------------------------------------------------------------------
echo-aux module
-----------------------------------------------------------------------------------------
Auxiliary resources for US handling.
"""

from enum import Enum


class USRegionSpatialFormat(Enum):
    """Codes of US Region Spatial Format."""

    NONE = 0
    TISSUE_2D = 1
    MMODE = 2
    SPECTRAL = 3
    WAVEFORM = 4
    GRAPHICS = 5

class PhysicalUnits(Enum):
    """Codes of Physical units."""

    NONE = 0
    PERCENT = 1
    DB = 2
    CM = 3
    SEC = 4
    HZ = 5
    DB_SEC = 6
    CM_SEC = 7
    CMSQR = 8
    CMSQR_SEC = 9
    CMCUBE = 10
    CMCUBE_SEC = 11
    DEGREE = 12