# Explanation
SealHits brings together all the data from the the Tritech Sonar and PAMGuard into a single database and a set of [FITS](https://en.wikipedia.org/wiki/FITS) files for ease of use in other applications. Once the data is brought together, it can be processed and converted into datasets for use with deep learning systems.

Sealhits brings the data together for analysis, processing and eventual reconfiguring into useful datasets.

## Ingesting

Before any final datasets can be produced, the various sources must be *ingested*. Once ingestion has finished, you will have a complete postgresql database and a directory of FITS images.

The database contains all the information required to reproduced the hand-annotated tracks/groups from PAMGuard. This includeds the classification, the points, any comments etc.

In addition, there will be a directory of FITS images (using [lz4 compression](https://en.wikipedia.org/wiki/LZ4_(compression_algorithm))). These represent the frames of sonar images required to reproduce the tracks/groups. Some of these will be buffer images - a number of second before and after the group.

The ingest program will do the following things in order:

1. Read the groups from the sqlite database, ignoring any groups that already exist in the database (unless the -q switch is passed).
2. Split the groups into subgroups if there are any gaps longer than the buffer amount (set with the -b flag).
3. With the groups obtained, read all the PGDFs, recording their start and end times.
4. Find all the relevant points from the PGDFs, storing them in the database.
5. Read all the GLFs, recording their start and end times.
6. Export all the frames from the GLFs that correspond to the track points time in each group, saving as a FITS image.

## Creating datasets

Once the ingest is complete, we can creat datasets for use with our various deep-learning programs and models. The project CrabSeal can generate datasets for use with our neural network project OceanMotion.

## Looking at the data

With all the data collected in one place, one can look at the data more widely. PostgreSQL queries are one way. The program video.py generates videos of the groups, complete with the tracks as bounding boxes.
