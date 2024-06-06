#!/usr/bin/env python
"""
check.py - make sure images are available for the groups in the db.

Check over the hard-disks to make sure there are images available for the
groups held in the database and if not, report back.
"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from tqdm import tqdm
from sealhits.db.db import DB
from sealhits.db.dbschema import Groups


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal(s greatest) Hits - check",
        description="Check a harddisk has all it's images exported",
        epilog="SMRU St Andrews",
    )

    parser.add_argument("-s", "--sqlite", default="", help="The sqlite3 file we are checking (default: '')")

    parser.add_argument(
        "-f", "--fitspath", default=".", help="The path where the input FITS images are saved"
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

    # Generate a set of images of found data using the tracks as a 
    # bounding box
    # Assume we have ingested into the db
    seal_db = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass, host=args.dbhost)
    uids_to_check = []
    imgs_checked = 0
    imgs_per_group = []

    track_lengths = []

    if seal_db is not None:
        groups = []
        #required_fits = []

        if args.sqlite == "":
            # Look at all the groups
            groups = seal_db.get_groups()

        else:
            groups = seal_db.get_groups_filters([Groups.sqlite == args.sqlite, ])
            
        for group in tqdm(groups, desc="Checking Groups"):
            # Now go through all UIDs, get the group, it's images and create a video
            # TODO - eventually we'll ignore the sonarid

            group_images = seal_db.get_images_group(group.uid)
            imgs_per_group.append(len(group_images))

            if len(group_images) == 0:
                print("*** No Image Records found for group: " + str(group.uid) + " ***")

            else:
                # Sonar 854 check
                group_images = seal_db.get_images_group_sonarid(group.uid, 854)
                track_len = 0

                for img in group_images:
                    fname = img.filename
                    points = seal_db.get_image_points_by_filename_group(fname, group.uid)

                    if len(points) > 0:
                        track_len+=1

                track_lengths.append(track_len)

                # Sonar 853 check
                group_images = seal_db.get_images_group_sonarid(group.uid, 853)
                track_len = 0

                for img in group_images:
                    fname = img.filename
                    points = seal_db.get_image_points_by_filename_group(fname, group.uid)

                    if len(points) > 0:
                        track_len += 1

                track_lengths.append(track_len)
                

            # Below functions are all a bit too slow

            '''
            group = seal_db.get_group_uid(group.uid)
            print("Times", group.timestart, "->", group.timeend, ":", len(group_images))
            
            for img in group_images:
                fits_file = utils.fast_find(img.filename, args.fitspath) 
                if fits_file is None:
                    print("*** No FITS found for group: " + str(group.uid) + " ***")
                else:
                    imgs_checked += 1
                    required_fits.append(os.path.basename(fits_file))
            '''

        # Check to see if any images need removing
        '''required_fits.sort()
        all_fits = utils.find("*.lz4", args.fitspath)
        removals = []

        for fits in all_fits:
            if fits not in required_fits:
                removals.append(fits)

        print("Number of un-needed FITS files", len(removals))'''
            

    else:
        print("Cannot connect to the Database")

    print("Average track lengths", sum(track_lengths) / len(track_lengths))

    avg = sum(imgs_per_group) / len(imgs_per_group)
    print("Images Checked", imgs_checked, "Groups checked:", len(uids_to_check), "Avg Imgs per group", avg)


if __name__ == "__main__":
    main()