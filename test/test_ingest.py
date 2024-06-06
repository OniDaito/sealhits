'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_ingest.py - create videos from a numpy array.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Tests for ingesting data.
'''

from ingest import find_group_objects, tracks_to_pgdfs
import os
import shutil
import pytest

from sqlalchemy import text

from sqlalchemy.orm import (
    Session,
)
from sealhits.sources import sqlpam
from sealhits.sources.glf import process_glfs
from sealhits.sources.pgdf import process_pgdfs
from sealhits.sources.group import split_groups, fix_group_times
from sealhits.db.dbschema import Groups


@pytest.mark.integtest
def test_ingest(get_data):
    """Test the ingest of a number of small groups, comparing against the loaded database."""
    datapath, db, db_blank = get_data
    sqlname =  "testseals.sqlite3"
    sqldb_path = os.path.join(datapath, sqlname)
    sqldb = sqlpam.SQLPAM(sqldb_path)

    # We MUST use a try finally block, with db.engine.dispose to make sure all connections
    # are terminated before the test fixture attempts to remove the databases and dispose
    # of everything.
    try:
        with Session(db_blank.engine) as session:
            new_groups, new_tracks = find_group_objects(session, sqldb, sqlname, sqlname)
            assert len(new_groups) == 3

            pgdfs_needed = tracks_to_pgdfs(new_tracks)
            new_pgdfs, new_points = process_pgdfs(
                session, datapath, pgdfs_needed, new_groups, new_tracks
            )

            for p in new_points:
                found = False

                for group in new_groups:
                    assert(p.group_id is not None)
                    if p.group_id == group.uid:
                        found = True
                        break
                assert(found)

            assert(len(new_pgdfs) == 3)

            fixed_groups = fix_group_times(new_groups, new_points)
            sgroups, spoints = split_groups(session, fixed_groups, new_points)

            assert(len(sgroups) > len(fixed_groups))
            sgroups_uids = [g.uid for g in sgroups]

            flag = True
    
            # using naive method
            # Make sure all split groups are unique
            for i in range(len(sgroups_uids)):
                for i1 in range(len(sgroups_uids)):
                    if i != i1:
                        if sgroups_uids[i] == sgroups_uids[i1]:
                            flag = False
            assert(flag)

            for p in spoints:
          
                found = False
                for group in sgroups:
                    assert(p.group_id is not None)
                    if p.group_id == group.uid:
                        found = True
                        break
                assert(found)

            assert len(sgroups) == 7

            for group in sgroups:  # Updated groups post split
                session.add(group)

            for track in new_tracks:
                session.add(track)

            for pgdf in new_pgdfs:
                session.add(pgdf)

            for point in spoints:  # Updated points post split
                session.add(point)

            assert len(new_groups[0].pgdfs) > 0

            # Now do the GLFS too!
            glfpath = os.path.join(datapath, "glfs")
            outpath = os.path.join(datapath, "genfits")

            if not os.path.exists(outpath):
                os.mkdir(outpath)

            tgroups = session.query(Groups).order_by(Groups.gid.asc()).all()
            new_glfs, new_images = process_glfs(session, tgroups, glfpath, outpath, 800)

            assert len(new_glfs) == 4

            for glf in new_glfs:
                session.add(glf)

            for img in new_images:
                session.add(img)

            session.commit()

        assert len(db_blank.get_tracks_groups()) > 0
        assert len(db_blank.get_pgdfs_distinct()) > 0

        with db_blank.engine.connect() as con:
            result = con.execute(
                text(
                    "select count(*) from points;"
                )
            )

            for r in result:
                assert int(r[0]) > 0

        with db_blank.engine.connect() as con:
            result = con.execute(text("select count(*) from groups_pgdfs;"))
           
            for r in result:
                assert int(r[0]) > 0

        # Check that the image files exist for all the image records attached to the groups
        with db_blank.engine.connect() as con:
            result = con.execute(
                text(
                    "select im.filename, g.huid from images im inner join groups_images gi on gi.image_id = im.uid inner join groups g on g.uid = gi.group_id"
                )
            )

            for r in result:
                fits_filename = r[0] + ".lz4" # Add on for the compression
                assert(os.path.exists(os.path.join(os.path.join(datapath, "genfits/2023_05_29"), fits_filename))
                       or os.path.exists(os.path.join(os.path.join(datapath, "genfits/2023_05_28"), fits_filename)))
                
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()

        # Remove the generated FITS. A bit wasteful but correct
        if os.path.exists(os.path.join(datapath, "genfits")):
            shutil.rmtree(os.path.join(datapath, "genfits"))

