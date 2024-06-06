"""
bbox.py - Classes and functions related to bounding boxes.
"""

from __future__ import annotations

__all__ = [
    "XYBox",
    "BearBox",
    "bb_expand",
    "bb_to_min",
    "bb_to_fix",
    "points_to_bb",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import math
from sealhits.db.dbschema import Points
from sealhits.utils import dist_bearing_to_xy
from sealhits.constants import MAX_ANGLE, MIN_ANGLE
from typing import List, Tuple, Union


class XYZBox:
    def __init__(
        self, minx: int, miny: int, minz: int, maxx: int, maxy: int, maxz: int
    ):
        """Initialise a 3D bounding box.

        Args:
            minx (int): minimum x value in pixels.
            miny (int): minimum y value in pixels.
            minz (int): minimum z value in pixels.
            maxx (int): maximum x value in pixels.
            maxy (int): maximum y value in pixels.
            maxz (int): maximum z value in pixels.
        """
        self.x_min = minx
        self.y_min = miny
        self.z_min = minz
        self.x_max = maxx
        self.y_max = maxy
        self.z_max = maxz

    def __str__(self):
        return (
            str(self.x_min)
            + ","
            + str(self.y_min)
            + ","
            + str(self.z_min)
            + ","
            + str(self.x_max)
            + ","
            + str(self.y_max)
            + ","
            + str(self.z_max)
        )

    def volume(self) -> int:
        """Return the volume of this bbox.
        Args:
            None

        Returns:
            int: the volume
        """
        # Z is always a minimum of 1, as zmax can equal zmin - this XYZBox is ultimately an XYBox
        return (
            (self.x_max - self.x_min)
            * (self.y_max - self.y_min)
            * max(self.z_max - self.z_min, 1)
        )

    def tuple(self) -> Tuple[int, int, int, int, int, int]:
        """Return the box as a Tuple
        Args:
            None

        Returns:
            Tuple[int,int,int,int,int,int]: the volume as xmin,ymin,zmin,xmax,ymax,zmax
        """
        return (self.x_min, self.y_min, self.z_min, self.x_max, self.y_max, self.y_max)

    def pair(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Return the box as two Tuples
        Args:
            None

        Returns:
            Tuple[Tuple[int,int,int],Tuple[int,int,int]]: the volume as [xmin,ymin,zmin],[xmax,ymax,zmax]
        """
        return (
            (self.x_min, self.y_min, self.z_min),
            (self.x_max, self.y_max, self.z_max),
        )

    def com(self) -> Tuple[int,int,int]:
        """Return the centre of this bbox.
        Args:
            None

        Returns:
            Tuple[int,int,int]: the centre of this bounding box, rounded and as ints.
        """
        return (
            int((self.x_max + self.x_min) / 2),
            int((self.y_max + self.y_min) / 2),
            int((self.z_max + self.z_min) / 2),
        )

    def equals(self, b: XYZBox) -> bool:
        """Does this box equal another?
        Args:
            b (XYZBox): the other box to compare against

        Returns:
            bool
        """
        return (
            self.x_min == b.x_min
            and self.x_max == b.x_max
            and self.y_min == b.y_min
            and self.y_max == b.y_max
            and self.z_min == b.z_min
            and self.z_max == b.z_max
        )


class XYBox:
    """A basic XY bounding box using minimums and maximums."""

    def __init__(self, minx: int, miny: int, maxx: int, maxy: int):
        """Create a 2D Bounding Box.
        Args:
            minx(int): minimum x value in pixels.
            miny(int): minimum y value in pixels.
            maxx(int): maximum x value in pixels.
            maxy(int): maximum y value in pixels.
        """
        self.x_min = minx
        self.y_min = miny
        self.x_max = maxx
        self.y_max = maxy

    def __str__(self):
        return (
            str(self.x_min)
            + ","
            + str(self.y_min)
            + ","
            + str(self.x_max)
            + ","
            + str(self.y_max)
        )

    def area(self) -> int:
        """Return the area of this bbox.
        Args:
            None

        Returns:
            int: the area
        """
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    def tuple(self) -> Tuple[int, int, int, int]:
        """Return the box as a Tuple
        Args:
            None

        Returns:
            Tuple[int,int,int,int]
        """
        return (self.x_min, self.y_min, self.x_max, self.y_max)

    def pair(self) -> Tuple[Tuple[int,int],Tuple[int,int]]:
        """Return the box as two Tuples

        Returns:
            Tuple[Tuple[int,int],Tuple[int,int]]: the box as [xmin,ymin],[xmax,ymax]
        """
        return ((self.x_min, self.y_min), (self.x_max, self.y_max))

    def com(self) -> Tuple[int,int]:
        """Return the centre of this bbox.
        Args:
            None

        Returns:
            Tuple[int,int]: the centre of this bounding box, rounded and as ints.
        """
        return (int((self.x_max + self.x_min) / 2), int((self.y_max + self.y_min) / 2))

    def flipv(self, img_height):
        """An in-place flip vertically.

        Args:
            img_height (int): the height of the image to which this box belongs.
        """
        tt = self.y_max
        self.y_max = img_height - self.y_min
        self.y_min = img_height - tt
        return self

    def equals(self, b) -> bool:
        """Does this box equal another?
        Args:
            b (XYBox): the other box to compare against

        Returns:
            bool
        """
        return (
            self.x_min == b.x_min
            and self.x_max == b.x_max
            and self.y_min == b.y_min
            and self.y_max == b.y_max
        )


class BearBox:
    def __init__(
        self,
        bearmin: float,
        bearmax: float,
        distmin: float,
        distmax: float,
        sonar_range: float,
    ):
        """Bearings are in radians and are left-/right+ of the vertical / Y axis, but from the top. Sonar range is the range
        the sonar was set to in metres.

        Args:
           bearmin (float): The minimum bearing.
           bearmax (float): The maximum bearing.
           distmin (float): The minimum distance.
           distmax (float): The maximum distance.
           sonar_range (float): The range of the sonar at this point (in metres).
        """
        self.bearing_min = bearmin
        self.bearing_max = bearmax
        self.dist_min = distmin
        self.dist_max = distmax
        self.sonar_range = sonar_range

    def to_xy_raw(self, image_size: Tuple[int, int]) -> XYBox:
        """Return a bearing box that is x,y but for the RAW, non-fan image.
        This image may be resized from the original but is still a rectangle. with
        no spatial distortion.

        Args:
            image_size (Tuple[int, int]): the size of the image this raw box belongs to (in pixels, width then height).

        Returns:
            XYBox: A new XYBox but within the *raw* image space (i.e original, not fan/polar transformed)

        """
        from sealhits.btable import bearing_table

        def _find_idx(c):
            for i in range(len(bearing_table) - 1):
                a = bearing_table[i]
                b = bearing_table[i + 1]

                if a >= c and b < c:
                    return i

            return 0

        # xmin = int(((-self.bearing_max - math.radians(MIN_ANGLE)) / (math.radians(MAX_ANGLE) - math.radians(MIN_ANGLE))) * image_size[0])
        # xmax = int(((-self.bearing_min - math.radians(MIN_ANGLE)) / (math.radians(MAX_ANGLE) - math.radians(MIN_ANGLE))) * image_size[0])
        r = float(image_size[0]) / float(len(bearing_table))
        xmin = int(
            _find_idx(self.bearing_max) * r
        )  # Swap due to the bearings being postive to negative
        xmax = int(_find_idx(self.bearing_min) * r)

        ymin = int(self.dist_min / self.sonar_range * image_size[1])
        ymax = int(self.dist_max / self.sonar_range * image_size[1])

        return XYBox(xmin, ymin, xmax, ymax)

    def to_xy(self, image_size: Tuple[int, int]) -> XYBox:
        """Given a fan/polar image size return the minx/y maxx/y in pixel coordinates.
        Image size is width/height. Resulting xy assumes origin at top left.

        Args:
            image_size (Tuple[int, int]): the size of the image this raw box belongs to (in pixels, width then height).

        Returns:
            XYBox: A new XYBox but within the *polar* image space (i.e fan/polar transformed, not raw rectangle)


        """
        txy = []
        txy.append(
            dist_bearing_to_xy(
                self.bearing_min, self.dist_min, self.sonar_range, image_size
            )
        )
        txy.append(
            dist_bearing_to_xy(
                self.bearing_max, self.dist_max, self.sonar_range, image_size
            )
        )
        txy.append(
            dist_bearing_to_xy(
                self.bearing_min, self.dist_max, self.sonar_range, image_size
            )
        )
        txy.append(
            dist_bearing_to_xy(
                self.bearing_max, self.dist_min, self.sonar_range, image_size
            )
        )

        min_x = txy[0][0]
        min_y = txy[0][1]
        max_x = txy[0][0]
        max_y = txy[0][1]

        for tt in txy[1:]:
            if tt[0] < min_x:
                min_x = tt[0]
            if tt[0] > max_x:
                max_x = tt[0]
            if tt[1] < min_y:
                min_y = tt[1]
            if tt[1] > max_y:
                max_y = tt[1]

        return XYBox(min_x, min_y, max_x, max_y)

    def __str__(self):
        return (
            str(self.bearing_min)
            + ","
            + str(self.bearing_max)
            + ","
            + str(self.dist_min)
            + ","
            + str(self.dist_max)
        )


def bb_expand(
    bb: Union[XYBox, XYZBox],
    img_size: Union[Tuple[int, int], Tuple[int, int, int]],
    b_size: Union[int, Tuple],
) -> Union[XYBox, XYZBox]:
    """ Expand the bounding box. bb is either an XYBox or XYZ Box. img_size
    is a tuple of either (w,h) or (w,h,d). b_size is either a single int, or
    a tuple of different sizes.

    Args:
        bb (Union[XYBox, XYZBox]): the XYBox or XYZBox to expand.
        img_size (Union[Tuple[int, int], Tuple[int, int, int]]): The size of the image to which this box belongs, in pixels.
        b_size (Union[int, Tuple]): the amount to expand either uniformly (a single int), or expand by different amounts in each dimension.

    Returns:
        Union[XYBox, XYZBox]: A new XYBox or XYZBox but within the *raw* image space (i.e original, not fan/polar transformed)
    """

    be = []

    if hasattr(b_size, "__iter__"):
        if len(b_size) < 2:
            # TODO - maybe raise an error/exception here?
            return bb

        be = b_size

    elif isinstance(b_size, int):
        if b_size <= 0:
            return bb

        be = [b_size, b_size, b_size]

    x = bb.x_min
    y = bb.y_min
    a = bb.x_max
    b = bb.y_max

    c = 0
    z = 0

    w = a - x
    h = b - y
    d = 0

    if hasattr(bb, "z_min"):
        z = bb.z_min
        c = bb.z_max
        d = c - z
        d = d + be[2]
        z = z - be[2]

    x = x - be[0]

    if x <= 0:
        x = 0

    if x >= img_size[0]:
        x = img_size[0] - 1

    y = y - be[1]

    if y <= 0:
        y = 0

    if y >= img_size[1]:
        y = img_size[1] - 1

    w += be[0]

    if w >= img_size[0]:
        w = img_size[0] - 1

    h += be[1]

    if h >= img_size[1]:
        h = img_size[1] - 1

    if hasattr(bb, "z_min"):
        if z <= 0:
            z = 0

        if z >= img_size[2]:
            z = img_size[2] - 1

        if d <= 0:
            d = 0

        if d >= img_size[2]:
            d = img_size[2] - 1

        return XYZBox(x, y, z, x + w, y + h, z + d)

    return XYBox(x, y, x + w, y + h)


def bb_to_min(
    bbox: XYBox, min_size: Tuple[int, int], image_size: Tuple[int, int]
) -> XYBox:
    """Given an XYBox, return an xy crop size that has a minimum size
    and is within the image size. Image size is height/width.

    Args:
        bbox (XYBox): the XYBox to crop.
        min_size (Tuple[int, int]): the new minimum size.
        image_size (Tuple[int, int]): the size of the image to which this bbox belongs.

    Returns:
        XYBox: the new XYBox.
    """

    ((min_x, min_y), (max_x, max_y)) = bbox.pair()
    x = min_x
    y = min_y

    w = max_x - x
    h = max_y - y

    if h < min_size[1]:
        d = (min_size[1] - h) / 2
        max_y += d
        min_y -= d

        # Checks to see if we are exceeding the size of the image
        if min_y < 0:
            dd = 0 - min_y
            min_y = 0
            max_y += dd

        if max_y > image_size[1]:
            dd = max_y - image_size[1]
            min_y -= dd
            max_y -= dd

    # Now do the width
    if w < min_size[0]:
        d = (min_size[0] - w) / 2
        max_x += d
        min_x -= d

        if min_x < 0:
            dd = 0 - min_x
            min_x = 0
            max_x += dd

        if max_x > image_size[0]:
            dd = max_x - image_size[0]
            min_x -= dd
            max_x -= dd

    return XYBox(int(min_x), int(min_y), int(max_x), int(max_y))


def bb_to_fix(
    bbox: XYBox, fix_size: Tuple[int, int], image_size: Tuple[int, int]
) -> XYBox:
    """ Given an XYBox, a fix_size and image_size, return an xy crop size that has a fixed size.
    Image size is width/height.
    
    Args:
        bbox (XYBox): the XYBox we are changing.
        fix_size (Tuple[int, int]): the new fixed size.
        image_size (Tuple[int, int]): the size of the image to which this bbox belongs.

    Returns:
        XYBox: the new XYBox with the new size.
    """

    ((min_x, min_y), (max_x, max_y)) = bbox.pair()

    cx = int((max_x + min_x) / 2)
    cy = int((max_y + min_y) / 2)

    s_x = cx - int(fix_size[0] / 2)
    s_y = cy - int(fix_size[1] / 2)

    e_x = cx + int(fix_size[0] / 2)
    e_y = cy + int(fix_size[1] / 2)

    if s_x < 0:
        dd = 0 - s_x
        s_x = 0
        e_x += dd

    if e_x >= image_size[0]:
        dd = e_x - image_size[0]
        s_x -= dd
        e_x -= dd

    if s_y < 0:
        dd = 0 - s_y
        s_y = 0
        e_y += dd

    if e_y >= image_size[1]:
        dd = e_y - image_size[1]
        s_y -= dd
        e_y -= dd

    return XYBox(int(s_x), int(s_y), int(e_x), int(e_y))


def bb_raw_to_fan(
    bbox: Union[XYBox, XYZBox],
    raw_size: Tuple(int, int),
    fan_size: Tuple(int, int),
    sonar_range: float,
) -> Union[XYBox, XYZBox]:
    """Given an XY or XYZ bounding box in the raw image space, convert
    to fan space.

    Args:
        bbox (Union[XYBox, XYZBox]): the XYBox or XYZBox to convert.
        raw_size (Tuple[int, int]): the size of the raw rectangle.
        fan_size (Tuple[int, int]): the size of the fan image.
        sonar_range (float): the range of the sonar in this image

    Returns:
        Union[XYBox, XYZBox]: the new XYBox or XYZBox.
    """
    from sealhits.btable import bearing_table

    x_min = bearing_table[max(bbox.x_min, 0)]
    x_max = bearing_table[min(bbox.x_max, len(bearing_table) - 1)]
    y_min = bbox.y_min / raw_size[1] * sonar_range
    y_max = bbox.y_max / raw_size[1] * sonar_range

    txy = []
    txy.append(dist_bearing_to_xy(x_min, y_min, sonar_range, fan_size))
    txy.append(dist_bearing_to_xy(x_max, y_max, sonar_range, fan_size))
    txy.append(dist_bearing_to_xy(x_min, y_max, sonar_range, fan_size))
    txy.append(dist_bearing_to_xy(x_max, y_min, sonar_range, fan_size))

    min_x = txy[0][0]
    min_y = txy[0][1]
    max_x = txy[0][0]
    max_y = txy[0][1]

    for tt in txy[1:]:
        if tt[0] < min_x:
            min_x = tt[0]
        if tt[0] > max_x:
            max_x = tt[0]
        if tt[1] < min_y:
            min_y = tt[1]
        if tt[1] > max_y:
            max_y = tt[1]

    return XYBox(min_x, min_y, max_x, max_y)


def bb_inside(a: Union[XYBox, XYZBox], b: Union[XYBox, XYZBox]) -> bool:
    """Return true if a is completely enclosed by b. False otherwise.
    
    Args:
        a (Union[XYBox, XYZBox]): the XYBox or XYZBox.
        b (Union[XYBox, XYZBox]): the XYBox or XYZBox.

    Returns:
       bool: is a *completely* enclosed by b?
    """

    if type(a) != type(b):
        return False

    if a.x_min >= b.x_min and a.x_max <= b.x_max:
        if a.y_min >= b.y_min and a.y_max <= b.y_max:
            if hasattr(a, "z_min") and hasattr(b, "z_min"):
                if a.z_min >= b.z_min and a.z_max <= b.z_max:
                    return True
            else:
                return True
    return False


def bb_overlap(a: Union[XYBox, XYZBox], b: Union[XYBox, XYZBox]) -> bool:
    """Return True if two boxes overlap, False if not. Takes either an XYBox or
    XYZ box. For now, both a and b must be the same type, else False is returned.
    
    Args:
        a (Union[XYBox, XYZBox]): the XYBox or XYZBox.
        b (Union[XYBox, XYZBox]): the XYBox or XYZBox.

    Returns:
        bool: do a and b overlap?
    
    """
    if type(a) != type(b):
        return False

    if a.x_min <= b.x_max and a.x_max >= b.x_min:
        if a.y_min <= b.y_max and a.y_max >= b.y_min:
            if hasattr(a, "z_min") and hasattr(b, "z_min"):
                if a.z_min <= b.z_max and a.z_max >= b.z_min:
                    return True
            else:
                return True
    return False


def bb_combine(
    a: Union[XYBox, XYZBox], b: Union[XYBox, XYZBox]
) -> Union[XYBox, XYZBox]:
    """Combine two bounding boxes into one. Either XYBox or XYZBox.
    
    Args:
        a (Union[XYBox, XYZBox]): the XYBox or XYZBox.
        b (Union[XYBox, XYZBox]): the XYBox or XYZBox.

    Returns:
        Union[XYBox, XYZBox]: the combined box.
    """
    assert type(a) == type(b)

    x_min = min(a.x_min, b.x_min)
    y_min = min(a.y_min, b.y_min)

    x_max = max(a.x_max, b.x_max)
    y_max = max(a.y_max, b.y_max)

    if hasattr(a, "z_min"):
        z_min = min(a.z_min, b.z_min)
        z_max = max(a.z_max, b.z_max)

        return XYZBox(x_min, y_min, z_min, x_max, y_max, z_max)

    return XYBox(x_min, y_min, x_max, y_max)


def combine_boxes(bbs: List[Union[XYBox, XYZBox]]) -> Tuple[List[Union[XYBox, XYZBox]], List[Union[XYBox, XYZBox]]]:
    """Given a list of 2D or 3D bbs, combine if they overlap.
    Overlapping groups are joined to create a bigger group,
    which makes further overlapping easier. 2D boxes are assumed
    to all be on the same Z step.

    This algorithm has bad complexity though and needs
    improvement.
    
    Args:
        bbs (List[Union[XYBox, XYZBox]]): a list of either XYBox or XYZBox.
      
    Returns:
        Tuple[List[Union[XYBox, XYZBox]], List[Union[XYBox, XYZBox]]]: Two lists - new boxes combined and a list of many lists of the grouped boxes.
    """
    merged = True
    new_bbs = bbs.copy()
    bbs_grouped = [[a] for a in new_bbs]

    while merged:
        # Create a pairwise matrix of all combinations
        pairwise = []

        # Divide list into pairs
        for i in range(0, len(new_bbs) - 1):
            for j in range(i + 1, len(new_bbs)):
                pairwise.append((i, j))

        merged = False
        # Now combine if we can
        for i, j in pairwise:
            a = new_bbs[i]
            b = new_bbs[j]

            if bb_overlap(a, b):
                new_bbs.pop(j)  # Pop j first as it's always larger
                new_bbs.pop(i)
                c = bb_combine(a, b)
                d = bbs_grouped.pop(j)
                e = bbs_grouped.pop(i)
                f = d + e
                bbs_grouped.append(f)
                new_bbs.append(c)
                merged = True
                break

        del pairwise[:]

    return new_bbs, bbs_grouped


def points_to_bb(points: List[Points], sonar_range: float) -> BearBox:
    """Given a list of points, generate the bounding box for them.
    The list of points is from the db and is  (time, sonarid, minbearing, maxbearing, minrange,
    maxrange, track, uid). All points should be from the same sonar.

    The max sonar range can change and therefore needs to be passed in.

    Args:
        points (List[Points]): a list of Points.
        sonar_range (float): the range of the sonar at this time.

    Returns:
        BearBox
    """

    # Assume the min/maxes based on the sonar
    bearing_limits = (math.radians(MIN_ANGLE), math.radians(MAX_ANGLE))
    distance_limits = (0.0, sonar_range)
    min_b = bearing_limits[1]
    max_b = bearing_limits[0]
    min_d = distance_limits[1]
    max_d = distance_limits[0]

    # TODO - Minbearing and maxbearing have been swapped here! It works but clearly
    # there is an issue somehere in what min and max actually mean in the PAMGuard
    # database
    for point in points:
        if point.maxbearing < min_b and point.maxbearing >= bearing_limits[0]:
            min_b = point.maxbearing

        if point.minbearing > max_b and point.minbearing < bearing_limits[1]:
            max_b = point.minbearing

        if point.minrange < min_d and point.minrange >= distance_limits[0]:
            min_d = point.minrange

        if point.maxrange > max_d and point.maxrange < distance_limits[1]:
            max_d = point.maxrange

    bb = BearBox(min_b, max_b, min_d, max_d, sonar_range)
    return bb
