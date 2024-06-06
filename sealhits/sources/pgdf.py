"""
model.py - build a model from a current ingest.

Functions for processing the PGDFs as part of the ingest.
"""

from __future__ import annotations

import os
import pytz
import datetime
import uuid
import logging
from tqdm import tqdm
from typing import List, Tuple
from sealhits.db.dbschema import Groups, TrackGroup, PGDFS, Points
from sealhits.sources.files import pgdfs_to_full_paths
from pypam import pgdf

from sqlalchemy.orm import (
    Session,
)

__all__ = ["tracks_to_pgdfs", "process_pgdfs"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


def tracks_to_pgdfs(tracks: List[TrackGroup]) -> List[str]:
    """Take the created TrackGroup list and return the PGDFs we need.
    
    Args:
        tracks (List[TrackGroup]): The TrackGroup list of interest.

    Returns:
        List[str]: List of PGDF filenames we need to cover these TrackGroup.
    
    """
    pgdfs_required = []

    for track in tracks:
        binfile = track.binfile
        if binfile not in pgdfs_required:
            pgdfs_required.append(binfile)

    return pgdfs_required


def process_pgdfs(
    session: Session,
    pgdf_path: str,
    pgdfs: List[str],
    groups: List[Groups],
    tracks: List[TrackGroup],
) -> Tuple[List[PGDFS], List[Points]]:
    """Build up the PGDFS, Points and groups_pgdfs tables
    from the list of PGDFs provided.
    
    Args:
        session (Session): The current SQLAlchemy session.
        pgdf_path (str): The path to the PGDFs.
        pgdfs (List[str]): The list of PGDF files we want.
        groups (List[Groups]): The list of Groups from the current session.
        tracks (List[TrackGroup]): The list of TrackGroup in the current session.

    Returns:
        Tuple[List[PGDFS], List[Points]]: The new PGDFS objects and the new Points objects.

    """
    # TODO - this should be a set of transactions that we apply to the db
    # so we don't muck things up if this process crashes.

    assert os.path.exists(pgdf_path)
    logging.info("Process PGDFs starting...")
    logging.info("Creating pgdf -> group...")
    full_paths = pgdfs_to_full_paths(pgdf_path, pgdfs)
    new_pgdfs = []
    new_points = []

    # Read all the PGDFs to get the start & end times
    for pgpath in tqdm(full_paths, desc="Reading PGDFs"):
        fgname = os.path.basename(pgpath)
        tp = pgdf.PGDF(pgpath)
        date_min = None
        date_max = None

        for pamobj in tp.module.objects:
            tdate = pamobj.pam.date
            assert tdate is not None

            if date_min is None:
                date_min = tdate
            elif date_min > tdate:
                date_min = tdate

            if date_max is None:
                date_max = tdate
            elif date_max < tdate:
                date_max = tdate

        # Find the tracks_groups for the groups and file we are currently processing
        logging.info("Creating tracks lookup for file %s", pgpath)

        # Create a second dictionary for fast checking of tracks_groups
        # Dictionaries have O(1) access time apparently. Hashtable like I bet.
        tracks_used = {}
        # We also don't use the pamguard id but a distinct-across-pgdf-files uid
        # of our own, so we need that lookup too.
        track_pam_to_track = {}

        for tg in tracks:
            assert(tg.track_pam_id not in tracks_used.keys())
            tracks_used[tg.track_pam_id] = 0
            track_pam_to_track[tg.track_pam_id] = tg

        # Create a PGDF and add it to the new list
        q = session.query(PGDFS).filter(PGDFS.filename == fgname)
        pgdf_entry = q.one_or_none()

        if pgdf_entry is None:
            pgdf_entry = PGDFS(
                uid=uuid.uuid4(),
                filename=fgname,
                startdate=date_min,
                enddate=date_max,
            )
        else:
            # Update PGDF with new details
            pgdf_entry.startdate = date_min,
            pgdf_entry.enddate = date_max

        new_pgdfs.append(pgdf_entry)

        # Now, we read the points in this PGDF but we must
        # only include these that reference the tracks_groups table.
        # We can safely assume the tracks table is not as stupidly
        # large as the number of annotations is small.
        for pamobj in tp.module.objects:
            pam_track = pamobj.data
            pam_track_uid = pamobj.pam.UID

            try:
                track = pam_track.track
                track_obj = track_pam_to_track[pam_track_uid]
                group = None

                for g in groups:
                    if g.uid == track_obj.group_id:
                        group = g
                        break
                # Should never happen but apparently, HDD 35 and 33 are sort of
                # mixed. Not sure what happened here but we just log and ignore
                if group is None:
                    logging.error("Missing group %s for trackgroup on pgdf %s", track_obj.group_id, fgname)
                    break 
                
                #assert(group is not None)

                # Create the link between the group and pgdf if not already
                if group not in pgdf_entry.groups:
                    pgdf_entry.groups.append(group)

                # Now insert all the points into the database for this known
                # track.
                for point in track.points:
                    q = session.query(Points).filter(
                        Points.time == point.time,
                        Points.sonarid == point.sonar_id,
                        Points.minbearing == point.min_bearing,
                        Points.maxbearing == point.max_bearing,
                        Points.minrange == point.min_range,
                        Points.maxrange == point.max_range,
                        Points.peakbearing == point.peak_bearing,
                        Points.maxvalue == point.max_value,
                        Points.occupancy == point.occupancy,
                        Points.objsize == point.obj_size,
                        Points.track_id == track_obj.track_id,
                    )
                    new_point = q.one_or_none()
                    # No need to run an update existing point as a point
                    # is unique if any of it's attributes are different.
    
                    if new_point is None:
                        new_point = Points(
                            uid=uuid.uuid4(),
                            time=point.time,
                            sonarid=point.sonar_id,
                            minbearing=point.min_bearing,
                            maxbearing=point.max_bearing,
                            minrange=point.min_range,
                            maxrange=point.max_range,
                            peakbearing=point.peak_bearing,
                            peakrange=point.peak_range,
                            maxvalue=point.max_value,
                            occupancy=point.occupancy,
                            objsize=point.obj_size,
                            track_id=track_obj.track_id,
                            group_id=group.uid
                        )

                    else:
                        # Make sure this point has it's group_uid changed!
                        new_point.time=point.time
                        new_point.sonarid=point.sonar_id
                        new_point.minbearing=point.min_bearing
                        new_point.maxbearing=point.max_bearing
                        new_point.minrange=point.min_range
                        new_point.maxrange=point.max_range
                        new_point.peakbearing=point.peak_bearing
                        new_point.peakrange=point.peak_range
                        new_point.maxvalue=point.max_value
                        new_point.occupancy=point.occupancy
                        new_point.objsize=point.obj_size
                        new_point.track_id=track_obj.track_id
                        new_point.group_id=group.uid

                    new_points.append(new_point)

            except KeyError:
                # This track isn't important so skip
                # print(e)
                # TODO - this try except thing is a bit naughty!
                pass

    return (new_pgdfs, new_points)