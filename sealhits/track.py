"""
track.py - functions relating to tracks, such as overlaps.

A number of functions used to detect tracks
in the fan sonar images.
"""

from __future__ import annotations

__all__ = [
    "get_bounding_boxes",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from typing import List, Tuple
from sealhits.bbox import XYBox, points_to_bb
from sealhits.db.db import DB
from sealhits.db.dbschema import Images

ORIGINAL_BB = None  # naughty global for sorting


def get_bounding_boxes(
    db: DB, huid: str, imgs: List[Images], img_size: Tuple[int, int], fan_distort=True
) -> List[Tuple[int, XYBox, str]]:
    """Get the track details for this group.

    Args:
        db (DB): the database object.
        huid (str): the huid for hte group we are looking for.
        imgs (List[Images]): the list of Images records for this group.
        img_size (Tuple[int,int]): The size of the images in pixels. Width then height.
        fan_distort (bool): Are these images fans?

    Returns:
        List[Tuple[int, XYBox, str]]: a list of frame numbers, bounding boxes and corresponding colours.

    """
    bbs = []
    group = db.get_group_huid(huid)
    uid = group.uid

    for idx, img in enumerate(imgs):
        points = db.get_image_points_by_filename_group(img.filename, uid)

        if (
            len(points) > 0
        ):  # Since we have buffer start / end images and intermediates, 0 tracks are possible
            bb = points_to_bb(points, img.range)

            if fan_distort:
                bbox = bb.to_xy(img_size)
                ((xmin, ymin), (xmax, ymax)) = bbox.pair()

                # Flip BBS vertically to match flipped fan (normally flipped. #TODO - We should make this consistent)
                # This is a bit silly it seems
                bbs.append(
                    (idx, XYBox(xmin, img_size[1] - ymax, xmax, img_size[1] - ymin))
                )
            else:
                bbox = bb.to_xy_raw(img_size)

                # Flip BBS vertically to match flipped fan (normally flipped. #TODO - We should make this consistent)
                # This is a bit silly it seems
                bbs.append((idx, bbox))

    # Add a colour to the bounding box for ease of video and drawing.
    bbs = [(f, b, "#ff0000") for (f, b) in bbs]
    return bbs
