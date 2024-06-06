#!/usr/bin/env python
"""
video.py - generate a video from an ingested group.

Create a video for a particular group. Uses ffmpegio and ffmpeg.
Example usage:
    python video.py -n 10.9.9.15 -i /mnt/work/sealhits/fits -r 853 -d sealhits \
        -o ~/tmp -c /mnt/work/sealhits/fan_cache 05c82a5c-713d-47b4-a206-84ae2c77057e
"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import sys
import os
import pytz
import numpy as np
from datetime import datetime
from tqdm import tqdm
from sealhits import image, utils
from sealhits.db.db import DB
from pytritech.glftimes import glf_times
from pytritech.glf import GLF
from sealhits.btable import bearing_table
from sealhits.sources.files import glf_files_avail
from sealhits.video import gen_video
from sealhits.cache import is_cached_fan
from sealhits.bbox import points_to_bb, XYBox, bb_to_fix


def check_cache(cache_path, fname, fresult, fan_size):
    """ Function that checks the cache for the fan image,
    generates the fan image if it doesn't exist and returns the
    result. We also check the size of the image in the cache and
    if it doesn't match we regenerate it."""
    # Start with the sonar image
    # Check the cache first for a fan
    cpath = None
    
    if cache_path != "":
        cpath = is_cached_fan(cache_path, fname)
    
    fan_image = None

    if cpath is not None:
        try:
            fan_image, _ = image.fits_to_np(cpath)

            if fan_image.shape[0] != fan_size[1] or fan_image.shape[1] != fan_size[0]:
                fan_image = None
        except Exception as e:
            print("Problem with corrupt FITS in cache:", cpath)
            print(e)

    if cpath is None or fan_image is None:
        # For some reason, we need flip up down and left right!
        data, _ = image.fits_to_np(fresult)
        fan_image = np.fliplr(np.flipud(image.fan_distort(data, fan_size[1], bearing_table)))
        
        # Save to cache if cache is being used
        # Cancelled for now as we don't want to overwrite nice caches made by other programs
        # just yet.
        #if args.cache != "":
        #    np_fan_to_cache(args.cache, fname, fan_image)

    return fan_image


def group_to_video(args):
      # Generate a set of images of found data using the tracks as a 
    # bounding box
    # Assume we have ingested into the db
    seal_db = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass, host=args.dbhost)

    # Bits we need to generate text for the video
    gid = ""
    uid = ""
    time_start = None
    time_end = None
    gcode = ""
    comment = ""
    fan_size = utils.get_fan_size(args.height)

    if seal_db is not None:
        uids_to_check = []
        
        if "ALL" == args.id:
            groups = seal_db.get_groups()
            
            for group in groups:
                uids_to_check.append(group.uid)
        
        else:
            uids_to_check.append(args.id)

        # Now go through all UIDs, get the group, it's images and create a video
        for uid in uids_to_check:
            bbs = []
            group_images = seal_db.get_images_group_sonarid(uid, args.sonarid)
            group_details = seal_db.get_group_id(uid)
            
            if len(group_images) <= 0:
                print("No frames found.")
                sys.exit()

            np_frames = np.zeros((len(group_images), fan_size[1], fan_size[0]), dtype=np.uint8)

            if group_images is not None:
                # Set the group details for writing out into the video
                time_start = group_details.timestart
                time_end = group_details.timeend
                gcode = group_details.code
                comment = group_details.comment
                gid = group_details.gid

                # Find all the images and create the base frames.
                for idx, img in enumerate(tqdm(group_images, desc="Create Base Frames")):
                    fname = img.filename
                    fresult = utils.fast_find(fname, args.inpath)
            
                    if fresult is not None:
                        fan_image = check_cache(args.cache, fname, fresult, fan_size)
                        print("Using Frame:", fname, img.uid, " Has original Track:", img.hastrack, "Range:", img.range)

                        # Resizing doesn't work sadly, as it distorts the images too much and the
                        # bounding boxes don't match                     
                        assert(fan_size[0] == fan_image.shape[1])
                        assert(fan_size[1] == fan_image.shape[0])
                     
                        np_frames[idx] = fan_image

                        # Find the Bounding boxes for each frame, if we have any.
                        # BBS need flipping just like the images, but only vertically
                        if args.draw_bboxes:
                            fname = img.filename
                            points = seal_db.get_image_points_by_filename_group(fname, uid)

                            if len(points) > 0: # Since we have buffer start / end images and intermediates, 0 tracks are possible
                                bb = points_to_bb(points, img.range)
                                print(bb, img.range)
                                bbox = bb.to_xy(fan_size)
                                ((xmin, ymin), (xmax, ymax)) = bbox.pair()
                                # Flip BBS
                                bbs.append((idx, XYBox(xmin, fan_size[1] - ymax, xmax, fan_size[1] - ymin)))

            # Clean the track if selected
            bbs_final = []

            if args.fix_size:
                for (f, bb) in bbs:
                    ebb = bb_to_fix(bb, (args.fix_size, args.fix_size), fan_size)
                    bbs_final.append((f, ebb))
            else:
                bbs_final = bbs

            # Add colour to bbs
            bbs_final = [(f, b, "#ff0000") for (f, b) in bbs_final]

            gen_video(np_frames, bbs_final, 
                      str(uid) + "\n" + str(gid) + "\n" + str(time_start) + "\n" + str(time_end) + "\n" + str(gcode) + "\n" + str(comment), args.outpath)


