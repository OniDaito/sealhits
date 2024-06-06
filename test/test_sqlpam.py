"""
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_sqlpam.py - test sqlite files.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Tests for the SQLPAM - the sqlite files asssociated with the 
tritech track detector program."""

import pytest
from sealhits.sources.sqlpam import SQLPAM 
import os

@pytest.mark.integtest
def test_sqlpam(get_data):
    datapath, db, db_blank = get_data
    try:
        sqlitepath = os.path.join(datapath, "testseals.sqlite3")
        assert os.path.exists(sqlitepath)
        sqlpam = SQLPAM(sqlitepath)
        assert(len(sqlpam.track_groups) == 3)
        assert(len(sqlpam.track_children) == 11)
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()
