"""
files.py - find the files on disk that we need.

The various functions that search out the files we want 
and the tracks we are looking for.
"""
from __future__ import annotations

import datetime
import os
from typing import Tuple, List
from pypam import pgdf
from pypam.module import PGObject

__all__ = ["glf_files_avail", "pgdfs_paths", "bin_files_avail", "get_tracks"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


def glf_files_avail(glf_path: str) -> List[str]:
    """Given a starting path, find all the possible glf files.
    
    Args:
        glf_path (str): the path to the GLF files.
    
    Returns:
       List[str]: A list of full paths to all found GLF files.
    
    """
    full_paths = []

    for root, _, files in os.walk(glf_path, topdown=False):
        for name in files:
            _, file_extension = os.path.splitext(name)
            if file_extension.lower() == ".glf":
                full_paths.append(os.path.join(root, name))

    return full_paths


def pgdfs_to_full_paths(pgdf_path: str, pgdfs: List[str]) -> List[str]:
    """Fill out the pgdf filenames with their full paths.

    Args:
        pgdf_path (str): the path to the PGDFS files.
        pgdfs (List[str]): a list of PGDF names to look for
    
    Returns:
       List[str]: A list of full paths to the PGDFS in the pgdfs list.
    """
    full_paths = []

    for root, _, files in os.walk(pgdf_path, topdown=False):
        for name in files:
            if name in pgdfs:
                fpath = os.path.join(root, name)
                full_paths.append(fpath)

    return full_paths


def pgdfs_paths(pgdf_path: str)  -> List[str]:
    """ Find all PGDFs under a given path.
    
    Args:
        pgdf_path (str): the path to the PGDF files.
    
    Returns:
       List[str]: A list of full paths to all found PGDF files.
    """
    full_paths = []

    for root, _, files in os.walk(pgdf_path, topdown=False):
        for name in files:
            _, file_extension = os.path.splitext(name)

            if file_extension.lower() == ".pgdf":
                fpath = os.path.join(root, name)
                full_paths.append(fpath)

    return full_paths


# TODO - we need to double check which Sonar we are reading. We have two remember? Tracks will list a sonar.
def bin_files_avail(
    pdir: str,
) -> List[Tuple[str, datetime.datetime, datetime.datetime]]:
    """Return a list of binary PGDF files with the corresponding date range.
    
    Args:
        pdir (str): the path to the gemini binary files.
    
    Returns:
       List[Tuple[str, datetime.datetime, datetime.datetime]]: A list of paths to the pgdf including the start and end datetimes
    
    """
    efiles = []

    for root, _, files in os.walk(pdir, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            _, file_extension = os.path.splitext(name)

            try:
                if "pgdf" in file_extension.lower():
                    print("Opening pgdf:", fpath)
                    tp = pgdf.PGDF(fpath)

                    if len(tp.module.objects) > 0:
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

                        print("Adding pgdf:", fpath)
                        efiles.append((fpath, date_min, date_max))
                    else:
                        print("PGDF has no module objects.")
            except Exception as e:
                print("Could not read", fpath, e)

    # Sort the efile bases on the dates
    efiles.sort(key=lambda ef: ef[1])

    return efiles


def get_tracks(bin_files: List[str]) -> List[PGObject]:
    """Read the found PGDF files and generate the tracks for our eventual
    dataset.
    
    Args:
        bin_files (str): the path to the PGDF files.
    
    Returns:
       List[PGObject]: A list of PGObject representing tracks from PAMGuard.

    """
    tracks = []

    # TODO - it is possible that one track can cross multiple files.
    # We've ignored this for now
    # https://github.com/PAMGuard/PAMGuardMatlab/blob/main/pgmatlab/loadPamguardMultiFile.m

    # UID in the track group is different to the UID in the Track group children.
    # Trackgroup children UID *should* match the UID in the pgdf

    for fb in bin_files:
        print("Reading bin file:", fb)
        pbin = pgdf.PGDF(fb)
        assert pbin.header.module_type == "Gemini Threshold Detector"

        for obj in pbin.module.objects:
            tracks.append(obj)

    # Sort tracks in order of time if not already
    tracks = sorted(tracks, key=lambda track: track.data.track.time_start)
    return tracks
