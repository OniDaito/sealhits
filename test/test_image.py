'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_image.py - test image functions.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Test our various image functions.
'''

import numpy as np
import time
from sealhits.image import fan_distort
from sealhits.btable import bearing_table


def test_fandistort():
    fan_size = (692, 400)
    img_data = np.ones((fan_size[1], fan_size[0]), dtype=np.uint8) * 255
    start = time.time()
    fan_image = fan_distort(img_data, fan_size[1], bearing_table)
    end = time.time()
    print(end - start)

    #start = time.time()
    #fan_image = fan_distort(img_data, fan_size[1], _bearing_table)
    #end = time.time()
    #print(end - start)

    assert(fan_image[10][10] == 0)
    assert(fan_image[200][300] != 0)