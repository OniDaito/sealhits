"""
model.py - build a model from a current ingest.

Function for creating the current model of the data from
a particular sqlite import.
"""

from __future__ import annotations

__all__ = ["build_model"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from typing import List, Tuple
from sealhits.db.dbschema import Groups, TrackGroup, GLFS, Images, PGDFS, Points
from sqlalchemy.orm import (
    Session,
)


def build_model(
    session: Session, sqlname: str
) -> Tuple[
    List[Groups], List[TrackGroup], List[Points], List[PGDFS], List[GLFS], List[Images]
]:
    """ The goal is to build an existing model from the database
    ready to compare with later. Anything in this model not in the new one
    will need to be deleted.

    Args:
        session (Session): The current SQLAlchemy session.
        sqlname (str): the name of the sqlite file we are attempting to model.

    Returns:
        Tuple[List[Groups], List[TrackGroup], List[Points], List[PGDFS], List[GLFS], List[Images]]: Six lists of the major objects in the database model.
    """
    groups = session.query(Groups).filter(Groups.sqlite == sqlname).all()

    # The following are all dependent on the groups above.
    tracks = []
    points = []
    pgdfs = []
    glfs = []
    images = []

    # TODO - must be a faster way?
    for group in groups:
        # Tracks first
        ts = session.query(TrackGroup).filter(TrackGroup.group_id == group.uid).all()
        for t in ts:
            tracks.append(t)

        # Now lookup points
        ps = session.query(Points).filter(Points.group_id == group.uid).all()
        for p in ps:
            points.append(p)

        # pgdfs, glfs and images - just the ones attached to the group
        pgdfs += group.pgdfs
        glfs += group.glfs
        images += group.images

    return (groups, tracks, points, pgdfs, glfs, images)
