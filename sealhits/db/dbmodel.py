"""
dbmodel.py - The Postgresql database model.

The model of the database, with all the objects 
loaded into a session for comparison. DBModel holds a 
representation of the database in order to compare against
the real database. This comparison is used when updating the
real database with new information.
"""

__all__ = ["DBModel", "gen_model", "diff_models"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from sqlalchemy.orm import (
    Session,
)

from sealhits.db.dbschema import GLFS, PGDFS, Groups, Images, Points, TrackGroup

class DBModel:
    """ Simmple struct like class to hold the model."""
    def __init__(self):
        self.groups = []
        self.points = []
        self.images = []
        self.pgdfs = []
        self.glfs = []
        self.track_groups = []


def gen_model(session: Session, sqlname: str) -> DBModel:
    """ Return the objects in our ORM model for a particular sqlname, 
    within a session. Mostly this is used to compare against a recent 
    ingest to see what needs to be deleted.

    Args:
        session (Session): the current sqlalchemy session.
        sqlname (str): The name of the sqlite file of the recent ingest.

    Returns:
        DBModel: the generated model reflecting just the single sqlite ingest.

    """
    model = DBModel()

    with session.no_autoflush:
        model.groups = session.query(Groups).filter(Groups.sqlite == sqlname).all()

        for group in model.groups:
            model.images += group.images
            model.pgdfs += group.pgdfs
            model.glfs += group.glfs

            tg = (
                session.query(TrackGroup)
                .filter(TrackGroup.group_id == group.uid)
                .all()
            )

            model.track_groups += tg

            tp = (
                session.query(Points)
                .filter(Points.group_id == group.uid)
                .all()
            )

            model.points += tp

    return  model


def diff_models(session: Session, model_a: DBModel, model_b: DBModel) -> DBModel:
    """ Compare two models - find the objects that do not exist in model_b
     but do exist in model_a and therefore should be removed from model_a.
     
    Args:
        session (Session): the current sqlalchemy session.
        model_a (DBModel): the first model of the database.
        model_b (DBModel): the second model to compare against the first.

    Returns:
        DBModel: a model of the differences.
    
     """
    
    model_diff = DBModel()

    # Start with groups
    groups_a = {a.uid for a in model_a.groups}
    groups_b = {b.uid for b in model_b.groups}

    groups_diff = groups_a - groups_b

    for uid in groups_diff:
        tt = (
                session.query(Groups)
                .filter(Groups.uid == uid)
                .one()
            )
        model_diff.groups.append(tt)
    
    # Now Points
    points_a = {a.uid for a in model_a.points}
    points_b = {b.uid for b in model_b.points}

    points_diff = points_a - points_b

    for uid in points_diff:
        tt = (
                session.query(Points)
                .filter(Points.uid == uid)
                .one()
            )
        model_diff.points.append(tt)

    # Images
    images_a = {a.uid for a in model_a.images}
    images_b = {b.uid for b in model_b.images}

    images_diff = images_a - images_b

    for uid in images_diff:
        tt = (
                session.query(Images)
                .filter(Images.uid == uid)
                .one()
            )
        model_diff.images.append(tt)

    # PGDFS
    pgdfs_a = {a.uid for a in model_a.pgdfs}
    pgdfs_b = {b.uid for b in model_b.pgdfs}

    pgdfs_diff = pgdfs_a - pgdfs_b

    for uid in pgdfs_diff:
        tt = (
                session.query(PGDFS)
                .filter(PGDFS.uid == uid)
                .one()
            )
        model_diff.pgdfs.append(tt)

    # GLFS
    glfs_a = {a.uid for a in model_a.glfs}
    glfs_b = {b.uid for b in model_b.glfs}

    glfs_diff = glfs_a - glfs_b

    for uid in glfs_diff:
        tt = (
                session.query(GLFS)
                .filter(GLFS.uid == uid)
                .one()
            )
        model_diff.glfs.append(tt)


    # TrackGroups
    tg_a = {a.track_id for a in model_a.track_groups}
    tg_b = {b.track_id for b in model_b.track_groups}

    tg_diff = tg_a - tg_b

    for uid in tg_diff:
        tt = (
                session.query(TrackGroup)
                .filter(TrackGroup.track_id == uid)
                .one()
            )
        model_diff.track_groups.append(tt)

    return model_diff
