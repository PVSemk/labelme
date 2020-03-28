# Copyright (c) 2018 Christopher Chute
# Create by Christopher Chute <chutechristopher@gmail.com>

import numpy as np
import os
import pickle
import pydicom
from PyQt5.QtGui import QImage, qRgb
from PIL import Image

DCM_EXT = 'dcm'
META_FILENAME = 'dicom_metadata.pkl'

class DICOMReader(object):

    suffix = DCM_EXT

    def __init__(self):
        raise NotImplementedError('DICOMReader is a static class.')

    @classmethod
    def getImage(cls, dicom_path, w_width=None, w_level=None, pil=False):
        """Read a DICOM file from `file_path`.
        Args:
            dicom_path: Path to read DICOM file from.
            w_width: Width for window to apply. If None, don't apply window.
            w_level: Center for window to apply. If None, don't apply window.
        Returns:
            QImage image data for DICOM file, windowed if `w_center` and `w_width` are not None.
        Raises:
            RuntimeWarning: If cannot find DICOM file at the given `dicom_path`.
        """
        # Read DICOM from disk
        dcm = cls.readRawDICOM(dicom_path)

        # Convert to raw Hounsfield Units and apply window
        pixels = cls._dicomToRaw(dcm)
        if w_level is not None and w_width is not None:
            pixels = cls._applyWindow(pixels, w_level, w_width)

        # Convert to QImage
        if pil:
            image = cls._toPIL(pixels)
        else:
            image = cls._toQImage(pixels)

        return image


    @staticmethod
    def readRawDICOM(dicom_path, stop_before_pixels=False):
        """Read a raw DICOM from disk.
        Args:
            dicom_path: Path to DICOM file to read.
            stop_before_pixels: If true, stop reading before pixel_data.
            Used for fast loading when you only need metadata.
        Returns:
            DICOM object.
        Raises:
            RuntimeWarning: If cannot find DICOM file at the given `dicom_path`.
        """
        try:
            with open(dicom_path, 'rb') as dicom_fh:
                dcm = pydicom.dcmread(dicom_fh, stop_before_pixels=stop_before_pixels)
        except IOError:
            raise RuntimeWarning('Could not load DICOM at path {}'.format(dicom_path))

        return dcm

    @staticmethod
    def _dicomToRaw(dcm, dtype=np.int16):
        """Convert a DICOM object to a Numpy array of raw Hounsfield Units.
        Scale by the RescaleSlope, then add the RescaleIntercept (both DICOM header fields).
        Args:
            dcm: DICOM object.
            dtype: Type of elements in output array.
        Returns:
            ndarray of shape (height, width). Pixels are `int16` raw Hounsfield Units.
        See Also:
            https://www.kaggle.com/gzuidhof/full-preprocessing-tutorial
        """
        img_np = dcm.pixel_array.astype(dtype)

        # Set outside-of-scan pixels to 0
        img_np[img_np == -2000] = 0

        intercept = dcm.RescaleIntercept if 'RescaleIntercept' in dcm else -1024
        slope = dcm.RescaleSlope if 'RescaleSlope' in dcm else 1

        if slope != 1:
            img_np = slope * img_np.astype(np.float64)
            img_np = img_np.astype(dtype)

        img_np += int(intercept)
        img_np = img_np.astype(np.uint8)

        return img_np

    @staticmethod
    def _applyWindow(img, w_center, w_width):
        """Apply a window to raw Hounsfield Units to get a PNG.
        Args:
            img: Raw Hounsfield Units for every pixel.
            w_center: Center of window to apply (e.g. 40 Hounsfield Units).
            w_width: Total width of window to apply (e.g. 400 Hounsfield Units).
        Returns:
            Single-byte pixel values for the Hounsfield Units image as a windowed greyscale image.
        """

        # Convert to float
        img = np.copy(img).astype(np.float64)

        # Clip to min and max values
        w_max = w_center + w_width / 2
        w_min = w_center - w_width / 2
        img = np.clip(img, w_min, w_max)

        # Normalize to uint8
        img -= w_min
        img /= w_width
        img *= np.iinfo(np.uint8).max
        img = img.astype(np.uint8)

        return img

    @staticmethod
    def _toQImage(arr, do_copy=False):
        """Convert NumPy ndarray to QImage format.
        Taken from:
            https://gist.github.com/smex/5287589
        Args:
            arr: NumPy array to convert.
            do_copy: If true, copy the QImage file before returning.
        Returns:
            QImage formatted image.
        """
        if arr is None:
            return QImage()

        gray_color_table = [qRgb(i, i, i) for i in range(256)]

        if arr.dtype == np.uint8:
            if len(arr.shape) == 2:
                qim = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if do_copy else qim

            elif len(arr.shape) == 3:
                if arr.shape[2] == 3:
                    qim = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_RGB32)
                    return qim.copy() if do_copy else qim
                elif arr.shape[2] == 4:
                    qim = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_ARGB32)
                    return qim.copy() if do_copy else qim

        raise NotImplementedError('Unsupported image format.')

    @staticmethod
    def _toPIL(arr):
        if arr.dtype == np.uint8:
            if len(arr.shape) == 2:
                return Image.fromarray(arr, mode='L')
            elif len(arr.shape) == 3:
                if arr.shape[2] == 3:
                    return Image.fromarray(arr, mode='RGB')
                elif arr.shape[2] == 4:
                    return Image.fromarray(arr, mode='RGBA')

        raise NotImplementedError('Unsupported image format.')

