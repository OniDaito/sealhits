"""
group.py - group object functions

Functions for sorting out group objects, such as fixing the times
and splitting based on a buffer time.
"""

from __future__ import annotations

import pytz
import datetime
import os
import uuid
import logging
from human_id import generate_id
from tqdm import tqdm
from typing import List, Tuple
from sealhits.db.dbschema import Groups, Points, TrackGroup

from sqlalchemy.orm import (
    Session,
)
from sqlalchemy import or_


from sealhits.sources import sqlpam

__all__ = ["find_group_objects", "split_groups", "fix_group_times"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


def find_group_objects(
    session: Session, sqldb: sqlpam.SQLPAM, sqlname: str, sqlalias: str, max_secs=800
) -> Tuple[List[Groups], List[TrackGroup]]:
    """Start by finding the Groups and TrackGroups from the
    SQLITE file and creating these in memory.

    sqlalias is required in case one is reading in an updated or otherwise changed sqlitefile
    that has a different name. Groups will exist from this previous version of the file and 
    should be included. sqlalias should be set to the name of that older file. Otherwise, alias
    should match sqlname.
    
    Args:
        session (Session): The current SQLAlchemy session.
        sqldb (SQLPAM): The SQLPAM database object we are reading.
        sqlname (str): The filename of the sqlite file.
        sqlalias (str): If we are reading from a different sqlite file but want to lookup with an alias, add a different name here.
        max_secs (int): The maximum length of group to consider in seconds.

    Returns:
         Tuple[List[Groups], List[TrackGroup]]: Two lists, the new Groups objects and the TrackGroup objects.
    """
    group_list = sqldb.track_groups
    found_groups = []
    found_tracks = []

    logging.info("Reading Groups...")

    for g in tqdm(group_list, desc="Reading Groups"):
        interaction = g.interaction
        code = "none"

        if g.track_type is not None:
            code = g.track_type.lower()

        # Start with the master group object
        # Check the *real* composite primary key. If it exists,
        # return that instead of a new thing. Means we can use
        # merge later on to do easy updates.
        # split can be -1 or 0. If it's not been split or it's been split and it's the first one.
        new_group = None

        with session.no_autoflush:
            q = session.query(Groups).filter(
                Groups.gid == g.uid,
                Groups.sqliteid == g.id,
                or_(Groups.split == -1, Groups.split == 0),
                Groups.sqlite == sqlalias,
            )

            new_group = q.one_or_none()

        if new_group is None:
            huid = generate_id()
            new_group = Groups(
                uid=uuid.uuid4(),
                gid=g.uid,
                sqliteid=g.id,
                sqlite=sqlname,
                huid=huid,
                timestart=g.utc,
                timeend=g.end_time,
                code=code,
                comment=g.comment,
                mammal=g.mammal,
                fish=g.fish,
                bird=g.bird,
                interact=interaction,
                split=-1,
                pgdfs=[],
                images=[],
                glfs=[],
            )
            logging.info("New Group: %d, %d, %s, %s", g.uid, g.id, sqlname, huid)
        else:
            # Check to see if this group needs updating
            new_group.timestart = g.utc
            new_group.timeend = g.end_time
            new_group.code = code
            new_group.comment = g.comment
            new_group.mammal = g.mammal
            new_group.fish = g.fish
            new_group.bird = g.bird
            new_group.interact = interaction
            # We may need to change the sqlname which is part of the composite key
            # We set it to the new SQLITEDB we are importing.
            new_group.sqlite = sqlname

        # Early rejection of groups that are too long. Note that due to bugs in PAMGuard
        # the group times may not be accurate. However, we reject here so that the tracks
        # are also not included. TODO - this could be improved.
        td = datetime.timedelta(seconds=max_secs)

        if new_group.timeend - new_group.timestart > td:
            logging.warn("Found %s Group that exceed %d seconds! Not including!", new_group.huid, max_secs)
            continue

        # Now Look at the track children - this links to the
        # PGDFs we are interested in.
        # We also add the track_id to the tracks_groups table
        # using our own UUID instead of the gids
        for c in g.children:
            binary_file = c.binary_file
            # Make sure the binary file is a single filename
            # with the pgdf extension
            binary_file = os.path.basename(binary_file)

            if binary_file[-5:] != ".pgdf":
                binary_file += ".pgdf"

            new_track = None

            with session.no_autoflush:
                q = session.query(TrackGroup).filter(
                    TrackGroup.track_pam_id == c.uid,
                    #TrackGroup.group_id == new_group.uid, # Commented as it's pam and binary that are unique identifiers before we add uids
                    TrackGroup.binfile == binary_file,
                )
                new_track = q.one_or_none()

            if new_track is None:
                new_track = TrackGroup(
                    track_id=uuid.uuid4(),
                    track_pam_id=c.uid,
                    group_id=new_group.uid,
                    binfile=binary_file,
                )
            else:
                # update the new trackgroup with latest
                new_track.track_pam_id = c.uid
                new_track.binfile = binary_file

            found_tracks.append(new_track)

        if len(found_tracks) > 0:
            found_groups.append(new_group)
        else:
            logging.warn("Found %d Group with 0 tracks! Not including!", new_group.huid)

    logging.info("Found %d Groups and %d Tracks.", len(found_groups), len(found_tracks))

    earliest = found_groups[0].timestart
    latest = found_groups[0].timeend

    for group in found_groups:
        if group.timestart < earliest:
            earliest = group.timestart

        if group.timeend < earliest:
            latest = group.timeend

    logging.info("Found %s Groups and %s Tracks.", str(earliest), str(latest))

    return (found_groups, found_tracks)


def split_groups(
    session: Session, new_groups: List[Groups], new_points: List[Points], buffer_gap=4
) -> Tuple[List[Groups], List[Points]]:
    """It is possible that some groups may have large gaps with no
    tracks. Such groups need to be split, creating new groups .
    This function returns a new list of all the groups including the
    original groups and the new splits, and the changed points.

    Split groups also buffers all groups including these that are not
    split, so each group has a blank area before and after it.

    TrackGroups are not changed. These are mostly irrelevant and are
    there to make matching up the original points to the original group
    easier. The group_id on the Point will point to the new group post
    split.

    Split groups also checks where the true start and end of the groups
    are as occasionally, some groups start earlier or finish later than
    the actual tracks for some reason.
    
    Args:
        session (Session): The current SQLAlchemy session.
        new_groups (List[Groups]): The latest groups we want to split.
        new_points (List[Points]): The latest points we want to re-assign.
        buffer_gap (int): The number of seconds for the start and end buffer. Also, the minimum gap between points in a track before we split.

    Returns:
        Tuple[List[Groups], List[Points]]: The new_groups and new_point with the new split-off groups and reassigned points.
    """
    return_groups = []
    return_points = []
    buffer = datetime.timedelta(seconds=buffer_gap)

    for group in tqdm(new_groups, desc="Splitting new groups."):
        # Check to see if this group has already been split?
        #logging.info("Group split code %s %d", group.huid, group.split)
        
        if group.split != -1:
            logging.info("Group %s has already been split", group.huid)
            # This group has already been assessed so get all splits then continue
            with session.no_autoflush:
                q = session.query(Groups).filter(
                        Groups.gid == group.gid,
                        Groups.sqliteid == group.sqliteid,
                        Groups.sqlite == group.sqlite,
                )

                new_groups = q.all()

                for group_two in new_groups:
                    return_groups.append(group_two)

                continue

        # It hasn't been split, so check if it needs to be
        # First, get all the points and their times from each track.
        group_points = []

        for point in new_points:
            if point.group_id == group.uid:
                group_points.append(point)

        # This should never happen but thanks to issues with data not where it should be
        # (disks 33 and 35) it does :/ Needs a fix at some point.
        if len(group_points) == 0:
            logging.error("No points found on group %s in split attempt.", group.huid)
            continue

        #assert len(group_points) > 0

        # We need to order times, and points, tpamids into ascending order of time
        group_points = sorted(group_points, key=lambda x: x.time)

        # Alter the start and end times of the groups to match the ones found
        # from the tracks. This is a 'belt-and-braces' sort of check given the one
        # problem group found in riverseals.
        new_group_start = group_points[0].time
        new_group_end = group_points[-1].time

        assert(new_group_start >= group.timestart)
        assert(new_group_end <= group.timeend)

        # Splits will contain the indices on which to split the
        # points into new tracks and the groups into new groups.
        # Group splits are the new group uids we've made.
        splits = []
        group_splits = []

        # Find the gaps and mark them up
        for tidx in range(len(group_points) - 2):
            t0 = group_points[tidx].time
            t1 = group_points[tidx + 1].time
            td = t1 - t0

            if td > buffer:
                splits.append(tidx + 1)

        group_time_end = group.timeend

        if len(splits) > 0:
            # Redo the first group - setting it's time end to the correct one.
            group_time_end = group_points[splits[0] - 1].time
            group.timeend = group_time_end
            group.split = 0
            group_splits.append(group)

            # Now create new groups with the same gid but new times
            for sidx, split in enumerate(splits):
                timestart = group_points[split].time
                timeend = group_points[-1].time  # Set to the last time for now

                if sidx + 1 < len(splits):
                    timeend = group_points[splits[sidx + 1] - 1].time

                # Add the buffer times for the new group
                timestart -= buffer
                timeend += buffer

                # New group with new times. We keep the gid but use an incremented string for the sqlite filename
                # 0 in split is the original group (or parent group in this case) so we increment sidx by one as this new group is the 'first split'
                # TODO - we keep the same PGDFs here but eventually we'll need to double check these
                assert(timestart < timeend)
                new_group = None
                
                with session.no_autoflush:
                    q = session.query(Groups).filter(
                        Groups.gid == group.gid,
                        Groups.sqliteid == group.sqliteid,
                        Groups.split == sidx + 1,
                        Groups.sqlite == group.sqlite,
                    )
                    new_group = q.one_or_none()

                if new_group is None:
                    new_group = Groups(
                        uid=uuid.uuid4(),
                        gid=group.gid,
                        sqliteid=group.sqliteid,
                        timestart=timestart,
                        timeend=timeend,
                        sqlite=group.sqlite,
                        code=group.code,
                        comment=group.comment,
                        interact=group.interact,
                        mammal=group.mammal,
                        fish=group.fish,
                        bird=group.bird,
                        split=sidx + 1,
                        huid=generate_id(),
                        pgdfs=group.pgdfs,
                        images=[],
                        glfs=[],
                    )

                assert(new_group is not None)
                return_groups.append(new_group)
                group_splits.append(new_group)

            # We look at each point in turn, assigning it to a new group
            for point in group_points:
                for sgroup in group_splits:
                    if point.time >= sgroup.timestart and point.time <= sgroup.timeend:
                        point.group_id = sgroup.uid
                        break

        return_groups.append(group) # Original group is always returned
        return_points += group_points
    
    return (return_groups, return_points)


def fix_group_times(new_groups: List[Groups], new_points: List[Points]) -> List[Groups]:
    """PAMGuard SQLITE file reports incorrect group times. We therefore
    look at all the tracks and find the earliest and latest times and
    set the group times to match these.
    
    Args:
        new_groups (List[Groups]): The latest groups we want to split.
        new_points (List[Points]): The latest points we want to re-assign.

    Returns:
        List[Groups]: The corrected groups.
    """

    logging.info("Fixing group times...")
    fixed_groups = []

    for group in tqdm(new_groups, desc="Groups fixed"):
        min_time = datetime.datetime.now().astimezone(tz=pytz.UTC)
        max_time = datetime.datetime(2000, 1, 1).astimezone(tz=pytz.UTC)

        # Check to see if we have points directly on this group
        # if we do then we can use these as the groups is
        points = []
        for point in new_points:
            if point.group_id == group.uid:
                points.append(point)

        if len(points) > 0:
            for point in points:
                if point.time < min_time:
                    min_time = point.time

                if point.time > max_time:
                    max_time = point.time

        group.timestart = min_time
        group.timeend = max_time
        fixed_groups.append(group)

    return fixed_groups
