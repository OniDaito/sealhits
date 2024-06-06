
# Tutorials

The following tutorial will show you how to go from the base datafiles to a final dataset that can be used with [ClassySeal](https://gitlab.st-andrews.ac.uk/biology/smru/bjb8/classyseal).

## Ingesting data

The first thing to do is to ingest the data using the ingest.py script. There are three sources of data required:

1. The PAMGuard derived SQLITE database file. This contains the metadata and the group annotations
2. A directory of PGDF files. These binary files are also taken from PAMGuard
3. A directory of GLF files. These hold the Tritech Sonar images and can be quite large. We will generate FITS images from these.

The ingest command can be executed as follows:

    python ingest.py -s /path/to/sqlite3.file -g /path/to/glf/dir -p /path/to/pgdf/dir -b 4 -o /path/to/output/fits/dir -d <database_name>

The '-b' switch specifies the length of the buffer in seconds. This amount of images will be appended and prepended to the group. For more information on the various switches type:

    python ingest.py -h

This command can take up to several days to complete depending on the number and size of the various groups. Multiple ingest commands can be run at once. Depending on the disks, network speed or other restrictions, you may or may not be able to run a large number of ingests at once.

## Generating a dataset

Once the ingest is complete, you can generate a dataset. Let's generate an Rdata dataset. This consists of a number of images, each a crop of the original sonar image and the metadata for each crop.

    python tordata.py -o /path/to/output/dir -c /path/to/cache -i /path/to/fits/dir -e -d <database name>

The cache directory saves the fan distorted images for use later and is optional. The '-e' switch interpolates and cleans the original track.