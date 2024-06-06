"""
glf.py - all the functions related to GLF files

Functions for ingesting the GLF files. This involves finding the 
files on disk, picking the ones we need, reading the required
image records, then saving these images to disk as LZ4 compressed
files. 
"""

from __future__ import annotations

import functools
import traceback
import os
import uuid
import datetime
import numpy as np
import logging
from astropy.io import fits
from typing import Tuple, List, Union
from pytritech.glf import GLF
from sealhits.db.dbschema import GLFS, Groups, Images, Points
from pytritech.glftimes import glf_times
from pytritech.util.range import calculate_range
from pytritech.image import ImageRecord
from sealhits.sources.files import glf_files_avail
from sealhits.compress import compress
from sqlalchemy.orm import (
    Session,
)

__all__ = [
    "has_track",
    "sort_times",
    "process_glfs",
    "get_times",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

NUM_THREADS = 16

class GDat(object):
    """An internal object that holds all the details we want on
    our GLFs as we process them."""

    def __init__(
        self,
        startdate: datetime.datetime,
        enddate: datetime.datetime,
        gobj: GLFS,
        full_path: str,
    ):
        self.start_date = startdate
        self.end_date = enddate
        self.gobj = gobj
        self.full_path = full_path


def has_track(session: Session, image_time: datetime.datetime, sonar_id: int) -> bool:
    """Look in the database to see if this image has a track.
    
    Args:
        session (Session): current SQLAlchemy session.
        image_time (datetime.datetime): the datetime of the current image.
        sonar_id (int): the sonar id.
    
    Returns:
       bool: does this image have a track

    """
    delta = datetime.timedelta(milliseconds=10)
    points = []

    with session.no_autoflush:
        points = (
            session.query(Points)
            .filter(
                Points.time >= image_time - delta, Points.time <= image_time + delta
            )
            .all()
        )

    for point in points:
        if point.sonarid == sonar_id:
            return True

    return False


def _get_glf_times(glf_file):
    try:
        times = glf_times(glf_file)
        assert times is not None
        return (times, glf_file)
    except Exception as e:
        print(e)
        return ((None, None), None)


def sort_times(a, b):
    """Sort GDat by start date"""
    s0 = a.start_date
    s1 = b.start_date

    if s0 < s1:
        return -1

    if s0 == s1:
        return 1

    return 0


def sort_times_group(a, b):
    "Sort Groups by time start"
    s0 = a.timestart
    s1 = b.timestart

    if s0 < s1:
        return -1

    if s0 == s1:
        return 1

    return 0


def _find_glf_times_db(session: Session, glffiles: List[str]):
    """See if our GLFS are already in the database. Take the full path,
    look in the DB and return the times as well as the glf files that aren't
    in the db. This search is likely to be a bit slow? Newsflash! It is!

    """
    glfs_in_db = []

    with session.no_autoflush:
        glfs_in_db = session.query(GLFS).all()

    # Convert to a dictionary for speed
    dictg = {}

    for gd in glfs_in_db:
        dictg[gd.filename] = gd

    missing = []
    times = []  # ((start, end), filename)

    for gf in glffiles:
        gname = os.path.basename(gf)

        try:
            gd = dictg[gname]
            times.append(((gd.startdate, gd.enddate), gf))
        except KeyError:
            missing.append(gf)

    return (times, missing)


def get_times(gpath: str) -> Union[Tuple[datetime.datetime, datetime.datetime], None]: 
    """Get the start and end times from this GLF file.
    
    Args:
        gpath (str): path to a single GLF file.
    
    Returns:
       Union[Tuple[datetime.datetime, datetime.datetime], None]: either the start and end times, or None.
    
    """
    try:
        with GLF(gpath) as gf:
            time_start = None
            time_end = None

            for image_rec in gf.images:
                image_time = image_rec.db_tx_time

                if time_start is None:
                    time_start = image_time
                elif image_time < time_start:
                    time_start = image_time

                if time_end is None:
                    time_end = image_time
                elif image_time > time_end:
                    time_end = image_time

            assert time_start is not None
            assert time_end is not None

            return (time_start, time_end)

    except Exception as e:
        logging.error("Failed to read glf: %s, %s", gpath, e)

    return None


def glf_times_range(gpath: str, start_t: datetime.datetime, end_t: datetime.datetime) -> Tuple[ImageRecord, float]:
    """ Given a path to a GLF file, and a start and end time, return an img record and 
    the sonar range. This is an iterator function.
    
    Args:
        gpath (str): path to a single GLF file.
        start_t (datetime.datetime): the start datetime.
        end_t (datetime.datetime): the end datetime.
    
    Returns:
       Union[Tuple[datetime.datetime, datetime.datetime], None]: either the start and end times, or None.
    """

    # TODO - I wonder if this could be made faster with a time index?
    # Also, yielding from within a with statement might mean a lot of opening and closing? Or maybe not?
    try:
        with GLF(gpath) as gf:
            for image_rec in gf.images:
                image_time = image_rec.db_tx_time

                if image_time >= start_t and image_time <= end_t:
                    sonar_range = int(round(calculate_range(image_rec)))
                    yield (image_rec, sonar_range)

    except Exception as e:
        logging.error("_glf_times failed to read glf: %s", gpath)
        logging.error("Exception %s", e)
        raise IOError


def glf_get_image(gpath: str, image_rec) -> Tuple[bytes, Tuple[int, int]]:
    """
    Get an image from a GLF file using the given record
    
    Args:
        gpath (str): path to a single GLF file.
        image_rec (ImageRecord): the GLF File image record
    
    Returns:
       Tuple[bytes, Tuple[int, int]]: raw data as bytes and the width and height in pixels as ints.
    
    """
    # TODO - as nice as it is to wrap the GLF path here, this means a double
    # open often, as glf_get_image can be inside a loop with glf_times_range above
    # Might need to think about how these two functions are used together.
    # It's also a small function so maybe there's a better way?
    try:
        with GLF(gpath) as gf:
            image_data, image_size = gf.extract_image(image_rec)
            return image_data, image_size

    except Exception as e:
        logging.error("_glf_times failed to read glf: %s", gpath)
        logging.error("Exception %s", e)
        return None


def process_glf_by_group(
    session: Session, group: Groups, fname_lookup, gdats: List[GDat], max_glf: int, outpath: str
) -> Tuple[List[Images], dict]:
    """Process a single group, outputting all of the images from both sonars for the
    time period of this group. fname_lookup is altered by the function, storing the new
    image objects by the filename.
    
    Args:
        session (Session): the current SQLAlchemy session.
        group (Groups): the Group we are currently looking at.
        fname_lookup (dict):  a lookup of images by filename. Can be an empty dict.
        gdats (List[GDat]): a list of GDat objects.
        max_glf (int): the maximum number of images to consider.
        outpath (str): where to save the output images.
    
    Returns:
       Tuple[List[Images], dict]: A list of the new Images objects created and the dict mapping filenames onto these images objects.
    
    """

    group_start = group.timestart
    group_end = group.timeend
    group_image_count = 0
    new_images = []

    # We need a check here on the length of the group as there are some erroneous
    # SUPER long groups we can't ingest really. Anything longer than 2 minutes ignore
    # TODO - could potentialy ingest *up-to* this seconds amount?
    gdd = group.timeend - group.timestart

    if gdd.total_seconds() > max_glf:
        logging.warn(
            "Group %s is much too long with a time of %s seconds.",
            group.huid,
            str(gdd.total_seconds()),
        )
        return new_images, fname_lookup  # Empty at this point

    found_gdat = False

    for gdat in gdats:
        glfname = gdat.gobj.filename

        # If our start is greater, we've already passed it as gdats is ordered.
        # probably doesn't save us too much time.
        if gdat.start_date > group_end:
            break

        if group_start <= gdat.end_date and group_end >= gdat.start_date:
            # Link GLF to group.
            with session.no_autoflush:
                # Check it doesn't exist already as sometimes we get duplicates
                if group not in gdat.gobj.groups:
                    gdat.gobj.groups.append(group)

            # Now fully read in the GLF
            # We read one frame at a time because it will use a lot of memory
            # TODO - could we check to see if the FITS already exists BEFORE the call to _glf_times?
            try:
                for image_rec, srange in glf_times_range(
                    gdat.full_path, group_start, group_end
                ):
                    found_gdat = True

                    image_time = image_rec.db_tx_time
                    sonar_id = image_rec.header.device_id
                    milli = int(image_time.microsecond / 1000)
                    ext = ".fits"

                    # Setup the FITS filename; a combination of time and sonar id.
                    fname = (
                        image_time.strftime("%Y_%m_%d_%H_%M_%S_")
                        + f"{milli:03d}"
                        + "_"
                        + str(sonar_id)
                        + ext
                    )

                    fname_compressed = fname + ".lz4"
                    subdir = os.path.join(outpath, image_time.strftime("%Y_%m_%d"))

                    if not os.path.exists(subdir):
                        os.mkdir(subdir)

                    # Check to see if this image already exists. It might if groups overlap
                    full_fits_path = os.path.join(subdir, fname_compressed)

                    if not os.path.exists(full_fits_path):
                        # TODO - remove this I think or fire up an error to ignore this GLF
                        # as looping around is not ideal!
                        # For some reason, this can fail too but the file seems fine.
                        # Therefore, we should loop around again till it reads correctly
                        res = glf_get_image(gdat.full_path, image_rec)
                        image_data, image_size = res

                        try:
                            image_np = np.frombuffer(image_data, dtype=np.uint8).reshape(
                                (image_size[1], image_size[0])
                            )

                            hdr = fits.Header()
                            hdr["SONARID"] = sonar_id
                            hdr["WIDTH"] = image_size[0]
                            hdr["HEIGHT"] = image_size[1]
                            hdr["YEAR"] = image_time.year
                            hdr["MONTH"] = image_time.month
                            hdr["DAY"] = image_time.day
                            hdr["HOUR"] = image_time.hour
                            hdr["MINUTE"] = image_time.minute
                            hdr["SECOND"] = image_time.second
                            hdr["MILLI"] = int(image_time.microsecond / 1000)
                            # hdr = fits.PrimaryHDU(image_np, header=hdr)
                            # hdul = fits.HDUList([hdr])
                            # hdul.writeto(full_fits_path)
                            compress(image_np, hdr, full_fits_path)

                            del image_data
                            del image_np
                            del hdr

                            logging.info(
                                "Generated %s from %s", full_fits_path, gdat.full_path
                            )

                        except Exception as e:
                            logging.error(
                                "Could not generate FITS: %s, %s",
                                fname,
                                e,
                            )
                            logging.error("Traceback %s", traceback.format_exc())

                    # else:
                    #    logging.info("File %s already exists for group %s", full_fits_path, group.huid)

                    # Now create the DB objects. We create new image objects, or
                    # we find the existing one and modify it. We return all images
                    # and hope our transaction does the right thing in adding or
                    # updating.
                    group_image_count += 1
                    new_image = None

                    with session.no_autoflush:
                        q = session.query(Images).filter(Images.filename == fname)
                        new_image = q.one_or_none()

                    # It's also possible that we already have this image ready to be committed to the
                    # DB but it gets pulled in again for a different group so we must check
                    if fname in fname_lookup.keys():
                        new_image = fname_lookup[fname]

                    if new_image is None:
                        ht = has_track(session, image_time, sonar_id)

                        new_image = Images(
                            uid=uuid.uuid4(),
                            filename=fname,
                            hastrack=ht,
                            glf=glfname,
                            time=image_time,
                            sonarid=sonar_id,
                            range=srange,
                        )

                    fname_lookup[fname] = new_image

                    if group not in new_image.groups:
                        new_image.groups.append(group)

                    new_images.append(new_image)

            except IOError:
                logging.Error("Failed to read GLF %s. Skipping...", glfname)

    if not found_gdat:
        logging.error("Found no GDATS for group %s ", group.huid)

    if group_image_count == 0:
        logging.error("*** Group %s has no images! ***", group.huid)

    return new_images, fname_lookup


def process_glfs(
    session: Session, groups: List[Groups], glfpath: str, outpath: str, max_glf: int
) -> Tuple[List[GLFS], List[Images]]:
    """Once the PGDFs and SQLITE are processed, we can
    begin to look for the GLF files we need. We want each new group
    to have a number of FITS images fitting the range timestart - buffer
    to time-end + buffer.
    The function split_groups will have split groups and adjusted start and
    end times already so we judt need to look at the group times.
    
    Args:
        session (Session): the current SQLAlchemy session.
        groups (List[Groups]): the Groups we are currently looking at.
        glfpath (str): the path to the GLF fules
        max_glf (int): the maximum number of images to consider.
        outpath (str): where to save the output images.
    
    Returns:
       Tuple[List[GLFS], List[Images]]: Two lists - the new GLFS objects to save to the DB and the new Images objects to save to the DB.
    
    """
    new_glfs = []
    logging.info("Finding available GLF files...")
    glf_files = glf_files_avail(glfpath)

    # Go through all GLFs and get the times of each.
    # Check the database first for the times we already have and
    # only grab the times for GLFs we don't have
    # There might be duplicates due to directory renaming or similar and rsync.
    times, glf_files_missing = _find_glf_times_db(session, glf_files)
    logging.info("Retrieving GLF Times (this may take a while)...")

    if len(glf_files_missing) > 0:
        logging.info("GLFs missing from DB: %s", len(glf_files_missing))
        # commented out due to errors on hdd5 for some reason?
        # with ThreadPool(NUM_THREADS) as pool:
        # times += pool.map(_get_glf_times, glf_files_missing, chunksize=NUM_THREADS)
        for glf_file in glf_files_missing:
            new_times = _get_glf_times(glf_file)

            if new_times[1] is not None:
                times.append(new_times)

    # Add the GLFS regardless of whether or not they are used.
    # times_glfs is the list of all the info we need.
    # gdats are just a struct that holds the times, database
    # object and path together.
    gdats = []

    for (glf_start, glf_end), glf_path in times:
        glfname = os.path.basename(glf_path)
        new_glf = None

        with session.no_autoflush:
            q = session.query(GLFS).filter(GLFS.filename == glfname)
            new_glf = q.one_or_none()

        # It's possible (for some reason) that GLFS might get double
        # counted in the addition phase, so make sure it doesn't exist
        # in the new_glfs already
        for ng in new_glfs:
            if ng.filename == glfname:
                new_glf = ng

        if new_glf is None:
            new_glf = GLFS(
                uid=uuid.uuid4(),
                filename=glfname,
                startdate=glf_start,
                enddate=glf_end,
                groups=[],
            )

        new_glfs.append(new_glf)
        gdats.append(GDat(glf_start, glf_end, new_glf, glf_path))

    # Make sure there are no errored entries and organise by time
    # Sorting by time makes the FITS export a little quicker.
    gdats = sorted(gdats, key=functools.cmp_to_key(sort_times))
    logging.info("Number of initial time ranges: %s", len(gdats))
    gdat_latest = gdats[-1].end_date

    for gd in gdats:
        if gd.end_date > gdat_latest:
            gdat_latest = gd.end_date

    logging.info(
        "GDats earliest %s and latest %s.", str(gdats[0].start_date), str(gdat_latest)
    )

    sofar = 0
    tlist = []

    logging.info("Number of groups: %s", len(groups))

    # The goal at this stage is to match up new group times with GLF times
    # and only process the files we need to, even if we've recorded a whole
    # batch of GLFs for a time period.
    groups = sorted(groups, key=functools.cmp_to_key(sort_times_group))
    group_earliest = groups[0].timestart
    group_latest = groups[0].timeend

    for g in groups:
        if g.timeend > group_latest:
            group_latest = g.timeend

    assert group_earliest < group_latest
    logging.info(
        "Groups earliest %s and latest %s.", str(group_earliest), str(group_latest)
    )

    new_images = []
    new_images_by_fname = {}  # Fast lookup

    # Start off the threads, chunking up the IDs then submitting to the threaded function.
    while len(groups) > 0:
        while len(groups) > 0 and len(tlist) < NUM_THREADS:
            tlist.append(groups.pop())

        for group in tlist:
            ni, nf = process_glf_by_group(
                session, group, new_images_by_fname, gdats, max_glf, outpath
            )
            new_images += ni
            new_images_by_fname = nf

        sofar += len(tlist)
        tlist = []
        logging.info("Processed %s. %s remaining.", sofar, len(groups))

    return (new_glfs, new_images)
