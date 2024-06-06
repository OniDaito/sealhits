#!/usr/bin/env python
"""
ingest.py - import a hard-disk's worth of data.

Ingest an SQLITE database and it's associated hard-disk.

This later version uses an ORM based approach. We start by building
up the Groups objects, then all the objects that hang off them.

Once we have each group object and it's associated parts, we check
them against the existing DB to see if they already exist and need
some sort of update.

UIDs need to be generated on the Python side, instead of the postgresql
side as we create everything in memory first, before hitting the DB with
a proper transaction.

Assumptions being made:
    - Groups do not cross multiple PGDFs.
    - Each PGDF contains unique track_ids - no duplicates.
    - Assume that no track or group crosses a PGDF boundary.
    - That gaps within groups longer than 'buffer' will cause the group to be split
"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import os
import logging
import traceback
from sealhits.db.db import DB
from sealhits.db.dbmodel import DBModel, diff_models, gen_model
from sealhits.db.dbschema import Groups
from sealhits.sources import sqlpam
from sqlalchemy.orm import Session
from sealhits.sources.glf import process_glfs
from sealhits.sources.group import find_group_objects, fix_group_times, split_groups
from sealhits.sources.pgdf import process_pgdfs, tracks_to_pgdfs
from sealhits.utils import create_dir


def main(args):
    """The main function that build the objects and either creates new objects,
    or adds to the database.

    The order of operations is as follows:
        1) Read the sqlite to get hold of the Groups and the TrackGroups that make up the groups.
        2) Find the PGDFs required for these groups and extract the points that makeup the tracks.
        3) Fix the times on the groups (by looking at the start and end points).
        4) Split the groups based on a buffer time.
        5) Create a DB Model of the existing database for this SQLITE file only.
        6) Insert or merge the new groups, trackgroups, points and pgdfs.
        7) Find the GLFs we need for each group. Extract the images and save to disk. Create Image
            objects and attach them to the groups.
        8) Insert or merge the GLF and Image objects, updating existing groups.
        9) Compare the new model against the older model, deleting anything that doesn't appear in
            the new model.
    """
    pgdb = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass)

    # Do everything as one big session / transaction
    # TODO - we should break up this into update add, per group item
  
    with Session(pgdb.engine) as session:
        try:
            # These lines are the main processes for dealing with all the
            # different files an ingest might have. At the end will be the
            # correct model structure for this ingest.
            session.begin()

            # Generate the existing model for this sqlite file.
            # We need to see if we are using an alias for the SQLITE file.
            # A previous model might have used a different name for the sqlite file
            # from the new one we are reading in. args.sql_alias holds this name. If
            # it is not empty, we use that alias to generate the model to check
            # against and pass it to find_group_objects.
            sqldbname = os.path.basename(args.sqldb)
            sqlmodelname = sqldbname
            sqlalias = sqldbname
            
            if args.sql_alias != "":
                sqlalias = args.sql_alias
                sqlmodelname = sqlalias
                
            model_a = gen_model(session, sqlmodelname)
            sqldb = sqlpam.SQLPAM(args.sqldb)
          
            new_groups, new_tracks = find_group_objects(session, sqldb, sqldbname, sqlalias, args.max_secs)
           
            pgdfs_needed = tracks_to_pgdfs(new_tracks)
            assert(len(pgdfs_needed) >  0)
            assert(len(new_groups) >  0)

            # Assuming all the required PGDFs exist on this path!
            new_pgdfs, new_points = process_pgdfs(
                session, args.pgdf, pgdfs_needed, new_groups, new_tracks
            )

            assert(len(new_pgdfs) >  0)
            assert(len(new_points) >  0)

            fixed_groups = fix_group_times(new_groups, new_points)

            sgroups, spoints = split_groups(
                session, fixed_groups, new_points, args.buffer
            )

            # Record the new model for deletion purposes
            model_b = DBModel()
            model_b.groups = sgroups
            model_b.pgdfs = new_pgdfs
            model_b.points = spoints
            model_b.track_groups = new_tracks

            # TODO - at this point we may have orphans due to, say, removal of tracks from
            # one group and additions of new tracks, so check over the relations
            # We add these to the session as we need to refer to these objects in the
            # GLF Image creation.

            # We are performing merge manually due to the nature of how primary keys are
            # randomly generated each ingest.
            for group in sgroups:
                session.merge(group)

            for track in new_tracks:
                session.merge(track)
               
            for pgdf in new_pgdfs:
                session.merge(pgdf)

            for point in spoints:
                session.merge(point)

            # Look at the GLF ingest unless we are skipping it.
            if not args.skip_glfs:
                logging.info("Reading GLFS...")
                create_dir(args.outpath)

                # Loaded the groups again before looking at GLFS
                # This is a test and I'm not sure if it solves the
                # two part issue but worth a shot.
                groups = []

                with session.no_autoflush:
                    q = session.query(Groups).filter(
                        Groups.sqliteid == sqldbname,
                    )

                groups = q.all()

                new_glfs, new_images = process_glfs(
                    session, groups, args.glf, args.outpath, args.max_glf
                )

                model_b.glfs = new_glfs
                model_b.images = new_images

                for glf in new_glfs:
                    session.merge(glf)

                for image in new_images:
                    session.merge(image)

            # Now perform the deletion side of the operation
            logging.info("Performing model diff...")
            diff_model = diff_models(session, model_a, model_b)

            # Perform the deletion then check it
            for group in diff_model.groups:
                session.delete(group)

            for track in diff_model.track_groups:
                session.delete(track)

            for pgdf in diff_model.pgdfs:
                session.delete(pgdf)

            for point in diff_model.points:
                session.delete(point)

            for glf in diff_model.glfs:
                session.delete(glf)

            for image in diff_model.images:
                session.delete(image)

            session.commit()

        except Exception as e:
            print(e)
            print(traceback.format_exc())
    
            for track in new_tracks:
                found = False
            
                for group in sgroups:
                    if track.group_id == group.uid:
                        found = True

                if not found:
                    print("Track refers to a group that doesn't exist", track)
    
            session.rollback()


if __name__ == "__main__":
    """Parse the command line arguments and begin the major steps in ingesting
    the data from the various sources."""
    import argparse

    # Try and see why this program halts occasionally
    # https://stackoverflow.com/questions/3443607/how-can-i-tell-where-my-python-script-is-hanging
    # Use with kill -s SIGUSR1 <pid>
    import faulthandler
    import signal
    import sys

    format = "%(asctime)s - %(levelname)s : %(message)s"
    logging.basicConfig(
        filename="ingest.log",
        format=format,
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter = logging.Formatter(format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    faulthandler.register(signal.SIGUSR1.value)

    parser = argparse.ArgumentParser(
        prog="Seal Hits - Ingest",
        description="Create a database and FITS files from a number of PAMGuard files",
        epilog="SMRU St Andrews",
    )
    parser.add_argument("-s", "--sqldb", help="The path to the SQLite File")
    parser.add_argument(
        "--sql-alias",
        default="",
        help="The alias to use for the SQLITE3 file when performing updates (default: none).",
    )
    parser.add_argument(
        "-q",
        "--override",
        action="store_true",
        help="Assume that the groups in the SQLite file haven't been added already",
    )
    parser.add_argument(
        "-v",
        "--skip-glfs",
        action="store_true",
        default=False,
        help="Skip processing the GLFs (default: False)",
    )
    parser.add_argument(
        "-p", "--pgdf", help="The path to the folder containing PGDF Files"
    )
    parser.add_argument(
        "-g", "--glf", help="The path to the folder containing GLF Files"
    )
    parser.add_argument(
        "-b",
        "--buffer",
        type=int,
        default=4,
        help="How many seconds of buffer (default: 4)?",
    )
    parser.add_argument(
        "-x",
        "--max-secs",
        type=int,
        default=800,
        help="Maximum number of seconds to ingest for a group (default: 800)?",
    )
    parser.add_argument(
        "-o", "--outpath", default=".", help="The path where the FITS images are saved"
    )
    parser.add_argument(
        "-d",
        "--dbname",
        default="sealhits",
        help="The name of the postgresql database (default: sealhits)",
    )
    parser.add_argument(
        "-u",
        "--dbuser",
        default="sealhits",
        help="The username for the postgresql database (default: sealhits)",
    )
    parser.add_argument(
        "-w",
        "--dbpass",
        default="kissfromarose",
        help="The password for the postgresql database (default: kissfromarose)",
    )
    parser.add_argument(
        "-t",
        "--dbhost",
        default="localhost",
        help="The location of the postgresql database (default: localhost)",
    )

    args = parser.parse_args()

    main(args)
