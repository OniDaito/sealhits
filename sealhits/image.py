"""
image.py - functions for reading and drawing images.

Functions related to drawing out images.
"""

from __future__ import annotations

__all__ = ["draw_bb", "draw_text", "fan_distort", "normalise_image"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import datetime
import math
import os
import uuid
import numpy as np
import numba
from PIL import ImageDraw
from astropy.io import fits
from typing import Tuple, Union, List
from sealhits.constants import MAX_ANGLE, MIN_ANGLE
from sealhits.utils import fast_find
from sealhits.bbox import XYBox
from PIL import Image
from sealhits.compress import decompress
from sealhits.btable import bearing_table
from numba.typed import List as NumbaList
from sealhits.cache import is_cached_fan
from sealhits.db.db import DB
from sealhits.db.dbschema import Images


def draw_bb(image: Image, bb: XYBox, colour="#1111ff"):
    """Given an RGB Fan distorted image and a set of bb coords, draw a bounding box.

    Args:
        image (PIL.Image): the PIL Image to draw on.
        bb (XYBox): the box to draw.
        colour (str): the colour of the box as an '#rrggbb' string.
    """
    assert image.mode == "RGB"
    draw = ImageDraw.Draw(image)
    ((x0, y0), (x1, y1)) = bb.pair()
    xy = ((x0, y0), (x0, y1), (x1, y1), (x1, y0))
    draw.polygon(xy, fill=None, outline=colour)


def draw_text(image: Image, pos: Tuple[int, int], colour="#1111ff", text="none"):
    """Draw some text on our image.

    Args:
        image (PIL.Image): the PIL Image to draw on.
        pos (Tuple[int, int]): the coordinates to draw at.
        colour (str): the colour of the box as an '#rrggbb' string.
        text (str): the text to draw.
    """
    draw = ImageDraw.Draw(image)
    draw.text(pos, text, align="left", fill=colour)


def np_to_fits(save_path: str, img: np.array, image_time: datetime.datetime):
    """Given an np array, write out our fits image to a cache.

    Args:
        save_path (str): the path and filename to save the fits to.
        img (np.array): the image to save.
        image_time: the time the image was taken.
    """

    if not os.path.exists(save_path):
        try:
            hdr = fits.Header()
            hdr["WIDTH"] = img.shape[1]
            hdr["HEIGHT"] = img.shape[0]
            hdr["YEAR"] = image_time.year
            hdr["MONTH"] = image_time.month
            hdr["DAY"] = image_time.day
            hdr["HOUR"] = image_time.hour
            hdr["MINUTE"] = image_time.minute
            hdr["SECOND"] = image_time.second
            hdr["MILLI"] = int(image_time.microsecond / 1000)
            hdr = fits.PrimaryHDU(img, header=hdr)
            hdul = fits.HDUList([hdr])
            hdul.writeto(save_path)
        except Exception as e:
            print("Could not save fits image:", save_path, e)


def fits_to_np(fits_path: str) -> Tuple[np.array, fits.hdu.image.PrimaryHDU]:
    """Given a path to a FITS file, attempt to return the numpy array and
    the fits header, or None if fails.

    Args:
        fits_path (str): the path to the fits to load.

    Returns:
        Tuple[np.array, fits.hdu.image.PrimaryHDU]: the loaded image as np.array and the FITS PrimaryHDU.
    """
    if ".lz4" in fits_path:
        return decompress(fits_path)

    img = fits.open(fits_path, memmap=False, lazy_load_hdus=False)
    return (img[0].data, img[0].header)


# @numba.jit(nopython=True, parallel=True)
@numba.njit
def fan_distort(
    input_array: np.ndarray, fan_height: int, bearing_table: NumbaList[float]
) -> np.ndarray:
    """The fan distortion function. We choose a height that works as our
    scaling ratio (1.732).

    Args:
        input_array (np.ndarray): the image to distort.
        fan_height (int): the height of the resulting fan image.
        bearing_table (NumbaList[float]): The bearing table.

    Returns:
        np.ndarray: the new fan image.

    """
    fan_size = (
        int(math.floor(1.732 * float(fan_height))),
        fan_height,
    )  # cant use get_fan_size(fan_height) function with numba sadly
    fan_image = np.zeros((fan_height, fan_size[0]))
    hx = int(fan_size[0] / 2)

    # Allow any width, not just 512.
    wratio = float(input_array.shape[1]) / 512.0

    # TODO - Definitely room for speedup here - can use tables and lookups.
    # TODO - bilinear filtering - but as an option as masks shouldn't be filtered.

    for y in range(1, fan_height):
        # Limit x range as we progress up the fan
        tt = int(y * math.tan(math.radians(60)))
        sx = max(0, hx - tt - 10)
        sy = min(fan_size[0], hx + tt + 10)

        for x in range(sx, sy):
            dx = int(x - hx)
            bearing = 0

            if dx != 0:
                bearing = math.atan2(dx, y)

            bearing_deg = math.degrees(bearing)

            if bearing_deg >= MIN_ANGLE and bearing_deg <= MAX_ANGLE:
                # We are inside the sweep so we need to now find the lookup
                # in the original image. However, we have a non-linear relationship
                # between the sonar x position and the true bearing, so we need
                # to find the closest sample point to our bearing via the lookup
                # table
                bearing_sidx = 0
                distance = int(
                    y / math.cos(math.fabs(bearing)) / fan_height * input_array.shape[0]
                )

                if distance < 0 or distance >= input_array.shape[0]:
                    continue

                for idx in range(511):  # Size of the bearing table
                    bt = bearing_table.getitem_unchecked(
                        idx
                    )  # This seems to speed up the numbalist stuff a lot!
                    bn = bearing_table.getitem_unchecked(idx + 1)

                    if bt >= bearing and bn < bearing:
                        bearing_sidx = int(float(idx) * wratio)
                        break

                sample = input_array[distance][bearing_sidx]
                fan_image[y][x] = sample

    return fan_image


def normalise_image(img: np.array) -> np.array:
    """Normalise the image to range 0 to 1.
    
    Args:
        img (np.array): the image to normalise.

    Returns:
        np.array: the normalised image (with a float32 type)
    """
    fimg = img.astype(np.float32)
    min_val = np.min(img)
    max_val = np.max(img)
    rval = (fimg - min_val) / (max_val - min_val)
    return rval


def get_group_images(
    db: DB,
    fits_path: str,
    group_id: Union[uuid.UUID, str],
    sonar_id=854,
    height=400,
    cache_path=".",
    fan_transform=True,
) -> Tuple[np.array, List[Images]]:
    """Return the image data and images for the group with this HUID. We check the
    cache first. All images must be preset and the correct size, otherwise we generate
    from new.

    Args:
        db (DB): the database object.
        fits_path (str): the path to the fits files.
        group_id (group_id: Union[uuid.UUID, str]): either the uid or the huid for the group.
        sonar_id (int): the id of the sonar to export.
        height (int): the height of the resulting images.
        cache_path (str): the path to the image cache.
        fan_transform (bool): return fans instead of rectangles.

    Returns:
        Tuple[np.array, List[Images]]: the images as a 3D np.array and a list of Images objects for each frame/image.

    """
    if type(group_id) is uuid.UUID:
        group_uid = group_id
    else:
        g = db.get_group_huid(group_id)
        group_uid = g.uid

    group = db.get_group_uid(group_uid)
    uid = group.uid
    group_images = db.get_images_group_sonarid(uid, sonar_id)
    imgs = []
    num_images = len(group_images)

    if num_images <= 0:
        print("No images found for group", uid)
        return None

    np_frames = []
    # Find all the images and create the base frames. Must be in the cache! Is probably
    # compressed as well.

    for img in group_images:
        dpath = is_cached_fan(cache_path, img.filename)
        cached = False

        if dpath is not None:
            data, header = decompress(dpath)
            np_frames.append(data)
            cached = True

        if not cached:
            fresult = fast_find(img.filename, fits_path)
            if fresult is not None:
                data, _ = fits_to_np(fresult)
                if fan_transform:
                    fan_image = np.fliplr(
                        np.flipud(fan_distort(data, height, bearing_table))
                    )
                    np_frames.append(fan_image)
                else:
                    np_frames.append(data)

        imgs.append(img)

    # It is possible, for some reason, that frames may not be the same size when in the RAW form, so
    # we run a check, making all images equal to the first. If the difference is too big we throw an error
    if not fan_transform:
        tframes = np_frames.copy()
        np_frames = []
        first_shape = tframes[0].shape
        np_frames.append(tframes[0])

        for frame in tframes[1:]:
            # Row differences
            diff = first_shape[0] - frame.shape[0]

            if abs(diff) > 1:
                raise AssertionError(
                    "get_groups_images: RAW images in group differ too much"
                )

            if diff == -1:
                np.delete(frame, -1, 0)

            if diff == 1:
                frame = np.append(frame, np.zeros((1, first_shape[1])), 0)

            # Column differences
            diff = first_shape[1] - frame.shape[1]

            if abs(diff) > 1:
                raise AssertionError(
                    "get_groups_images: RAW images in group differ too much"
                )

            if diff == -1:
                np.delete(frame, -1, 1)

            if diff == 1:
                frame = np.append(frame, np.zeros((first_shape[0], 1)), 1)

            np_frames.append(frame)

    try:
        np_frames = np.stack(np_frames)
    except Exception as e:
        print(e)
        return None

    return np_frames, imgs
