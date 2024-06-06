"""
dbset.py - The Postgresql set functions.

The Postgresql Database SET functions.
These functions set records in the db.
"""

from __future__ import annotations

__all__ = [
    "set_group_timestart",
    "set_group_timeend",
    "set_point_track",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import datetime
import uuid

from sqlalchemy.orm import (
    Session,
)
from sealhits.db.dbschema import (
    Points,
    Groups,
)

from sqlalchemy.exc import IntegrityError

# TODO - why not just pass a group object instead of the uid?
def set_group_timestart(
    self, group_uid: uuid.uuid4, new_timestart: datetime.datetime
):
    """Change the group timestart value. Useful when splitting the group.
    
    Args:
        group_uid (uuid.uuid4): uid of the group
        new_timestart (datetime.datetime): the new datetime for the group start.
    """
    with Session(self.engine) as session:
        try:
            session.query(Groups).filter(Groups.uid == group_uid).update(
                {"timestart": new_timestart}
            )
            session.commit()
        except IntegrityError as e:
            print("set_group_timeend failed", e)


def set_group_timeend(self, group_uid: uuid.uuid4, new_timeend: datetime.datetime):
    """Change the group timeend value. Useful when splitting the group.
    
    Args:
        group_uid (uuid.uuid4): uid of the group
        new_timeend (datetime.datetime): the new datetime for the group end.
    """
    with Session(self.engine) as session:
        try:
            session.query(Groups).filter(Groups.uid == group_uid).update(
                {"timeend": new_timeend}
            )
            session.commit()
        except IntegrityError as e:
            print("set_group_timeend failed", e)


def set_group_huid(self, group_uid: uuid.uuid4, new_huid: str):
    """Set a human readable uid.
    Args:
        group_uid (uuid.uuid4): uid of the group
        new_huid(str): the new human readable ID (huid) 
    
    """
    with Session(self.engine) as session:
        try:
            session.query(Groups).filter(Groups.uid == group_uid).update(
                {"huid": new_huid}
            )
            session.commit()
        except IntegrityError as e:
            print("set_group_huid failed", e)


def set_group_split(self, group_uid: uuid.uuid4, new_split: int):
    """Change the group split. Useful when splitting the group.
    
    Args:
        group_uid (uuid.uuid4): uid of the group
        new_split (int): the new datetime for the group start.
    """
    with Session(self.engine) as session:
        try:
            session.query(Groups).filter(Groups.uid == group_uid).update(
                {"split": new_split}
            )
            session.commit()
        except IntegrityError as e:
            print("set_group_split failed", e)


def set_point_track(self, point_uid: uuid.uuid4, new_track: uuid.uuid4):
    """Change the track that this point belongs to.
    
    Args:
        point_uid (uuid.uuid4): uid of the point
        new_track (uuid.uuid4): the new track this point belongs to.

    """
    with Session(self.engine) as session:
        try:
            session.query(Points).filter(Points.uid == point_uid).update(
                {"track_id": new_track}
            )
            session.commit()
        except IntegrityError as e:
            print("set_point_track failed", e)


def set_point_group(self, point_id: uuid.uuid4, new_group: uuid.uuid4):
    """Change the group that this point belongs to.
    
    Args:
        point_id (uuid.uuid4): uid of the point
        new_group (uuid.uuid4): the new group this point belongs to.
    
    """
    with Session(self.engine) as session:
        try:
            session.query(Points).filter(Points.uid == point_id).update(
                {"group_id": new_group}
            )
            session.commit()
        except IntegrityError as e:
            print("set_point_group failed", e)
