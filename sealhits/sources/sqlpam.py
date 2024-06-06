"""
sqlpam.py - Reading data from the annotation SQLite file.

This module contains the following:
    - SQLPAM - a class representing the PAM SQLITE file.
    - TrackChild - a class representing an individual track
    - TrackGroup - a group of TrackChild representing *something*

Examples:

    >>> from pypam.sqlpam import SQLPAM
    >>> sqlitepath = "pam.sqlite3"
    >>> assert os.path.exists(sqlitepath)
    >>> sqlpam = SQLPAM(sqlitepath)
    >>> print(sqlpam.tables)

"""
from __future__ import annotations

__all__ = ["SQLPAM", "TrackGroup"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import sqlite3
import pytz
from datetime import datetime
from pypam.util import checks

# TODO - could we use a nice database shim library abstraction here?
class TrackChild:
    """The class representing the individual track from the PAMGUARD
    pgdf binary file. It contains a UID link to the gemini object from
    the PGDF."""

    def __init__(
        self,
        uid: int,
        utc: str,
        pc_local: str,
        pc_time: str,
        channel: int,
        parent_id: int,
        parent_uid: int,
        long_data_name: str,
        binary_file: str,
    ):
        """Initialise our TrackChild Object.

        Args:
            uid (int): a unique identifier matching the PGDF binary track.
            utc (str): a string representing the time in UTC.
            pc_local (str): the local time on the pc recording.
            pc_time (str): the time on the pc recording.
            channel (int): unknown.
            parent_id (int): The ID of the TrackGroup to which this child belongs.
            parent_uid (int): The UID of the TrackGroup to which this child belongs.
            long_data_name (str): unknown.
            binary_file (str): The filename of the PGDF that holds this track.
        """
        self.uid = uid
        self.utc = datetime.fromisoformat(utc)
        self.utc = pytz.utc.localize(self.utc)
        self.pc_local_time = pc_local
        self.pc_time = pc_time
        self.channel_bitmap = channel
        self.parent_id = parent_id
        self.parent_uid = parent_uid
        self.long_data_name = long_data_name
        self.parent = None

        # Fix for the bug in pamguard with the binary file
        if binary_file[:2] == "i_":
            self.binary_file = "Gemin" + binary_file


    def _add_parent(self, parent: TrackGroup):
        self.parent = parent

    def __str__(self):
        return (
            str(self.uid)
            + ","
            + str(self.utc)
            + ","
            + str(self.pc_local_time)
            + ","
            + str(self.pc_time)
            + ","
            + str(self.channel_bitmap)
            + ","
            + str(self.parent_id)
            + ","
            + str(self.parent_uid)
            + ","
            + str(self.long_data_name)
            + ","
            + str(self.binary_file)
        )


class TrackGroup:
    """A group of TrackChild that may have annotations."""

    def __init__(
        self,
        id : int,
        uid: int,
        utc: str,
        pc_local: str,
        pc_time: str,
        channel: int,
        end_time: str,
        dc: int,
        track_type: str,
        comment: str,
        mammal: int,
        fish: int,
        bird: int,
        interact: bool,
    ):
        """Initialise our TrackGroup Object.

        Args:

            uid (int): a unique identifier matching the PGDF binary track, although not that unique it seems :/
            utc (str): a string representing the time in UTC.
            utc_milli (int): an int number of milliseconds since the epoch in utc.
            pc_local (str): the local time on the pc recording.
            pc_time (str): the time on the pc recording.
            channel (int): unknown.
            end_time (str): When does the last Track in this group finish?
            dc (int): unknown.
            track_type (str): unknown.
            comment (str):
            mammal (int): Was this trackgroup a mammal?
            fish (int): Was this trackgroup a fish?
            bird (int): Was this trackgroup a bird?
            interact (bool): Did this trackgroup interact with the turbine?
        """
        self.id = id
        self.uid = uid
        self.utc = datetime.fromisoformat(utc)
        self.utc = pytz.utc.localize(self.utc)
        self.pc_local_time = pc_local
        self.pc_time = pc_time
        self.channel_bitmap = channel
        self.end_time = datetime.fromisoformat(end_time)
        self.end_time = pytz.utc.localize(self.end_time)
        self.data_count = dc
        self.track_type = track_type  # TODO - enum
        self.comment = comment
        self.mammal = mammal
        self.fish = fish
        self.bird = bird
        self.interaction = interact
        self.children = []

    def __str__(self):
        return (
            str(self.id)
            + ","
            + str(self.uid)
            + ","
            + str(self.utc)
            + ","
            + str(self.pc_local_time)
            + ","
            + str(self.pc_time)
            + ","
            + str(self.channel_bitmap)
            + ","
            + str(self.end_time)
            + ","
            + str(self.data_count)
            + ","
            + str(self.track_type)
            + ","
            + str(self.comment)
            + ","
            + str(self.marine_mammal)
            + ","
            + str(self.fish)
            + ","
            + str(self.bird)
            + ","
            + str(self.interaction)
            + ","
        )

    def add_child(self, child: TrackChild):
        """Add a TrackChild to this TrackGroup.

        Args:
            child (TrackChild): a TrackChild object to add.
        """
        assert child.parent_uid == self.uid
        self.children.append(child)
        child._add_parent(self)
        return self


class SQLPAM:
    """The class that represents the data held in the SQLite
    annotation database. This object will hold the TrackGroups and
    TrackChilds."""

    # TODO - just as with GLF, do we want to concat multiple files?
    # TODO - better checking for return values from the db (I.e missing)

    def __init__(self, sqlite_path):
        """Initialise our SQLPAM object

        Args:
            sqlite_path (str): full path and name of the sqlite_path file.

        """
        con = sqlite3.connect(sqlite_path)
        cur = con.cursor()
        res = cur.execute("SELECT name FROM sqlite_master")
        self.tables = [t[0] for t in res.fetchall()]

        self.track_groups = []
        self.track_children = []

        res = cur.execute(
            "SELECT ID, UID, UTC, PCLocalTime, PCTime, \
            ChannelBitmap, EndTime, DataCount, Track_Type, \
                Marine_Mammal, Fish, Bird, Interaction_with_blades, \
                    Comment FROM Track_Groups"
        )
        tracks = res.fetchall()
        id_uid_lookup = {}

        # TODO - could do some inner join stuff here instead of python combine
        # Read the track groups first off
        for (
            id,
            uid,
            utc,
            pclocal,
            pctime,
            cbitmap,
            endtime,
            dcount,
            ttype,
            mammal,
            fish,
            bird,
            interaction,
            comment,
        ) in tracks:

            # We need extra checks here to make sure
            # numerics are indeed numerics. SQLLite DB has a number
            # of mistakes.

            if mammal is None or not checks.is_float(mammal):
                mammal = -1

            if fish is None or not checks.is_float(fish):
                fish = -1

            if bird is None or not checks.is_float(bird):
                bird = -1

            interact = False

            # This is very annoying and silly
            if interaction is not None:
                if "1" in interaction:
                    interact = True

                if "0" in interaction:
                    interact = False

                elif not checks.is_float(interaction):
                    interact = False

                elif interaction == 1:
                    interact = True
            
                elif interaction == 0:
                    interact = False

            tg = TrackGroup(
                id,
                uid,
                utc,
                pclocal,
                pctime,
                cbitmap,
                endtime,
                dcount,
                ttype,
                comment,
                mammal,
                fish,
                bird,
                interact,
            )

            self.track_groups.append(tg)

            # Use a composite key as only id and uid combined are unique
            id_uid_lookup[str(tg.id) + "-" + str(tg.uid)] = tg

        res = cur.execute(
            "SELECT UID, UTC, PCLocalTime, PCTime, \
            ChannelBitmap, parentID, parentUID, LongDataName, \
                BinaryFile FROM Track_Groups_Children where \
                    BinaryFile is not null"
        )
        children = res.fetchall()

        # Read the track children, adding them to their parent
        for (
            uid,
            utc,
            pclocal,
            pctime,
            cbitmap,
            parentid,
            parentuid,
            ldata,
            bfile,
        ) in children:
            tc = TrackChild(
                uid,
                utc,
                pclocal,
                pctime,
                cbitmap,
                parentid,
                parentuid,
                ldata,
                bfile,
            )
            self.track_children.append(tc)
            parent = id_uid_lookup[str(tc.parent_id) + "-" + str(tc.parent_uid)]
            parent.add_child(tc)