def glf_to_video(args):
    """ Given a list of GLFs and a timerange, generate video from that."""

    glf_files = glf_files_avail(args.glfpath)
    glf_files.sort()
    assert(len(glf_files) > 0)
    fan_size = utils.get_fan_size(args.height)
    frames = []
    rate = 4
    
    try:
        start_time = datetime.strptime(args.starttime, "%Y-%m-%d %H:%M:%S.%f").replace(tz=pytz.UTC)
        end_time = datetime.strptime(args.endtime, "%Y-%m-%d %H:%M:%S.%f").replace(tz=pytz.UTC)
    
        for gf in glf_files:
            try:
                gstart, gend = glf_times(gf)

                if end_time >= gstart and start_time <= gend:
                    with GLF(gf) as f:
                        
                        for image_rec in f.images:
                            if image_rec.header.time >= start_time and image_rec.header.time < end_time:
                                image_data, image_size = f.extract_image(image_rec)
                                np_frame = np.frombuffer(image_data, dtype=np.uint8).reshape((image_size[1], image_size[0]))
                                fan_image = np.fliplr(np.flipud(image.fan_distort(np_frame, fan_size[1], bearing_table)))
                                frames.append(fan_image)
            
            except Exception as e:
                print("Could not read GLF", gf)
                print(e)

        np_frames = np.array(frames)
        td = end_time - start_time
        rate = int(len(frames) / td.seconds)
        print("Frame Rate:", rate)
        assert(len(frames) > 0)
        gen_video(np_frames, None, str(start_time) + "\n" + str(end_time), args.outpath, rate=rate)

    except ValueError as e:
        print("Failed to parse start and end times from arguments.")
        print(e)
        return


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal(s greatest) Hits - Video",
        description="Create a video for a particular group",
        epilog="SMRU St Andrews",
    )

    parser.add_argument("id", help="The Group ID to generate a video for, or ALL for all groups. ID is either a UID or a HUID.")

    parser.add_argument(
        "-o", "--outpath", default=".", help="The path where the output images are saved"
    )
    parser.add_argument(
        "-c", "--cache", default="", help="An optional path to existing fan images of the correct size."
    )
    parser.add_argument(
        "-i", "--inpath", default=".", help="The path where the input FITS images are saved"
    )
    parser.add_argument(
        "-s", "--starttime", default="", help="(optional) Start Date Time in YYYY-mm-dd HH:MM:SS.f UTC (default: none)"
    )
    parser.add_argument(
        "-e", "--endtime", default="",  help="(optional) End Date Time in YYYY-mm-dd HH:MM:SS.f UTC (default: none)"
    )
    parser.add_argument(
        "-r", "--sonarid", type=int, default=854, help="Which Sonar are we looking at (default: 854)?"
    )
    parser.add_argument(
        "-y", "--height", type=int, default=400, help="The fansize height (default: 400)?"
    )
    parser.add_argument("-b", "--draw-bboxes", action="store_true", default=False)
    parser.add_argument("-g", "--glfpath", default="", help="Rather than use a group, use glfs on this path (default: none)")

    parser.add_argument(
        "-f",
        "--fix-size",
        type=int,
        default=0,
        help="Use a square of fixed size instead of a calculated bounded box (default: 0).",
    )   
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

    if args.glfpath != "" and os.path.exists(args.glfpath):
        glf_to_video(args)
    else:
        group_to_video(args)

if __name__ == "__main__":
    main()
