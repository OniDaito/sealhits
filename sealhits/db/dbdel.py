"""
dbdel.py - The Postgresql delete functions.

Deleting records from the database based on certain
parameters.
"""

from __future__ import annotations

__all__ = [
    "del_by_sqlite",
]

__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


from sqlalchemy.orm import (
    Session,
)

from sealhits.db.dbschema import (
    Points,
    Groups,
    Images,
    GLFS,
    PGDFS,
    TrackGroup
)

def del_by_sqlite(self, sqlite:str):
    """ Delete all the records that were imported from a particular database.
    Effectively an 'undo' of an ingest.

    Args:
        sqlite (str): the name of the sqlite file used in the initial import.
    
    Returns:
        None
    """
    assert(sqlite is not None)

    with Session(self.engine) as session:
        groups = session.query(Groups).where(Groups.sqlite == sqlite).order_by(Groups.gid.asc()).all()

        for group in groups:
            # Track groups list, then remove the points on these tracks first before the tracks themselves
            tracks = session.query(TrackGroup).where(TrackGroup.group_id == group.uid).all()

            for track in tracks:
                # Start deleting points
                points = session.query(Points).where(Points.track_id == track.track_id).all()
            
                for point in points:
                    session.delete(point)

                session.delete(track)

            # Now go with images. This is a many to many so we can only delete these
            # that are only on this group (probably most of them)
            images = session.query(Images).join(Groups, Images.groups).filter(Groups.uid == group.uid)

            for image in images:
                del_image = True

                # If all groups are in this image then delete
                for ig in image.groups:
                    if ig not in groups:
                        del_image = False
                    else:
                        image.groups.remove(ig) # Remove from the list forces ORM to remove from the intermediate table

                if del_image: 
                    session.delete(image)
            

            # GLFS
            glfs = session.query(GLFS).join(Groups, GLFS.groups).filter(Groups.uid == group.uid)

            for glf in glfs:
                del_glf = True

                # If all groups are in this image then delete
                for ig in glf.groups:
                    if ig not in groups:
                        del_glf = False
                    else:
                        glf.groups.remove(ig)
                
                if del_glf: 
                    session.delete(glf)


            # PGDFs
            pgdfs = session.query(PGDFS).join(Groups, PGDFS.groups).filter(Groups.uid == group.uid)

            for pgdf in pgdfs:
                del_pgdf = True

                # If all groups are in this image then delete
                for ig in pgdf.groups:
                    if ig not in groups:
                        del_pgdf = False
                    else:
                        pgdf.groups.remove(ig)
                
                if del_pgdf: 
                    session.delete(pgdf)
        
        # Finally delete the groups
        groups = session.query(Groups).where(Groups.sqlite == sqlite).order_by(Groups.gid.asc()).all()
        
        for group in groups:
            session.delete(group)

        # Actually finally - delete any orphaned points. These may be around despite the groups having
        # been deleted
        subquery = session.query(Groups.uid)
        points = session.query(Points).where(~Points.group_id.in_(subquery))
        
        for point in points:
            session.delete(point)

        session.commit()