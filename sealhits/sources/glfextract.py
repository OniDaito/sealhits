"""
glfextract.py - extract numpy arrays from GLF files.

A short utility function to extract numpy arrays
from a GLF file within a particular time range."""

import datetime
import os
import pytz
import numpy as np
from tqdm import tqdm
from typing import Union
from pytritech.glf import GLF


def extract(gpath: str, start_t: datetime.datetime, end_t: datetime.datetime) -> Union[None, np.array]:
    """ Given a path to a GLF file, a start and end time, return a 3D numpy
    array of images within that time frame.
    
    Args:
        gpath (str): The path to a GLF file.
        start_t (datetime.datetime): The starting date time.
        end_t (datetime.datetime): The ending date time.
    
    Returns:
        Union[None, np.array]: either None, or an np.array of frames
    """
    try:
        with GLF(gpath) as gf:
            time_start = None
            time_end = None
            frames = []

            for image_rec in tqdm(gf.images, desc="Ingesting Images"):
                image_time = image_rec.db_tx_time

                if time_start is None:
                    time_start = image_time
                elif image_time < time_start:
                    time_start = image_time

                if time_end is None:
                    time_end = image_time
                elif image_time > time_end:
                    time_end = image_time

                if image_time >= start_t and image_time <= end_t:
                    image_data, image_size = gf.extract_image(image_rec)
                    image_np = np.frombuffer(
                        image_data, dtype=np.uint8
                    ).reshape((image_size[1], image_size[0]))

                    frames.append(image_np)
        
        frames = np.array(frames)
        return frames

    except Exception as e:
        print(e)
    
    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="Seal Hits",
        description="Create a database from a number of PAMGuard files",
        epilog="SMRU St Andrews",
    )
    
    parser.add_argument(
        "-g", "--glf", help="The path to the GLF File"
    )

    parser.add_argument(
        "-s", "--start", help="The start datetime."
    )

    parser.add_argument(
        "-e", "--end", help="The end datetime."
    )

 
    args = parser.parse_args()

    assert(os.path.exists(args.glf))

    tz = pytz.timezone("UTC")

    start_t = datetime.datetime.fromisoformat(args.start)
    end_t = datetime.datetime.fromisoformat(args.end)

    start_t = tz.localize(start_t)
    end_t = tz.localize(end_t)

    res = extract(args.glf, start_t, end_t)
    np.savez("glf.npz", res)

if __name__ == "__main__":
    main()