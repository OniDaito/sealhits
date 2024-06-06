'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_boxes.py - test bounding boxes.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Testing the various bounding boxes against
what we get from the equivalent PAMGuard.
'''

import math
from sealhits.bbox import bb_expand, combine_boxes, XYBox, XYZBox, BearBox, bb_to_fix, bb_inside


def test_bbox():
    pass


def test_inside():
    aa = XYBox(11, 11, 20, 20)
    bb = XYBox(10, 10, 30, 30)

    assert bb_inside(aa, bb) is True

    aa = XYZBox(10, 10, 10, 12, 12, 12)
    bb = XYZBox(0, 0, 0, 30, 30, 30)

    assert bb_inside(aa, bb) is True


def test_fix():
    bb = XYBox(10, 10, 30, 30)
    fbb = bb_to_fix(bb, (50, 50), (100, 100))

    assert fbb.x_min == 0
    assert fbb.y_max == 50

    bb = XYBox(0, 0, 30, 30)
    fbb = bb_to_fix(bb, (50, 50), (100, 100))

    assert fbb.x_min == 0
    assert fbb.y_max == 50

    bb = XYBox(50, 50, 70, 60)
    fbb = bb_to_fix(bb, (50, 50), (200, 200))

    assert fbb.x_min == 35
    assert fbb.y_max == 80

def test_bear_to_xy():
    bb = BearBox(math.radians(-5.0), math.radians(5.0), 26, 28, 55)
    bb_raw = bb.to_xy((692, 400))

    assert bb_raw.x_min == 328
    assert bb_raw.x_max == 363
    assert bb_raw.y_min == 188
    assert bb_raw.y_max == 202


def test_bear_to_xy_raw():
    bb = BearBox(math.radians(-50.0), math.radians(-40.0), 40, 42, 55)
    bb_raw = bb.to_xy_raw((512, 1657))

    assert bb_raw.x_min == 445
    assert bb_raw.x_max == 481
    assert bb_raw.y_min == 1205
    assert bb_raw.y_max == 1265


def test_expand_combine():
    a = XYZBox(0,0,0,10,10,10)
    b = XYZBox(12,12,12,20,20,20)

    a = bb_expand(a, (100,100,100), [5, 5, 5])
    c, d = combine_boxes([a, b])
    assert len(c) == 1
    c = c[0]
    assert c.x_min == 0
    assert c.y_min == 0
    assert c.x_max == 20
    assert c.y_max == 20

    a = XYZBox(0,0,0,10,10,10)
    b = XYZBox(0,0,20,10,10,40)

    a = bb_expand(a, (100,100,100), [2, 2, 2])
    c, d = combine_boxes([a, b])
    assert len(c) == 2
    c = c[0]
    assert c.x_min == 0
    assert c.y_min == 0
    assert c.x_max == 12
    assert c.y_max == 12



