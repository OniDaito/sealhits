"""
dbsearch.py - The Postgresql search functions.

Various functions for finding and generating
data from our images and database. 
"""

from __future__ import annotations

__all__ = [
    "gid_to_fans_imgs",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import numpy as np
import math
from . import utils
from . import image
from . import btable
from astropy.io import fits
from sealhits.db.db import DB
from sealhits.db.dbschema import Images
from tqdm import tqdm
from typing import List, Tuple


def gid_to_fans_imgs(uid:str, db:DB, fits_path: str, sonar_id: int, scale_factor=1.0, limit=-1) -> List[Tuple[np.array, Images]]:
    """ Given a GID, DB, path to fits files and sonarid, return the 
    fan images for a particular group along with the filename path. The fan
    image sizes are created using the heighest resolution.
    
    Args:
        uid (str): uid or huid of the group as a string.
        db (DB): The active database object.
        fits_path (str): The path the fits files.
        sonar_id (int): The sonar_id.
        scale_factor (float): optional scaling factor for the fan images.
        limit (int): optional number of results to process (-1 is no limit)

    Returns:
        List[Tuple[np.array, Images]]: a list of both the fans and their associate Images records.
    
    """
    current_frames = []
    results = db.get_images_group(uid, sonar_id)     

    if results is not None:
        if limit > 0:
            results = results[:limit]
            
        # Do the resize only once - All images in the group
        # should be the same. It'd be bad otherwise
        fname = results[0].filename
        fresult = utils.fast_find(fname, fits_path)

        hdul = fits.open(fresult)
        fits_height = int(hdul[0].data.shape[0])

        if scale_factor != 1.0:
            fits_height = int(math.floor(fits_height * scale_factor))

        for idx, img in enumerate(tqdm(results)):
            fname = img.filename
            fresult = utils.fast_find(fname, fits_path)
    
            if fresult is not None:
                # Start with the sonar image
                # We need flip up down and left right!
                hdul = fits.open(fresult)
                fan_image = image.fan_distort(hdul[0].data, fits_height, btable.bearing_table)
                current_frames.append(np.fliplr(np.flipud(fan_image)))
    
    return zip(current_frames, results)
    
