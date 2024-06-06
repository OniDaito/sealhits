"""
utils.py - misc utility functions.

Useful utilities for various Sealhits related tasks.
"""

from __future__ import annotations

__all__ = [
    "dist_bearing_to_xy",
    "find",
    "fast_find",
    "get_fan_size",
    "create_dir",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import os
import fnmatch
import math
from typing import Tuple, List, Union


def dist_bearing_to_xy(
    bearing: float, distance: float, max_range: float, image_size: Tuple[int, int]
) -> Tuple[int, int]:
    """Convert bearing (radians) and distance from a track to fan/polar image x, y coords.
    Image size is width/height. X and Y are integers within image_size.
    
    Args:
       bearing (float): the bearing in radians.
       distance (float): the distance in metres.
       max_range (float): the maximum possible range (the sonar range) in metres.
       image_size: the size of the image in pixels - width then height.

    Returns:
       Tuple[int, int]: the x and y coordinates in pixels.
    """

    # Assume bearing is either side of the vertical line?
    # Assume distance is in metres with the max being passed in as max_range
    # assert math.degrees(bearing) >= MIN_ANGLE and math.degrees(bearing) <= MAX_ANGLE

    # We are effectively rotating this 90 degrees anti clockwise and a POSITIVE bearing
    # should be to the LEFT of the centre line post rotation (this seems silly but is
    # the way according to PAMGuard)

    # TODO - we are returning integers here. We might wish to do floats at some point
    # so we can do interpolation.    
    d0 = float(distance / max_range * image_size[1])
    x0 = math.sin(math.fabs(bearing)) * d0
    y0 = math.cos(math.fabs(bearing)) * d0

    hl = image_size[0] / 2

    if bearing > 0:
        x0 = hl - x0
    else:
        x0 = hl + x0

    return (int(x0), int(y0))


def find(pattern: str, path: str) -> List[str]:
    """Find a file somewhere underneath path, matching the pattern.
    Args:
       pattern (str): a pattern string for fnmatch.
       distance (float): a path to a directory to search.

    Returns:
       List[str]: the resulting files as full paths.
    """
    results = []

    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                results.append(os.path.join(root, name))

    return results


def fast_find(name: str, base_path: str) -> Union[str, None]:
    """Find the full FITS bath based on how we store the images.
    This is much faster than a full path walk. We also look for
    images without the .lz4 extension. We prioritise the non 
    compressed file.
    
    Args:
       name (str): the file we are looking for.
       base_path (str): the directory we are searching.

    Returns:
       Union[str, None]: the path to the file if found, or None.
    """

    joined_unzipped = os.path.join(base_path, name)
    if os.path.exists(joined_unzipped):
        return joined_unzipped
    
    joined = os.path.join(base_path, name + ".lz4")
    if os.path.exists(joined):
        return joined

    for tt in os.listdir(base_path):
        tt = os.path.join(base_path, tt)

        if os.path.isdir(tt):
            full_path_unzipped = os.path.join(tt, name)

            if os.path.isfile(full_path_unzipped):
                return full_path_unzipped
            
            full_path = os.path.join(tt, name + ".lz4")

            if os.path.isfile(full_path):
                return full_path

    print("Could not find:", name)
    return None


def get_fan_size(height: int) -> Tuple[int, int]:
    """ Return a fan size, given the height. Uses a ratio of 1.732 
    given the 120 degree spread.
    
    Args:
       height (int): the height we want in pixels.

    Returns:
       Tuple[int, int]: the width and height of the fan image in pixels.
    """
    return (int(math.floor(1.732 * float(height))), height)


def create_dir(path: str) -> bool:
    """Create a directory if it doesn't already exist.
    
    Args:
        path (str): the path to the directory we want to make.
    
    Returns:
        bool: success?
        
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception:
            return False

    return True
