'''
db.py - The Postgresql Database Object.

This file holds the class that represents everything about our 
data. We use SQLAlchemy as the ORM to wrap the various postgresql
commands and schemas.
'''

from __future__ import annotations

__all__ = [
    "DB",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

from sqlalchemy import create_engine

# Declare our ORM here with the PostgreSQL classes
# TODO session.query might be legacy. Might need to redo it: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-20-query-usage

class DB:
    """Our database class that holds the engine and ORM and what not."""
    # TODO - Import the many functions onto this class (perhaps there is a better way?)
    
    from sealhits.db.dbget import (
        get_groups,
        get_num_groups,
        get_groups_filters,
        get_pgdf_filename,
        get_glf_filename,
        get_group_id,
        get_group_uid,
        get_group_huid,
        get_sqlites,
        get_points_group,
        get_pgdfs,
        get_pgdfs_distinct,
        get_group_gid_sqlite_id_split,
        get_group_gid_sqlite_id,
        get_group_track,
        get_images_groups,
        get_tracks_groups,
        get_tracks_groups_groups_binfile,
        get_image_points_by_filename,
        get_image_points_by_filename_group,
        get_image_groups_by_filename,
        get_tracks_group_uid,
        get_points_from_track,
        get_images_group,
        get_images_group_sonarid,
        get_image_uid,
        get_img_fname
    )

    from sealhits.db.dbset import (
        set_group_timestart,
        set_group_timeend,
        set_point_track,
        set_point_group,
        set_group_split,
        set_group_huid
    )

    from sealhits.db.dbdel import (
        del_by_sqlite
    )

    def __init__(self, db_name, username, password, host="localhost", echo=False):
        con_str = (
            "postgresql+psycopg2://"
            + username
            + ":"
            + password
            + "@"
            + host
            + "/"
            + db_name
        )
        self.engine = create_engine(con_str, echo=echo)
