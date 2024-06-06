"""
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_video.py - test the video functions.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Test the video functions.
"""

import os
import pytest
import numpy as np
from sealhits import utils
from sealhits.video import gen_video
from video import check_cache
from sqlalchemy import text


@pytest.mark.integtest
def test_create_video(get_data):
    datapath, db, db_blank = get_data
    huid= ""
    try:
        with db.engine.connect() as con:
            result = con.execute(text("select huid from groups limit 1;"))
                
            for r in result:
                huid = r[0]
            
        images = db.get_images_group_sonarid(huid, 854)
        for image in images:
            print(image.filename)
        fan_size = utils.get_fan_size(400)
        frames = []
    
        for img in images:
            fname = img.filename + ".lz4"
            fresult = utils.fast_find(fname, os.path.join(datapath, "fits"))
            nframe = check_cache("", fname, fresult, fan_size)
            frames.append(nframe)

        assert(len(frames) > 0)

        frames = np.array(frames).astype(np.uint8)
        vid_path = os.path.join(datapath, "test.mp4")
        gen_video(frames, [], "test text", vid_path)
        assert(os.path.exists(vid_path))
        os.remove(vid_path)
    finally:
        db.engine.dispose()
        db_blank.engine.dispose()