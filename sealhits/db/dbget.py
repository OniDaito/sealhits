"""
dbget.py - The Postgresql getter functions.

These functions retrieve records from the db, performing certain
queries to return the data required.
"""

from __future__ import annotations

__all__ = [
    "get_groups",
    "get_num_groups",
    "get_pgdfs",
    "get_pgdf_filename",
    "get_glf_filename",
    "get_group_uid",
    "get_group_gid_sqlite_id_split",
    "get_group_gid_sqlite_id",
    "get_images_groups",
    "get_tracks_groups",
    "get_group_track",
    "get_points_group",
    "get_image_points_by_filename",
    "get_image_points_by_filename_group",
    "get_image_groups_by_filename",
    "get_images_group_sonarid",
    "get_tracks_group_uid",
    "get_points_from_track",
    "get_images_group",
    "get_image_uid",
    "get_img_fname",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import uuid
from typing import List, Union
from sqlalchemy import select

from sqlalchemy.orm import (
    Session,
)
from sealhits.db.dbschema import (
    groups_images,
    Points,
    Groups,
    Images,
    GLFS,
    PGDFS,
    TrackGroup,
)

from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound


def get_groups(self, code=None) -> List[Groups]:
    """return all the groups, ordered by the pamguard sqlite uid ascending. Optionally
    a search can be made using a code.

    Args:
        code (str): a string to match against the 'code' field on groups.

    Returns:
        List[Groups]: the resulting list of 'Groups'

    """
    results = []
    with Session(self.engine) as session:
        if code is not None:
            results = (
                session.query(Groups)
                .where(Groups.code == code)
                .order_by(Groups.gid.asc())
                .all()
            )
        else:
            results = session.query(Groups).order_by(Groups.gid.asc()).all()

    return results


def get_groups_filters(self, filters) -> List[Groups]:
    """Return groups using a number of filters that the user can pass in.
    Filters is a list or tuple containing an appropriate filters for groups such
    as Groups.mammal > 1. Filters must be a list or tuple, not a single filter on
    it's own (though a single filter can be used so long as it's inside a list.)

    Args:
        filters (List[]): as list of 'filters' such as 'Groups.mammal > 1'

    Returns:
        List[Groups]: the resulting list of 'Groups'

    """
    results = []

    with Session(self.engine) as session:
        q = session.query(Groups).filter(*filters).all()
        results = q

    return results


def get_num_groups(self, code=None, originals=False) -> int:
    """Return the count of the groups. Optionally
    a search can be made using a code. Optionally, Originals means these
    with a split number of 0, i.e the group from PAMGuard before it was
    split by ingest.py.


    Args:
        code (str): a string that matches against the 'code' field on Groups.
        originals (bool): return only these groups that were not generated with a split.

    Returns:
        int: the number of groups

    """
    res = 0
    # TODO - this is a bit verbose. Maybe compose where clauses?
    with Session(self.engine) as session:
        if code is not None:
            if originals:
                res = int(
                    session.query(Groups)
                    .where(Groups.code == code)
                    .where(Groups.split == 0)
                    .count()
                )
            else:
                res = int(session.query(Groups).where(Groups.code == code).count())
        else:
            if originals:
                res = int(session.query(Groups).where(Groups.split == 0).count())
            else:
                res = int(session.query(Groups).count())

    return res


def get_pgdfs(self, limit=-1) -> List[PGDFS]:
    """Return all the PGDFs from the DB, with optional limit.

    Args:
        limit (int): an optional limit on how many to return. -1 means no limit.

    Returns:
        List[PGDFS]: the resulting list of 'PGDFS'
    """
    results = []

    with Session(self.engine) as session:
        if limit > 0:
            results = (
                session.query(PGDFS).order_by(PGDFS.startdate.asc()).limit(limit).all()
            )
        else:
            results = session.query(PGDFS).order_by(PGDFS.startdate.asc()).all()

    return results


def get_pgdfs_distinct(self) -> List[PGDFS]:
    """Return all the PGDFs with no duplicates. Why there should be duplicates I am not sure.

    Returns:
        List[PGDFS]: the resulting list of 'PGDFS'

    """
    results = []

    with Session(self.engine) as session:
        results = session.query(PGDFS).order_by(PGDFS.startdate.asc()).distinct().all()

    return results


def get_pgdf_filename(self, fname: str) -> Union[PGDFS | None]:
    """Return a single PGDF matching the filename.

    Args:
        fname (str): the filename to match against.

    Returns:
        Union[PGDFS | None]: either the matching PGDFS or None.

    """
    result = None

    with Session(self.engine) as session:
        stmt = select(PGDFS).where(PGDFS.filename == fname)
        result = session.scalars(stmt).one_or_none()

    return result


def get_glf_filename(self, fname: str) -> Union[GLFS | None]:
    """Return a single GLF matching the filename.

    Args:
        fname (str): the filename to match against.

    Returns:
        Union[GLFS | None]: either the matching GLFS or None.

    """
    result = None

    with Session(self.engine) as session:
        stmt = select(GLFS).where(GLFS.filename == fname)
        result = session.scalars(stmt).one_or_none()

    return result


def get_group_id(self, id: str) -> Union[Groups | None]:
    """Get a group with either a string UID, or a HUID.

    Args:
        id (str): the id either as a UUID or a HUID.

    Returns:
        Union[Groups | None]: either the matching 'Groups' or None.

    """
    try:
        uid = uuid.UUID(id)
        return self.get_group_uid(uid)
    except ValueError:
        return self.get_group_huid(id)


def get_group_uid(self, uid: uuid.uuid4) -> Union[Groups | None]:
    """Return a Groups object matching the uid.

    Args:
        uid (uuid.uuid4): the uid to match against.

    Returns:
        Union[Groups | None]: either the matching 'Groups' or None.
    """
    result = None

    with Session(self.engine) as session:
        result = session.execute(
            select(Groups).where(Groups.uid == uid)
        ).scalar_one_or_none()

    return result


def get_group_huid(self, huid: str) -> Union[Groups | None]:
    """Return a Groups object matching the human uid. Should be
    only one but we can't be sure.

    Args:
        huid (str): the huid to match against.

    Returns:
        Union[Groups | None]: either the matching 'Groups' or None.

    """
    result = None

    with Session(self.engine) as session:
        result = session.execute(
            select(Groups).where(Groups.huid == huid)
        ).scalar_one_or_none()

    return result


def get_group_track(self, track_id: uuid.uuid4) -> Union[Groups | None]:
    """Return a group, given a track uid.

    Args:
        track_id (uuid.uuid4): the uid of the track to match against.

    Returns:
        Union[Groups | None]: either the matching 'Groups' or None.

    """
    result = None

    with Session(self.engine) as session:
        result = session.execute(
            select(Groups)
            .join(TrackGroup)
            .where(Groups.uid == TrackGroup.group_id)
            .filter(TrackGroup.track_id == track_id)
        ).one_or_none()

        if result is not None:
            return result[0]

    return result


def get_group_gid_sqlite_id_split(
    self, gid: int, sqlite_name: str, sqliteid: int, split: int
) -> Union[Groups | None]:
    """Return a Groups object matching the gid, sqliteid, split and sqlite name.
    These four fields combine for a unique key.

    Args:
        gid (int): the uid to match against.
        sqlite_name (str): value matched against the "sqlite" field in the Groups Schema.
        sqliteid (int): value matched against the "sqliteid" field in the Groups Schema.
        split (int): value matched against the "split" field in the Groups Schema.

    Returns:
        Union[Groups | None]: either the matching 'Groups' or None.

    """
    result = None

    with Session(self.engine) as session:
        result = session.execute(
            select(Groups)
            .where(Groups.gid == gid)
            .where(Groups.sqlite == sqlite_name)
            .where(Groups.sqliteid == sqliteid)
            .where(Groups.split == split)
        ).scalar_one_or_none()

    return result


def get_group_gid_sqlite_id(
    self, gid: int, sqlite_name: str, sqliteid: int
) -> Union[List[Groups] | None]:
    """Return a Groups object matching the gid, sqliteid and sqlite name.
    These three fields combine for a unique key - a bit too complicated sadly.
    We want all the splits.

    Args:
        gid (int): the uid to match against.
        sqlite_name (str): value matched against the "sqlite" field in the Groups Schema.
        sqliteid (int): value matched against the "sqliteid" field in the Groups Schema.

    Returns:
        Union[List[Groups] | None] : Either a list of matching Groups or None

    """
    results = None

    with Session(self.engine) as session:
        results = session.execute(
            select(Groups)
            .where(Groups.gid == gid)
            .where(Groups.sqlite == sqlite_name)
            .where(Groups.sqliteid == sqliteid)
        ).all()
        results = [r[0] for r in results]

    return results


def get_images_groups(self, sonar_id: int) -> List[Groups]:
    """Return a list of all the images that have a group within them that is annotated
    for a particular sonar. It need not have an actual track within the image, therefore
    buffer images and images appearing between tracks appear as well.

    Args:
        sonar_id (int): the sonar id to match against.

    Returns:
        List[Groups]: List of matching Groups

    """
    results = []

    with Session(self.engine) as session:
        results = session.execute(
            select(Images, Groups.uid)
            .join(Images.groups)
            .where(Images.sonarid == sonar_id)
        ).all()

    return results


def get_tracks_groups(self) -> List[TrackGroup]:
    """Return all the track groups table.

     Args:
        None

    Returns:
       List[TrackGroup]: List of matching TrackGroup.
    """
    results = []

    with Session(self.engine) as session:
        stmt = select(TrackGroup)
        results = session.scalars(stmt).all()

    return results


def get_tracks_groups_groups_binfile(
    self, group_uids: List[uuid.UUID], binfile: str
) -> List[TrackGroup]:
    """Return all the track groups table that match the
    group uids and pgdf binary file.

    Args:
        group_uids (List[uuid.UUID]): a list of uids to match against.
        binfile (str): a string that represents the binary file. Matched against binfile.

    Returns:
       List[TrackGroup]: List of matching TrackGroup.

    """
    results = []

    with Session(self.engine) as session:
        q = (
            session.query(TrackGroup)
            .filter(TrackGroup.group_id.in_(group_uids))
            .filter(TrackGroup.binfile == binfile)
            .all()
        )
        results = q

    return results


def get_points_group(self, group_id: Union[uuid.UUID, str]) -> List[Points]:
    """Get all the points for this group. group_id can either be a uuid.uuid4
    or it can be huid string.

    Args:
        group_id (Union[uuid.UUID, str]): Either a uuid for uid, or a string for huid matching.

    Returns:
       List[Points]: List of matching Points.

    """
    results = []
    group_uid = None

    if type(group_id) is uuid.UUID:
        group_uid = group_id
    else:
        g = self.get_group_huid(group_id)
        group_uid = g.uid

    with Session(self.engine) as session:
        q = session.query(Points).filter(Points.group_id == group_uid).all()
        results = q

    return results


def get_sqlites(self) -> List[str]:
    """Return the SQLites we have considered.

    Returns:
       List[str]: List of sqlites in the database as strings.
    """
    results = []
    with Session(self.engine) as session:
        results = session.execute(select(Groups.sqlite).distinct()).scalars().all()

    return results


def get_image_points_by_filename(self, imagefile: str) -> List[Points]:
    """Get all the points for a particular image regardless of group.

    Args:
        imagefile (str): the name of the imagefile to match against.

    Returns:
       List[Points]: List of matching Points.

    """
    results = []
    with Session(self.engine) as session:
        results = (
            session.execute(
                select(Points)
                .join_from(TrackGroup, Points)
                .join_from(TrackGroup, Groups)
                .join_from(Groups, groups_images)
                .join_from(groups_images, Images)
                .filter(Images.hastrack is True)
                .filter(Points.sonarid == Images.sonarid)
                .filter(Images.filename == imagefile)
            )
            .scalars()
            .all()
        )

    return results


def get_image_points_by_filename_group(
    self, imagefile: str, group_id: Union[uuid.UUID, str]
) -> List[Points]:
    """Get all the tracks in an annotated group for this single image.
    We use the groups_key on points to do the matching.

    Args:
        imagefile (str): the image filename to check against.
        group_id (Union[uuid.UUID, str]): group to match against, either with a uuid or huid string.

    Returns:
       List[Points]: List of matching Points.

    """
    results = []
    filters = []

    if type(group_id) is uuid.UUID:
        filters.append(Groups.uid == group_id)
    else:
        filters.append(Groups.huid == group_id)

    with Session(self.engine) as session:
        results = (
            session.execute(
                select(Points)
                .join_from(Groups, Points)
                .join_from(Groups, groups_images)
                .join_from(groups_images, Images)
                .filter(*filters)
                .filter(Points.group_id == Groups.uid)
                .filter(Images.filename == imagefile)
                .filter(Points.time == Images.time)
                .filter(Points.sonarid == Images.sonarid)
            )
            .scalars()
            .all()
        )

    return results


def get_image_groups_by_filename(self, filename: str) -> List[Groups]:
    """Return a list of all the groups in the image with this filename.

    Args:
        filename (str): the image filename to check against.

    Returns:
       List[Groups]: List of matching Groups.
    
    """
    results = []

    with Session(self.engine) as session:
        try:
            results = (
                session.execute(
                    select(Groups)
                    .join_from(Groups, groups_images)
                    .join_from(groups_images, Images)
                    .filter(Images.filename == filename)
                )
                .scalars()
                .all()
            )

        except IntegrityError as e:
            print("get_images_groups failed", e)

    return results


def get_tracks_group_uid(self, group_id: Union[uuid.UUID, str]) -> List[TrackGroup]:
    """Get all the tracks in a particular group.

    Args:
        group_id (Union[uuid.UUID, str]): group to match against, either with a uuid or huid string.

    Returns:
       List[TrackGroup]: List of matching TrackGroup.

    """
    results = []
    group_uid = None

    if type(group_id) is uuid.UUID:
        group_uid = group_id
    else:
        g = self.get_group_huid(group_id)
        group_uid = g.uid

    with Session(self.engine) as session:
        try:
            q = session.query(TrackGroup).filter(TrackGroup.group_id == group_uid).all()

            results = q

        except IntegrityError as e:
            print("get_group_tracks_uid failed", e)

    return results


def get_points_from_track(self, track_uid: uuid.UUID) -> List[Points]:
    """ Get all the points for a particular track, given the track_uid.
    Returns a list of tuple - (time, sonarid, minbearing, maxbearing, minrange,
    maxrange, track, uid).

    Args:
        track_uid (uuid.UUID): the uid of the track

    Returns:
       List[Points]: List of matching Points.
    """
    results = []

    with Session(self.engine) as session:
        try:
            q = session.query(Points).filter(Points.track_id == track_uid).all()

            results = q

        except IntegrityError as e:
            print("get_group_tracks_uid failed", e)

    return results


def get_images_group(self, group_id:Union[str, uuid.UUID]) -> Union[List[Images], None]:
    """Given a group uid return all the images for this group
    in order. Group_uid can be either uuid.UUID4 or a string
    representing the huid.
    
    Args:
        group_id (Union[str, uuid.UUID]): either the huid (str) or uid (uuid) of the group.

    Returns:
       Union[List[Images], None]: List of matching Images or None.
    
    """
    results = None
    filters = []

    if type(group_id) is uuid.UUID:
        filters.append(Groups.uid == group_id)
    else:
        filters.append(Groups.huid == group_id)

    with Session(self.engine) as session:
        try:
            results = (
                session.execute(
                    select(Images)
                    .join_from(Groups, groups_images)
                    .join_from(groups_images, Images)
                    .filter(*filters)
                    .order_by(Images.time.asc())
                )
                .scalars()
                .all()
            )

        except IntegrityError as e:
            print("get_images_group failed", e)

    return results


def get_images_group_sonarid(self, group_id, sonar_id: int) -> Union[List[Images], None]:
    """Given a group uid and a sonarid, return all the images for this group
    in order. Group_id is either a uuid.uuid4 or a huid string.
    
    Args:
        group_id (Union[str, uuid.UUID]): either the huid (str) or uid (uuid) of the group.
        sonar_id (int): the sonar id to check against.

    Returns:
       Union[List[Images], None]: List of matching Images or None.
    
    """
    results = None
    filters = []

    if type(group_id) is uuid.UUID:
        filters.append(Groups.uid == group_id)
    else:
        filters.append(Groups.huid == group_id)

    filters.append(Images.sonarid == sonar_id)

    with Session(self.engine) as session:
        try:
            results = (
                session.execute(
                    select(Images)
                    .join_from(Groups, groups_images)
                    .join_from(groups_images, Images)
                    .filter(*filters)
                    .order_by(Images.time.asc())
                )
                .scalars()
                .all()
            )

        except IntegrityError as e:
            print("get_images_group failed", e)

    return results


def get_image_uid(self, image_uid: uuid.uuid4) -> Union[Images | None]:
    """Does this image exist already? Return it if it does or None if not.
    
    Args:
        image_uid (uuid.uuid4): the uid of the image

    Returns:
       Union[Images | None]: List of matching Images or None.
    """
    result = None

    try:
        with Session(self.engine) as session:
            result = session.query(Images).where(Images.uid == image_uid).first()

    except IntegrityError as e:
        print("get_image_uid failed", e)

    return result


def get_img_fname(self, image_fname: str) -> Union[Images, None]:
    """Does this image exist already? Return it if it does or None if not.
      
    Args:
        image_fname (str): the filename of the image (minus the .lz4)

    Returns:
       Union[Images | None]: List of matching Images or None.
    
    """
    result = None

    try:
        with Session(self.engine) as session:
            result = session.query(Images).where(Images.filename == image_fname).first()

    except MultipleResultsFound as e:
        print("get_img_fname failed - result is not unique", e)
    except NoResultFound:
        pass  # Okay to pass here as this result is valid
    except IntegrityError as e:
        print("get_img_fname failed", e)

    return result
