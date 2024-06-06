"""
dbschema.py - The Postgresql schema.
author: Benjamin Blundell (bjb8@st-andrews.ac.uk)

The Postgresql Database Schema.
We use SQLAlchemy as the ORM to wrap the various postgresql.
"""

from __future__ import annotations

__all__ = [
    "Points",
    "Groups",
    "Images",
    "GLFS",
    "PGDFS",
    "TrackGroup",
]
__version__ = "0.7.0"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"

import datetime
from typing import List

from sqlalchemy import (
    ForeignKey,
    Table,
    Column,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.dialects.postgresql import UUID

# Declare our ORM here with the PostgreSQL classes
# TODO session.query might be legacy. Might need to redo it: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-20-query-usage

class Base(DeclarativeBase):
    pass

groups_images = Table(
    "groups_images",
    Base.metadata,
    Column("group_id", ForeignKey("groups.uid"), primary_key=True),
    Column("image_id", ForeignKey("images.uid"), primary_key=True),
)

groups_glfs = Table(
    "groups_glfs",
    Base.metadata,
    Column("glf_id", ForeignKey("glfs.uid"), primary_key=True),
    Column("group_id", ForeignKey("groups.uid"), primary_key=True),
)

groups_pgdfs = Table(
    "groups_pgdfs",
    Base.metadata,
    Column("pgdf_id", ForeignKey("pgdfs.uid"), primary_key=True),
    Column("group_id", ForeignKey("groups.uid"), primary_key=True),
)

class Points(Base):
    __tablename__ = "points"
    uid = Column(UUID(as_uuid=True), primary_key=True)
    time: Mapped[datetime.datetime]
    sonarid: Mapped[int]
    minbearing: Mapped[float]
    maxbearing: Mapped[float]
    minrange: Mapped[float]
    maxrange: Mapped[float]
    peakbearing: Mapped[float]
    peakrange: Mapped[float]
    maxvalue: Mapped[float]
    occupancy: Mapped[float]
    objsize: Mapped[float]
    track_id: Mapped[UUID] = mapped_column(ForeignKey("tracks_groups.track_id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.uid"))

    def __repr__(self) -> str:
        return f"Points(uid={self.uid!r}, time={self.time!r}, \
        sonarid={self.sonarid!r}, minbearing={self.minbearing}, maxbearing={self.maxbearing},\
        minrange={self.minrange}, maxrange={self.maxrange}, track={self.track_id}, group_id={self.group_id})"


class Groups(Base):
    __tablename__ = "groups"

    uid = Column(UUID(as_uuid=True), primary_key=True)
    gid: Mapped[int]
    sqliteid: Mapped[int]
    timestart: Mapped[datetime.datetime]
    timeend: Mapped[datetime.datetime]
    sqlite: Mapped[str]
    code: Mapped[str]
    comment: Mapped[str]
    interact: Mapped[bool]
    mammal: Mapped[int]
    fish: Mapped[int]
    bird: Mapped[int]
    split: Mapped[int]
    huid: Mapped[str]

    # TODO - could we add tracksgroups here too?
    images: Mapped[List[Images]] = relationship(
        secondary=groups_images, back_populates="groups"
    )
    glfs: Mapped[List[GLFS]] = relationship(
        secondary=groups_glfs, back_populates="groups"
    )
    pgdfs: Mapped[List[PGDFS]] = relationship(
        secondary=groups_pgdfs, back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"Groups(uid={self.uid!r}, timestart={self.timestart!r}, \
        timeend={self.timeend!r}, interact={self.interact}, mammal={self.mammal},\
        fish={self.fish}, bird={self.bird})"


class Images(Base):
    __tablename__ = "images"

    uid = Column(UUID(as_uuid=True), primary_key=True)
    filename: Mapped[str]
    hastrack: Mapped[bool]
    glf: Mapped[str]
    time: Mapped[datetime.datetime]
    sonarid: Mapped[int]
    range: Mapped[float]
    groups: Mapped[List[Groups]] = relationship(
        secondary=groups_images, back_populates="images"
    )

    def __repr__(self) -> str:
        return f"Images(uid={self.uid!r}, filename={self.filename!r}, \
        hastrack={self.hastrack!r}, glf={self.glf}, time={self.time},\
        sonarid={self.sonarid})"


class GLFS(Base):
    __tablename__ = "glfs"

    uid = Column(UUID(as_uuid=True), primary_key=True)
    filename: Mapped[str]
    startdate: Mapped[datetime.datetime]
    enddate: Mapped[datetime.datetime]

    groups: Mapped[List[Groups]] = relationship(
        secondary=groups_glfs, back_populates="glfs"
    )

    def __repr__(self) -> str:
        return f"GLFS(uid={self.uid!r}, filename={self.filename!r}, \
        startdate={self.startdate!r}, enddate={self.enddate})"


class PGDFS(Base):
    __tablename__ = "pgdfs"

    uid = Column(UUID(as_uuid=True), primary_key=True)
    filename: Mapped[str]
    startdate: Mapped[datetime.datetime]
    enddate: Mapped[datetime.datetime]

    groups: Mapped[List[Groups]] = relationship(
        secondary=groups_pgdfs, back_populates="pgdfs"
    )

    def __repr__(self) -> str:
        return f"PGDFS(uid={self.uid!r}, filename={self.filename!r}, \
        startdate={self.startdate!r}, enddate={self.enddate})"


class TrackGroup(Base):
    """Represents the tracks that are part of this group.
    We use our own UUID but the constraint is that track_id and
    binfile together must be unique."""

    __tablename__ = "tracks_groups"

    track_pam_id: Mapped[int]
    track_id = Column(UUID(as_uuid=True), primary_key=True)
    group_id = Column(
        UUID(as_uuid=True), ForeignKey(Groups.uid)
    )  # TODO - foreign relation here?
    binfile: Mapped[str]

    def __repr__(self) -> str:
        return f"TrackGroup(track_id={self.track_id!r}, group_id={self.group_id!r})"
