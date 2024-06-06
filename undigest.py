#!/usr/bin/env python
"""
undigest.py - remove a hard-disk's worth of data.

Delete an ingest. The opposite of ingest. It works off the sqlite filename.
"""

from __future__ import annotations

__all__ = []
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from sealhits.db.db import DB


def undigest(args): 
    """Delete an ingest using the sqliteid."""
    pgdb = DB(db_name=args.dbname, username=args.dbuser, password=args.dbpass)
    pgdb.del_by_sqlite(args.sqlite)


def main():
    """Parse the command line arguments and begin the major steps in ingesting
    the data from the various sources."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal Hits - deingest",
        description="Remove a database from the ingest.",
        epilog="SMRU St Andrews",
    )

    parser.add_argument("-s", "--sqlite", help="The name of the SQLITE file that we are deleting.")
   
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
    undigest(args)


if __name__ == "__main__":
    main()


