"""
-----------------------------------------------------------------------------------------
echo module
-----------------------------------------------------------------------------------------
Includes Echo class.
"""

from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
import pydicom
import cv2

from pyecho.echo_error import EchoViewerError
from pyecho.echo_aux import USRegionSpatialFormat, PhysicalUnits


class Echo:
    """Class to operate with echo data from DICOM files."""

    # INIT
    def __init__(self, data: pydicom.FileDataset):
        self.__data = data

        self.__meta = {}
        for sequence in self.__data.SequenceOfUltrasoundRegions:
            self.__meta[USRegionSpatialFormat(sequence.RegionSpatialFormat)] = {
                "PhysicalUnitsXDirection": PhysicalUnits(
                    sequence.PhysicalUnitsXDirection
                ),
                "PhysicalUnitsYDirection": PhysicalUnits(
                    sequence.PhysicalUnitsYDirection
                ),
                "PhysicalDeltaX": sequence.PhysicalDeltaX,
                "PhysicalDeltaY": sequence.PhysicalDeltaY,
            }

    # GETTERS
    def get_echo(self) -> np.ndarray:
        """Returns the complete echo image array.

        Returns:
            np.ndarray: Image array.
        """
        return cv2.cvtColor(self.__data.pixel_array, cv2.COLOR_RGB2GRAY)

    def get_mmode_idx(self) -> int:
        """Finds the index of the M-mode within SequenceOfUltrasoundRegions.

        Returns:
            int: Index of the M-mode (returns -1 when not found).
        """
        for i, seq in enumerate(self.__data.SequenceOfUltrasoundRegions):
            if (
                USRegionSpatialFormat(seq.RegionSpatialFormat)
                == USRegionSpatialFormat.MMODE
            ):
                return i
        return -1

    def get_mmode_metadata(self) -> pydicom.Dataset:
        """Get m_mode metadata.

        Returns:
            pydicom.Dataset: M-mode metadata.

            Returns an empty pydicom.Dataset if not found.
        """
        idx = self.get_mmode_idx()
        if idx >= 0:
            return self.__data.SequenceOfUltrasoundRegions[idx]
        return pydicom.Dataset()

    def get_mmode_img(self, crop: Tuple[int, int, int, int] = None) -> np.ndarray:
        """Get M-mode region.

        Args:
            crop (Tuple[int,int,int,int], optional): Crop the returned image.
            Defaults to None (no crop).

        Returns:
            np.ndarray: M-mode array.

            Returns empty np.ndarray if not found.
        """
        m_mode_data = self.get_mmode_metadata()
        if m_mode_data:
            if "ReferencePixelX0" in m_mode_data:
                img = self.get_echo()[
                    m_mode_data.RegionLocationMinY0 : m_mode_data.RegionLocationMaxY1,
                    m_mode_data.RegionLocationMinX0 : min(m_mode_data.ReferencePixelX0,m_mode_data.RegionLocationMaxX1),
                ]
            else:
                img = self.get_echo()[
                    m_mode_data.RegionLocationMinY0 : m_mode_data.RegionLocationMaxY1,
                    m_mode_data.RegionLocationMinX0 : m_mode_data.RegionLocationMaxX1,
                ]

            if crop is None:
                return img
            else:
                return img[
                    crop[0] : img.shape[0] - crop[1] + 1,
                    crop[2] : img.shape[1] - crop[3] + 1,
                ]

        return np.array([])

    # VIEWERS
    def view_all(self, figsize: Tuple[int, int] = (20, 30), axis: bool = False) -> None:
        """Visualizes the complete echo image.

        This method is namely for interactive purposes.

        Args:
            figsize (Tuple[int, int], optional): Size of the ouput figure (in inches).
            Defaults to (20, 30).

            axis (bool, optional): Wether to show or not the figure axis.
            Defaults to False.
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.gca()
        ax.imshow(self.get_echo(), cmap="gist_gray")
        if not axis:
            ax.axis("off")
        plt.show()

    def view_mmode(
        self,
        figsize: Tuple[int, int] = (20, 30),
        crop: Tuple[int, int, int, int] = None,
        axis: bool = False,
    ) -> None:
        """Visualizes the M-mode region.

        Args:
            figsize (Tuple[int, int], optional): Size of the ouput figure (in inches).
            Defaults to (20, 30).

            crop (Tuple[int,int,int,int], optional): Crop the viewed image.
            Defaults to None (no crop).

            axis (bool, optional): Whether to show or not the figure axis.
            Defaults to False.

        Raises:
            EchoViewerError: Raised when no M-mode is found.
        """
        m_mode = self.get_mmode_img(crop)
        if m_mode.size:
            fig = plt.figure(figsize=figsize)
            ax = fig.gca()
            ax.imshow(m_mode, cmap="gist_gray")
            if not axis:
                ax.axis("off")
            plt.show()
        else:
            raise EchoViewerError("No M-mode found.")
