"""
compress.py - image compression and decompression. 

Functions related to compressing and decompressing images. We
use LZ4 as the various python zip routines are quite slow.
"""

from __future__ import annotations

__all__ = [
    "compress",
    "decompress",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import lz4.frame
import os
import numpy as np
from astropy.io import fits
from typing import Tuple


def decompress(image_path: str) -> Tuple[np.array, fits.hdu.image.PrimaryHDU]:
    ''' Decompress with LZ4. We have to return the data from within
    the lz4 context so we assume only one HDU which is true for our
    data at present.

    Args:
        image_path (str): the path to the LZ4 image we want to decompress.

    Returns:
        Tuple[np.array, fits.hdu.image.PrimaryHDU]: the image as a numpy array, and the FITS Primary HDU.
    '''
    assert(os.path.exists(image_path))
    assert(os.path.splitext(image_path)[1] == ".lz4")

    with lz4.frame.open(image_path, mode='rb') as fp:
        img = fits.open(fp, memmap=False, lazy_load_hdus=False)
        return (img[0].data, img[0].header)


def compress(data: np.array, header: fits.hdu.image.PrimaryHDU, image_path: str):
    ''' Given a FITS hdul, write this out to an lz4 compressed file.
    We unfortunately need to take the data out of the hdul and put it
    back in, so we just take the np.array and header as is.
    
    Args:
        data (np.array): the image to save.
        header (PrimaryHDU): the header to add to the FITS file.
        image_path (str): the image to save.
    '''
    assert(os.path.splitext(image_path)[1] == ".lz4")
    
    with lz4.frame.open(image_path, mode='wb') as fp:
        fits.writeto(fp, data, header=header)