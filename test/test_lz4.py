'''
  ______  ______  ____    ____    __   _  ____    __   ______  
 |   ___||   ___||    \  |    |  |  |_| ||    | _|  |_|   ___| 
  `-.`-. |   ___||     \ |    |_ |   _  ||    ||_    _|`-.`-.  
 |______||______||__|\__\|______||__| |_||____|  |__| |______|

test_lz4.py - test compression.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

Test the compression and decompresion.
'''

import pytest
import os
from sealhits.compress import compress, decompress


@pytest.mark.integtest
def test_decompress_compress(get_data):
    ''' Uncompress a FITS with lz4, check it, then compress it
    again, then decompress a second time!'''
    datapath, db, db_blank = get_data
    try:
        fpath = os.path.join(datapath, "fits/2023_05_29/2023_05_29_14_07_53_645_854.fits.lz4")
        img_data, img_header = decompress(fpath)
        assert (img_header['SONARID'] == 854)
        assert (img_data[97][178] == 7)

        vpath = os.path.join(datapath,"test.lz4")
        compress(img_data, img_header, vpath)
        img_data2, img_header2 = decompress(vpath)

        assert(img_header['SONARID'] == img_header2['SONARID'] )
        assert (img_data[97][178] == img_data2[97][178])

        os.remove(vpath)

    finally:
        db.engine.dispose()
        db_blank.engine.dispose()