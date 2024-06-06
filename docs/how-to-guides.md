# How-to guides

The following are a number of short guides on how perform some of the key processes in sealhits.

## Bring data from PAMGuard and Tritech into the database

The ingest program requires a database be available (in this case, a postgresql database called sealhits, with the sealhits user). The following parameters are required:

* -s - The path to the sqlite3 file we are importing from.
* -g - The path to where the GLFs live.
* -p - The path to the PGDFs.
* -b - The buffer size in seconds.
* -o - The output directory for the FITS image files.
* -d - The database name.

Ingest will look at the groups, tracks and pgdfs in the sqlite file. It will then find out which are the new groups (that don't already exist in the database) and will add the new ones. The PGDFs and GLFS do not need to be organised or grouped to match - ingest will search all GLFs and PGDFs available and find the ones that match the groups from the sqlite.

    python ingest.py -s /mnt/spinning0/sealhits/sqlites/MeygenTritechDetectHDD_12Binary_GH_221220.sqlite3 -g /mnt/smru-sonar -p /mnt/spinning0/sealhits/pgdfs -b 4 -o /mnt/spinning0/sealhits/fits -d sealhits

The resulting output will be a populated database with the associated FITS files, compressed with LZ4 compression. From here, other programs such as video.py.

## Process GLFs on their own

If you passed the '-v' option to ingest.py, you will have skipped processing the GLF files. This can be useful if you just need the data from the PGDFs and the sqlite databases. Sometimes, GLF ingests will fail for various reasons and may need running again. If you have read in the databases correctly and just need to re-ingest the GLF files, you can do so with the following command:

    python ingest_glfs_hdd.py -i /path/to/glfs -d sealhits -a oursqlitefile.sqlite3 -o /output/folder/for/images

This command will look in the GLFs folder and extract the matching images against the datbase, spitting out fits files into the output directory. This program works on a per sqlite3/hard-disk capacity. Any groups with a matching 'sqlite' column will be checked.

Ingesting GLFs is the most time consuming operation of the entire ingest process by quite some way.

## Verify the data is correct 

*to-do*

## Generate Videos from the data

It's useful to see what the data look like in the form of a video.

    python video.py -o ~/tmp -d testseals -u testseals -w testseals -y 1200 -i ../sealhits_testdata/fits -c ~/tmp/cache -b b51d4e92-7259-4fc2-b13e-83878763fccf

This command will generate a video of the group 'b51d4e92-7259-4fc2-b13e-83878763fccf', from the database 'testseals'. The following parameters are:

* -o - The output directory for the video.
* -d - The database name.
* -u - The username for the database.
* -w - The password for the database.
* -y - The height of the final video.
* -i - The path to the fits files.
* -c - The path to the cache of fan images (if it exists).
* -b - Draw the bounding boxes for this track.


## SQL queries

Some SQL queries that can be performed on the database.

### Get all the images for a group

    select * from images ig
    inner join groups_images gi
    on gi.image_id = ig.uid
    inner join groups gg
    on gg.uid = gi.group_id
    where gg.uid = '16010b86-8c0e-4ec0-93b3-00414842286d';

### Get all the points in a group

These points are associated with a group post splitting.

    select * from points ps
    inner join groups gg
    on gg.uid = ps.group_id
    where gg.uid = '16010b86-8c0e-4ec0-93b3-00414842286d';