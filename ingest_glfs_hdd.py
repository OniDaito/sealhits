"""
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

ingest_glfs_hdd.py - ingest just the FITS images from GLFS.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

If all the groups, pgdfs, points etc have all been ingested, just do the
GLFs for a particular hdd.

"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import logging
from sealhits.db.db import DB
from sealhits.db.dbschema import Groups
from sealhits.sources.glf import process_glfs
from sqlalchemy.orm import Session
from sealhits.utils import create_dir


def main():
    """Assume that all the groups, PGDFs, points and such are in place. Now just get
    all the groups from a particular hard-drive and save out the images."""
    import argparse
    import sys

    # Setup some logging
    format = "%(asctime)s - %(levelname)s : %(message)s"
    logging.basicConfig(
        filename="ingest_glf.log", format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
    )
    formatter = logging.Formatter(format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    parser = argparse.ArgumentParser(
        prog="Seal Hits",
        description="Create a database from a number of PAMGuard files",
        epilog="SMRU St Andrews",
    )

    parser.add_argument("-i", "--glf", help="The path to where the GLFs are stored")

    parser.add_argument(
        "-a",
        "--sqlite",
        help="The name of the sqlite file (and therefore harddisk) to process. Note this is not the path to a file but the name of the file in the db.",
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
    parser.add_argument(
        "-o", "--outpath", default=".", help="The path where the FITS images are saved"
    )
    parser.add_argument(
        "-x",
        "--max-glf",
        type=int,
        default=800,
        help="Maximum number of seconds to ingest for a group (default: 800)?",
    )

    args = parser.parse_args()

    import resource
    import sys
    import faulthandler

    resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))
    sys.setrecursionlimit(10**6)
    faulthandler.enable()

    pgdb = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass)

    try:
        with Session(pgdb.engine) as session:
            session.begin()
            logging.info("Reading GLFS...")
            create_dir(args.outpath)
            groups = session.query(Groups).filter(Groups.sqlite==args.sqlite).order_by(Groups.gid.asc()).all()
            logging.info("Number of groups: %d", len(groups))
           
            new_glfs, new_images = process_glfs(
                    session, groups, args.glf, args.outpath, args.max_glf
            )

            # Update groups as images are attached to groups
            for group in groups:
                session.merge(group)

            for glf in new_glfs:
                session.merge(glf)

            for img in new_images:
                session.merge(img)

            session.commit()

    except Exception as e:
        print(e)
        session.rollback()


if __name__ == "__main__":
    main()
