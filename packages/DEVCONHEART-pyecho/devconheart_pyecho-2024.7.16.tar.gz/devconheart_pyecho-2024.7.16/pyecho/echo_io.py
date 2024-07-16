"""
-----------------------------------------------------------------------------------------
echo-io module
-----------------------------------------------------------------------------------------
IO tools.
"""

import pydicom

from pyecho.echo import Echo

def read_echo(file:str) -> Echo:
    """Reads a DICOM file.

    Args:
        file (str): Path to the DICOM file.

    Returns:
        Echo: Object with echo data.
    """
    data = pydicom.dcmread(file)
    data.decompress()

    return Echo(data)