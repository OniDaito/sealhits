'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_db.py - test the database functions.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Tests for the DB - the postgresql. Requires a database to test against
installed on the local machine.
'''

import uuid
import datetime
import pytest


@pytest.mark.integtest
def test_db_basic(get_data):
    try:
        datapath, db, db_blank = get_data
        groups = db.get_groups()
        assert(len(groups) == 7)

        timestart = groups[0].timestart
        newtime = timestart + datetime.timedelta(seconds=10)
        db.set_group_timestart(groups[0].uid, newtime)
        cgroup = db.get_group_uid(groups[0].uid)
        assert(cgroup.timestart == newtime)
        db.set_group_timestart(groups[0].uid, timestart)
        cgroup = db.get_group_uid(groups[0].uid)
        assert(cgroup.timestart == timestart)

        timeend = groups[0].timeend
        newtime = timeend + datetime.timedelta(seconds=10)
        db.set_group_timeend(groups[0].uid, newtime)
        cgroup = db.get_group_uid(groups[0].uid)
        assert(cgroup.timeend == newtime)
        db.set_group_timeend(groups[0].uid, timeend)
        cgroup = db.get_group_uid(groups[0].uid)
        assert(cgroup.timeend == timeend)

        groups = db.get_groups(code="seal")
        assert(len(groups) == 6)
    
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()


@pytest.mark.integtest
def test_get_points(get_data):
    try:
        datapath, db, db_blank = get_data
        groups = db.get_groups()
        points = db.get_points_group(groups[0].uid)
        assert(len(points) > 0)
    
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()


@pytest.mark.integtest
def test_db_pgdf(get_data):
    try:
        datapath, db, db_blank = get_data
        pgdfs = db.get_pgdfs()
        assert(len(pgdfs) == 3)

        pgdfs = db.get_pgdfs(limit=1)
        assert(len(pgdfs) == 1)
    
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()


@pytest.mark.integtest
def test_db_sonar(get_data):
    try:
        datapath, db, db_blank = get_data
        images = db.get_images_group_sonarid(uuid.UUID('23ff1ea4-865e-4889-bef1-9086450f1698'), 854)

        # For sonar 854, there are no tracks for this group.
        for image in images:
            assert(image.hastrack is False)
    
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()