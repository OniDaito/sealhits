'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_delete.py - test database delete functions.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Tests for deleting data from the DB.

This works by creating a model before the import and 
a second one after. Any objects missing from the second
model are deleted.
'''

from ingest import find_group_objects, tracks_to_pgdfs
import os
import pytest
import shutil
from sqlalchemy import text

from sqlalchemy.orm import (
    Session,
)
from sealhits.sources import sqlpam
from sealhits.sources.glf import process_glfs
from sealhits.sources.pgdf import process_pgdfs
from sealhits.sources.group import split_groups, fix_group_times
from sealhits.db.dbmodel import gen_model, DBModel, diff_models
from sealhits.utils import create_dir


@pytest.mark.integtest
def test_delete(get_data):
    """Test loading the DB then loading it again"""
    datapath, db, db_blank = get_data
    sqldb_path = os.path.join(datapath, "testseals_small.sqlite3")

    # We MUST use a try finally block, with db.engine.dispose to make sure all connections
    # are terminated before the test fixture attempts to remove the databases and dispose
    # of everything.
    try:
        # Get the initial relationships
        initial_links = 0
        with db.engine.connect() as con:
            result = con.execute(text("select count(*) from groups_pgdfs;"))

            for r in result:
                initial_links = int(r[0])

        with Session(db.engine) as session:
            # Grab the current model. Although we are reading from testseals_small.sqlite3
            # we set the name to testseals.sqlite3 to simulate a change in the data.
            sqlname = "testseals.sqlite3"

            model_a = gen_model(session, sqlname)
            model_b = DBModel()
            sqldb = sqlpam.SQLPAM(sqldb_path)

            new_groups, new_tracks = find_group_objects(session, sqldb, sqlname, sqlname)
            # One fewer group than before
            assert(len(new_groups) == 2)
            model_b.track_groups = new_tracks
            assert(len(new_tracks) == 6)
            pgdfs_needed = tracks_to_pgdfs(new_tracks)
            assert(len(pgdfs_needed) == 2)

            new_pgdfs, new_points = process_pgdfs(
                session, datapath, pgdfs_needed, new_groups, new_tracks
            )
            model_b.pgdfs = new_pgdfs
            fixed_groups = fix_group_times(new_groups, new_points)

            gids = [g.uid for g in fixed_groups]
            pids = []
            
            for p in new_points:
                if p.group_id not in pids:
                    pids.append(p.group_id)

            for g in gids:
                assert(g in pids)

            sgroups, spoints = split_groups(session, fixed_groups, new_points)
            model_b.groups = sgroups
            model_b.points = spoints

            for group in sgroups:
                session.add(group)

            for track in new_tracks:
                session.add(track)

            for pgdf in new_pgdfs:
                session.add(pgdf)

            for point in spoints:
                session.add(point)

            # TODO ADD THE IMAGES AND GLFS!
            # Look at the GLF ingest unless we are skipping it.
            create_dir(os.path.join(datapath, "genfits"))

            new_glfs, new_images = process_glfs(
                session,
                sgroups,
                os.path.join(datapath, "glfs"),
                os.path.join(datapath, "genfits"),
                800,
            )

            model_b.glfs = new_glfs
            model_b.images = new_images

            for glf in new_glfs:
                session.merge(glf)

            for image in new_images:
                session.merge(image)

            session.commit()

            diff_model = diff_models(session, model_a, model_b)
            assert len(diff_model.groups) == 2
            assert len(diff_model.points) == 138
            assert len(diff_model.pgdfs) == 1
            assert len(diff_model.glfs) == 0

            assert("give-hard-social-idea" in [x.huid for x in diff_model.groups])

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

        # Make sure the connecting parts of the model are deleted too
        with db.engine.connect() as con:
            result = con.execute(text("select count(*) from groups_pgdfs;"))

            for r in result:
                assert int(r[0]) < initial_links

            result = con.execute(text("select count(*) from groups;"))

            for r in result:
                assert int(r[0]) == 5 

    finally:
        db.engine.dispose()
        db_blank.engine.dispose()

        # Remove the generated FITS. A bit wasteful but correct
        if os.path.exists(os.path.join(datapath, "genfits")):
            shutil.rmtree(os.path.join(datapath, "genfits"))