#!/usr/bin/env python
"""
glf_to_png.py - create png files from a GLF.

Given a GLF file, spit out all the PNGs as fans, with a possible
limit.
"""

from __future__ import annotations

import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from datetime import datetime
from pytritech.glf import GLF
from sealhits.image import fan_distort
from sealhits.btable import bearing_table

def main(args):
    """ Open up the GLF and spit out the Fan PNGs up to limit."""
    with GLF(args.glf) as g:
        i = 0
        limit = args.limit
        if limit == -1:
            limit = len(g.images)

        img_recs = []

        # Time range supercedes limit (for now - starttime on it's own might be fine)
        if args.fromtime != "" and args.totime != "":
            start_date = datetime.strptime(args.fromtime, "%d/%m/%Y-%H:%M:%S")
            end_date = datetime.strptime(args.totime, "%d/%m/%Y-%H:%M:%S")
            
            for img_rec in g.images:
                if img_rec.db_tx_time >= start_date and  img_rec.db_tx_time < end_date and img_rec.header.device_id == args.sonarid:
                    img_recs.append(img_rec)
        else:
            for img_rec in g.images:
                if img_rec.header.device_id == args.sonarid:
                    img_recs.append(img_rec)
       
        for i, img in tqdm(enumerate(img_recs)):
                glf_img_data, glf_img_size = g.extract_image(img)
                image_np = np.frombuffer(glf_img_data, dtype=np.uint8).reshape((glf_img_size[1], glf_img_size[0]))
                fan_img = np.fliplr(np.flipud(fan_distort(image_np, args.height, bearing_table))).astype(np.uint8)
                pil_img = Image.fromarray(fan_img)
                png_name = os.path.basename(args.glf)
                png_num = "{:05d}".format(i)
                png_name = args.outpath + "/" + png_name.replace(".glf","") + "_" + str(png_num) + ".png"
                pil_img.save(png_name)
            

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal(s greatest) Hits - GLF to png",
        description="Convert a GLF file to a png.",
        epilog="SMRU St Andrews",
    )

    parser.add_argument(
        "-o", "--outpath", default=".", help="The path where the output images are saved"
    )
    parser.add_argument(
        "-g", "--glf", default=".", help="The glf in question"
    )
    parser.add_argument(
        "-r", "--sonarid", type=int, default=854, help="Which Sonar are we looking at (default: 854)?"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=-1, help="How many pngs to output (default: -1 or all)?"
    )
    parser.add_argument(
        "-y", "--height", type=int, default=400, help="The height of the fans (default: 400)?"
    )
    parser.add_argument(
         "-f", "--fromtime", type=str, default="", help="An optional start time(default: "")?"
    )

    parser.add_argument(
         "-t", "--totime", type=str, default="", help="An optional end time(default: "")?"
    )
  
    args = parser.parse_args()

    main(args)