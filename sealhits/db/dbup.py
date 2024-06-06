"""
dbupdate.py - The Postgresql update functions.

The Postgresql Database update functions.
Updating the objects that may already exist.
"""

from __future__ import annotations

__all__ = [
    "update_group",
]

__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


from sqlalchemy.orm import (
    Session,
)
from sqlalchemy import select

from sealhits.db.dbschema import (
    Groups,
)

def update_group(self, new_group: Groups):
    """ Update a single group. UID is the main key ingredient. 
    We ignore foreign keys for now however. This function only updates the local group.
    
    Args:
        new_group (Groups): the new Groups data. We update based on the uid.
    """
    with Session(self.engine) as session:
        exist_group = session.execute(
            select(Groups).where(Groups.uid == new_group.uid)
        ).scalar_one_or_none()
  
        if exist_group is not None:
            exist_group.bird = new_group.bird
            exist_group.code = new_group.code
            exist_group.comment = new_group.comment
            exist_group.fish = new_group.fish
            exist_group.gid = new_group.gid
            exist_group.glfs = new_group.glfs
            exist_group.huid = new_group.huid
            exist_group.interact = new_group.interact
            exist_group.mammal = new_group.mammal
            exist_group.sqlite = new_group.sqlite
            exist_group.sqliteid = new_group.sqliteid
            exist_group.split = new_group.split
            exist_group.timestart = new_group.timestart
            exist_group.timeend = new_group.timeend
        
            session.commit()
            

        
            