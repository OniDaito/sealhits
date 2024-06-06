"""
cache.py - caching functions.

We use several caches to speed things up, chief of which 
is the cached fan images of a particular size. These functions
help with saving and checking the caches.

All cached fan images are stored as FITS images with the same
name as their original image.
"""

from __future__ import annotations

__all__ = [
    "is_cached_fan",
    "np_fan_to_cache",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import os
import traceback
import numpy as np
from astropy.io import fits
from typing import Union
from sealhits.compress import compress


def is_cached_fan(cache_path: str, filename: str) -> Union[str, None]:
    """ Look in the directory for this particular fan image. If it exists,
    return the full path, or none if it doesnt. We 
    also consider non-gzipped files. Note, the size isn't checked so you
    might find the cached image larger or smaller than you require. 
    
    Args:
        cache_path (str): the path of the cache.
        filename (str): the filename we are looking for.

    Returns:
        Union[str, None]: The path in the cache to this file, or None.
    """
    #assert(os.path.exists(cache_path))

    tokens = filename.split("_")
    year = int(tokens[0])
    month = int(tokens[1])
    day = int(tokens[2])

    assert( year > 0 and month >= 0 and month <= 12 and day >=0 and day <= 31)
    
    subdir = tokens[0] + "_" + tokens[1] + "_" + tokens[2]

    # Prioritise unzipped if we have them
    upath = os.path.join(cache_path, subdir, filename)

    if os.path.exists(upath):
        return upath

    tpath = os.path.join(cache_path, subdir, filename + ".lz4")

    if os.path.exists(tpath):
        return tpath
    
    return None

def np_fan_to_cache(cache_path: str, filename: str, fan_image: np.array, compression=True):
    """ Given a filename in the correct format, save out this numpy fan
    as a FITS image in the correct subdir within the cache.
    
    Args:
        cache_path (str): the path of the cache.
        filename (str): the filename to save.
        fan_image (np.array): the image to save.
        compression (bool): should we compress.

    Returns:
        None
    """

    tokens = filename.split("_")

    # Options for compressed fits saving.
    if compression:
        if os.path.splitext(filename) != ".lz4":
            filename += ".lz4"
    else:
        filename = filename.replace(".lz4", "")

    year = int(tokens[0])
    month = int(tokens[1])
    day = int(tokens[2])

    assert( year > 0 and month >= 0 and month <= 12 and day >=0 and day <= 31)
    
    subdir = tokens[0] + "_" + tokens[1] + "_" + tokens[2]
    subdir = os.path.join(cache_path, subdir)
                    
    if not os.path.exists(subdir):
        os.mkdir(subdir)

    full_fits_path = os.path.join(subdir, filename)

    try:
        hdr = fits.Header()
       
        hdr["WIDTH"] = fan_image.shape[1]
        hdr["HEIGHT"] = fan_image.shape[0]
        hdr["YEAR"] = tokens[0]
        hdr["MONTH"] = tokens[1]
        hdr["DAY"] = tokens[2]
      
        if compression:
            compress(fan_image, hdr, full_fits_path)
        else:
            hdr = fits.PrimaryHDU(fan_image, header=hdr)
            hdul = fits.HDUList([hdr])
            hdul.writeto(full_fits_path, overwrite=True)

    except Exception as e:
        print(
            "Could not generate FITS:",
            full_fits_path,
            e,
        )
        print(traceback.format_exc())