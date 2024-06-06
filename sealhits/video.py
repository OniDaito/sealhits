"""
video.py - create videos from a numpy array.

Generate video from a list of frames, bounding boxes and group
information.
"""

from __future__ import annotations

__all__ = ["gen_video"]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import ffmpegio
import numpy as np
from sealhits.image import normalise_image
from sealhits.bbox import XYBox
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from palettable.scientific.sequential import Batlow_20


def gen_video(
    frames: np.array,
    bbs: List[Tuple[int, XYBox, str]],
    text: str,
    out_path=".",
    colour_map=Batlow_20,
    rate = 4
) -> str:
    """Given the original frames and a Bounding Box list, create our final video. The BBS list is in the format
    (frame number, xmin, ymin, xmax, ymax, colour).
    The path is the full path to the video file, plus the extension (which determines the type).

    Args:
        frames (np.array): the frames that makeup the video.
        bbs (List[Tuple[int, XYBox, str]]): the list of bounding boxes, frame numbers and the colour.
        text (str): text to draw.
        out_path (str): the full path to the video. Must end in a video type like '.mp4' or '.webm'.
        colour_map (palettable.Palette): the colour palette to use.
        rate (int): frames per second.

    Returns:
       str: path to the saved video.
    """
    over_frames = []
    font = ImageFont.truetype("./Hack-Regular.ttf", 16)

    for fidx in range(frames.shape[0]):
        frame = frames[fidx]
        blank_image = Image.fromarray(
            np.full((frame.shape[0], frame.shape[1], 3), (0, 0, 0), np.uint8)
        )
        draw = ImageDraw.Draw(blank_image)
        lines = text.split("\n")

        for i, line in enumerate(lines):
            draw.text((10, i * 20), str(line), font=font)

        if bbs is not None:
            for frame_id, bbox, colour in bbs:
                if frame_id == fidx:
                    draw.rectangle(bbox.tuple(), outline=colour)

        over_frames.append(np.array(blank_image))

    # Now create a quick video
    coloured = frames

    # If this is a luminance image, do the nice colour mapping
    if len(frames.shape) == 3 or (frames.shape[-1] == 1 and len(frames.shape) == 4):
        np_fan = np.array(normalise_image(frames) * 255, dtype=np.uint8)
        coloured = np.zeros((*np_fan.shape, 3), dtype=np.uint8)

        # Take entries from RGB LUT according to greyscale values in image
        lut = [colour_map.mpl_colormap(x / 255.0) for x in range(256)]
        lut = [[int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)] for x in lut]
        np.take(lut, np_fan, axis=0, out=coloured)

        np_track = np.array(over_frames, dtype=np.uint8)
        coloured = np.maximum(coloured, np_track)

    ffmpegio.video.write(out_path, rate, coloured, overwrite=True, show_log=False)
    return out_path
