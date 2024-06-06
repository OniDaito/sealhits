# SealHits
This site contains the project documentation for the
`sealhits` project.

The project is named after the [rather famous compilation music album](https://en.wikipedia.org/wiki/Hits_(Seal_album)).

## Table Of Contents

1. [Explanation](explanation.md) - The overall explanation of what sealhits does.
2. [Tutorials](tutorials.md) - Some basic tutorials on how to use the various scripts inside sealhits.
3. [How-To Guides](how-to-guides.md) - Specific how-tos on various things.
4. [Reference](reference.md) - An API reference.
5. [The Sealhits Database](database.md) - The description of the Postgresql database behind it all.


## Requirements and Setup

Sealhits is written in Python and requires a number of additional libraries. These can be installed using pip. It is recommended to use a virtual environment as follows:

    python -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt

A [PostgreSQL](https://www.postgresql.org/) database setup is required to hold all the data. Most Linux distributions have an install candidate for Postgresql. Once installed, the database can be setup as follows:

First, create the user and the database (using psql or similar)

    create user sealhits with password 'kissfromarose' createdb login;
    create database sealhits owner sealhits;

Then, import the schema:

    psql -U sealhits sealhits < sealhits.sql


The documentation follows the best practice for
project documentation as described by Daniele Procida
in the [Diátaxis documentation framework](https://diataxis.fr/).
