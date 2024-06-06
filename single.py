#!/usr/bin/env python
"""
single.py - extract an image with a track, group number and bounding box.

Extract an image and any associated tracks, complete with their
group numbers and bounding boxes.

Example usage:

    python single.py -o ~/tmp -i /mnt/work/fits -r 1637 -d riverseals -n 10.9.9.15 
"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import os
import sys
import uuid
import numpy as np
from PIL import Image
from sealhits.db.db import DB
from sealhits.image import draw_bb, draw_text, fan_distort, fits_to_np
from sealhits.btable import bearing_table
from sealhits.bbox import points_to_bb
from sealhits.utils import get_fan_size, fast_find


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal(s greatest) Hits - Single Image",
        description="Create a single from our ingested database",
        epilog="SMRU St Andrews",
    )

    parser.add_argument("image_uid")

    parser.add_argument(
        "-o", "--outpath", default=".", help="The path where the output images are saved"
    )
    parser.add_argument(
        "-i", "--inpath", default=".", help="The path where the input FITS images are saved"
    )
    parser.add_argument(
        "-y", "--height", type=int, default=400, help="The fansize height (default: 400)?"
    )
    parser.add_argument("-t", "--draw-tracks", action="store_true", default=False)

    parser.add_argument(
        "-d", "--dbname", default="sealhits", help="The name of the postgresql database (default: sealhits)"
    )
    parser.add_argument(
        "-u", "--dbuser", default="sealhits", help="The username for the postgresql database (default: sealhits)"
    )
    parser.add_argument(
        "-w", "--dbpass", default="kissfromarose", help="The password for the postgresql database (default: kissfromarose)"
    )
    parser.add_argument(
        "-n", "--dbhost", default="localhost", help="The hostname for the postgresql database (default: localhost)"
    )

    args = parser.parse_args()

    # Generate a set of images of found data using the tracks as a 
    # bounding box
    # Assume we have ingested into the db
    seal_db = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass, host=args.dbhost)
    colours = ["#11ff11", "#1111ff", "#33ff11", "#3333ff"]
    
    image_uid = uuid.UUID(args.image_uid)
    print("Using Image UID:", image_uid)

    # Generate a set of images of found data using the tracks as a
    # bounding box
    # Assume we have ingested into the db

    if seal_db is None:
        print("Error accessing PostgreSQL Database.")
        sys.exit(1)


    colours = ["#11ff11", "#1111ff", "#33ff11", "#3333ff"]
    fan_size = get_fan_size(args.height)
    img = seal_db.get_image_uid(image_uid)
    fname = img.filename
    ftime = img.time
    result = fast_find(fname, args.inpath)

    # Create the fan image and write it out as a png
    if result is not None:
        data, _ = fits_to_np(result)
        fan_image = fan_distort(data, args.height, bearing_table)
        out_image  = Image.fromarray(fan_image.astype(np.uint8))
        fpath = os.path.join(args.outpath, os.path.splitext(fname)[0] + '.png')
        print_buffer = []
        cidx = 0

        if args.draw_tracks:
            groups = seal_db.get_image_groups_by_filename(fname)

            for grp in groups:
                points = seal_db.get_image_points_by_filename_group(fname, grp.uid)
                bb = points_to_bb(points, img.range)

                #for point in points:
                #   draw_point(out_image, point, img.range, colours[cidx % 4])

                draw_bb(out_image, bb, "#ff1111")

            out_image = out_image.transpose(Image.FLIP_TOP_BOTTOM)

            for grp in groups:
                pos = bb.to_xy(fan_size)
                draw_text(out_image, (pos.x_min,  args.height - pos.y_min), "#ff1111", str(grp.gid))

        out_image.save(fpath)
