# sealhits

A set of programs relating the Sonar data captured during the Meygen project. Written in Python, these scripts will combine the data from different sources to create statistics, images and videos. The following programs have been implemented:

* ingest.py - combine the pgdf, glf and sqlite3 files to create a unified dataset.
* single.py - output a single image given a timestamp.
* undigest.py - reverse an ingest.py run.
* video.py - create a video file for a particular group.

## setup

Firstly, create a virtual python environment using your preferred method. Then, using pip, install the required libraries

    pip install -r requirements.txt


### Database

Sealhits requires a PostgreSQL database to be setup on the computer running SealHits. Follow the instructions for your OS to install PostgreSQL first.

Using a Postgresql database (in this example called 'sealhits' with the user 'sealhits')

    create user sealhits with password 'kissfromarose' createdb login;
    create database sealhits owner sealhits;

Connecting as the user 'sealhits' to get access to the database is a little trickier:

    sudo vim /etc/postgresql/14/main/pg_hba.conf

Add the following line:

    local   all             sealhits                                md5

Apparently, we might need to edit /etc/postgresql/14/main/pg_ident.conf but not sure:

    sealhits1       <linux username here>                     sealhits

Import the database schema as follows:

    psql -U sealhits sealhits < sealhits.sql

## ingest.py

This is the main program that deals with all the data from PAMGuard and the Tritech Gemini sonar. It writes to the postgresql database all the metadata, and a number of [FITS](https://fits.gsfc.nasa.gov/fits_home.html) files to the disk. It can be run as follows:

   python ingest.py -s <path to sqlite3> -g <path to tritech glfs> -p <path to pamguard pgdfs> -o <output dir>

Ingest will look at the sqlite3 database, creating a tree of groups, tracks and annotations. It will then look for the required PGDF files for the track details, then the GLF files for the images that match these groups. By default, a 4 second buffer is added at the front and back of the group. The length of the buffer in seconds can be adjusted on the command line with the '-b' switch. All images between these start and end times are included. If there is a gap longer than this buffer time, the group is split into two, with this split being marked in the database.

This might need to be run multiple times if there are many sqlite3 files, glf directories etc. The principle restriction is the data held in the sqlite database, as this determines which images are worth exporting.

ingest.py has a number of option related to database name, password, host etc.


## single.py

This program will spit out an image corresponding to a particular sonar and a particular time, as follows:

    python single.py -o <output directory> -i <path to fits images> <image uid>

Like ingest, this script has many parameters related to database names, passwords etc. Width and height of the required output image can also be passed on the command line.


## video.py

The easiest way to see the output of the ingest is to run the video.py script. This program takes a group UID and creates an MP4 file showing the fan view of the sonar, complete with the bounding box marking out the group in question. It can be run as follows:

    python video.py -d sealhits -r <sonar id> -b -o ~/tmp -i <path to fits images> <group uid>

## caches

Depending on the size of the fan images you create, it can be a good idea to use a shared cache that works across video, gen_dataset and all the programs. This cache will hold fan images in FITS format (compressed with LZ4 or uncompressed) at a particular size. Other programs will need to work at this same size if they want to take advantage of the cache.

## Tests

To perform the tests, use pytest. The paths are set with the pytest.ini file.

    pytest

During the first ever run, pytest will attempt to download the test data (Currently located at [https://gitlab.st-andrews.ac.uk/biology/smru/bjb8/sealhits_testdata](https://gitlab.st-andrews.ac.uk/biology/smru/bjb8/sealhits_testdata)). This dataset is quite large so it might take a while to obtain.

The tests assume you have a working PosgreSQL on the test machine. This will need to be installed first, before any tests can be run. Once this is setup on your test machine, the pytest will create a temporary database called *testseals*. Make sure this database does not already exist.

## Docs

Full documentation including the API reference and database schema are available at [https://OniDaito.github.io/sealhits/](https://OniDaito.github.io/sealhits/).

Documentation is built using the program [mkdocs](https://www.mkdocs.org/). It should be installed as part of the python requirements. The following commands are handy:

* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.

## Useful resources

Some useful resources for this particular project:

* [FITS handling with Astropy](https://docs.astropy.org/en/stable/io/fits/index.html)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/20/index.html)
* [Read the Docs with MkDocs](https://docs.readthedocs.io/en/stable/intro/getting-started-with-mkdocs.html)
* [MkDocs](https://www.mkdocs.org/)
  