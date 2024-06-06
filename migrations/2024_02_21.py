"""Postgresql Migration Script on the 2024-02-21. 
The main goal is to replace bigint on the PGDF and
GLF tables with UUID, consistent with the other
tables.

Process involves creation of a new table, copying
and checking the foreign keys, deletion of the old
table, then a renaming.

"""
from __future__ import annotations

import sys
import uuid
from sqlalchemy import create_engine, text

sys.path.append("../")


def migrate():
    """Perform the migration. We can't do this via an ORM sadly, so its
    raw SQL time. We can at least rollback I think."""
    username = "sealhits"
    password = "kissfromarose"
    host = "localhost"
    db_name = "sealhits"
    echo = True

    con_str = (
        "postgresql+psycopg2://"
        + username
        + ":"
        + password
        + "@"
        + host
        + "/"
        + db_name
    )
    engine = create_engine(con_str, echo=echo)

    # Do the rename of the tables concerned, and their constraints
    with engine.connect() as con:
        con.execute(text("ALTER TABLE glfs RENAME TO glfs_old;"))
        con.execute(text("ALTER TABLE glfs_pk RENAME TO glfs_pk_old;"))
        con.execute(
            text("ALTER TABLE glfs_filename_idx RENAME TO glfs_filename_idx_old;")
        )
        con.execute(text("ALTER TABLE glfs_un RENAME TO glfs_un_old;"))

        con.execute(text("ALTER TABLE pgdfs RENAME TO pgdfs_old;"))
        con.execute(text("ALTER TABLE pgdfs_pk RENAME TO pgdfs_pk_old;"))
        con.execute(
            text("ALTER TABLE pgdfs_filename_idx RENAME TO pgdfs_filename_idx_old;")
        )
        con.execute(text("ALTER TABLE pgdfs_un RENAME TO pgdfs_un_old;"))

        con.execute(text("ALTER TABLE groups_glfs RENAME TO groups_glfs_old;"))
        con.execute(text("ALTER TABLE groups_glfs_pk RENAME TO groups_glfs_pk_old;"))
        con.execute(
            text(
                "ALTER TABLE groups_glfs_old RENAME CONSTRAINT groups_glfs_fk TO groups_glfs_fk_old;"
            )
        )
        con.execute(
            text(
                "ALTER TABLE groups_glfs_old RENAME CONSTRAINT groups_glfs_fk1 TO groups_glfs_fk1_old;"
            )
        )

        con.execute(text("ALTER TABLE groups_pgdfs RENAME TO groups_pgdfs_old;"))
        con.execute(text("ALTER TABLE groups_pgdfs_pk RENAME TO groups_pgdfs_pk_old;"))
        con.execute(
            text(
                "ALTER TABLE groups_pgdfs_old RENAME CONSTRAINT groups_pgdfs_fk TO groups_pgdfs_fk_old;"
            )
        )
        con.execute(
            text(
                "ALTER TABLE groups_pgdfs_old RENAME CONSTRAINT groups_pgdfs_fk1 TO groups_pgdfs_fk1_old;"
            )
        )

        con.commit()

    try:
        with engine.begin() as con:
            # Now, try to create the four new tables
            create_glfs = """CREATE TABLE public.glfs (
                filename character varying NOT NULL,
                startdate timestamp with time zone NOT NULL,
                enddate timestamp with time zone NOT NULL,
                uid uuid NOT NULL
            );
            
            ALTER TABLE public.glfs OWNER TO sealhits;
            ALTER TABLE ONLY public.glfs
            ADD CONSTRAINT glfs_pk PRIMARY KEY (uid);
            ALTER TABLE ONLY public.glfs ADD CONSTRAINT glfs_un UNIQUE (filename);
            CREATE INDEX glfs_filename_idx ON public.glfs USING btree (filename);"""

            result = con.execute(text(create_glfs))

            create_pgdfs = """
                CREATE TABLE public.pgdfs (
                    filename character varying NOT NULL,
                    startdate timestamp with time zone NOT NULL,
                    enddate timestamp with time zone NOT NULL,
                    uid uuid NOT NULL
                );
                ALTER TABLE public.pgdfs OWNER TO sealhits;
                ALTER TABLE ONLY public.pgdfs ADD CONSTRAINT pgdfs_pk PRIMARY KEY (uid);
                ALTER TABLE ONLY public.pgdfs ADD CONSTRAINT pgdfs_un UNIQUE (filename);
                CREATE INDEX pgdfs_filename_idx ON public.pgdfs USING btree (filename);
                """

            result = con.execute(text(create_pgdfs))

            create_groups_pgdfs = """
                CREATE TABLE public.groups_pgdfs (
                    pgdf_id uuid NOT NULL,
                    group_id uuid NOT NULL
                );
                ALTER TABLE public.groups_pgdfs OWNER TO sealhits;
                ALTER TABLE ONLY public.groups_pgdfs ADD CONSTRAINT groups_pgdfs_pk PRIMARY KEY (pgdf_id, group_id);
                ALTER TABLE ONLY public.groups_pgdfs ADD CONSTRAINT groups_pgdfs_fk FOREIGN KEY (group_id) REFERENCES public.groups(uid);
                ALTER TABLE ONLY public.groups_pgdfs ADD CONSTRAINT groups_pgdfs_fk1 FOREIGN KEY (pgdf_id) REFERENCES public.pgdfs(uid);

            """

            result = con.execute(text(create_groups_pgdfs))

            create_groups_glfs = """
                CREATE TABLE public.groups_glfs (
                    glf_id uuid NOT NULL,
                    group_id uuid NOT NULL
                );
                ALTER TABLE public.groups_glfs OWNER TO sealhits;
                ALTER TABLE ONLY public.groups_glfs ADD CONSTRAINT groups_glfs_pk PRIMARY KEY (glf_id, group_id);
                ALTER TABLE ONLY public.groups_glfs ADD CONSTRAINT groups_glfs_fk FOREIGN KEY (group_id) REFERENCES public.groups(uid);
                ALTER TABLE ONLY public.groups_glfs ADD CONSTRAINT groups_glfs_fk1 FOREIGN KEY (glf_id) REFERENCES public.glfs(uid);
            """

            result = con.execute(text(create_groups_glfs))

            # Now we have new tables, go through GLFS and PGDFs, recreating the tables, adding new UIDS
            # and storing the connections in memory.
            groups_glfs = {}
            groups_pgdfs = {}

            result = con.execute(text("select * from glfs_old"))

            for gfile, gstart, gend, guid in result:
                newuid = uuid.uuid4()
                con.execute(
                    text(
                        "INSERT INTO glfs (filename, startdate, enddate, uid) VALUES (:filename, :startdate, :enddate, :uid)"
                    ),
                    [
                        {
                            "filename": gfile,
                            "startdate": gstart,
                            "enddate": gend,
                            "uid": newuid,
                        }
                    ],
                )

                groups_glfs[guid] = newuid

            result = con.execute(text("select * from pgdfs_old"))

            for gfile, gstart, gend, guid in result:
                newuid = uuid.uuid4()
                con.execute(
                    text(
                        "INSERT INTO pgdfs (filename, startdate, enddate, uid) VALUES (:filename, :startdate, :enddate, :uid)"
                    ),
                    [
                        {
                            "filename": gfile,
                            "startdate": gstart,
                            "enddate": gend,
                            "uid": newuid,
                        }
                    ],
                )

                groups_pgdfs[guid] = newuid

            # Finally, look at the dictionaries and recreate the relationship tables
            result = con.execute(text("select * from groups_glfs_old"))

            for gglf_id, ggroup_id in result:
                con.execute(
                    text(
                        "INSERT INTO groups_glfs (glf_id, group_id) VALUES (:glf_id, :group_id)"
                    ),
                    [{"glf_id": groups_glfs[gglf_id], "group_id": ggroup_id}],
                )

            result = con.execute(text("select * from groups_pgdfs_old"))

            for gpgdf_id, ggroup_id in result:
                con.execute(
                    text(
                        "INSERT INTO groups_pgdfs (pgdf_id, group_id) VALUES (:pgdf_id, :group_id)"
                    ),
                    [{"pgdf_id": groups_pgdfs[gpgdf_id], "group_id": ggroup_id}],
                )

            # Now delete the old tables if we've gotten this far
            # Order dependent thanks to constraints
            con.execute(text("DROP TABLE groups_glfs_old;"))
            con.execute(text("DROP TABLE groups_pgdfs_old;"))
            con.execute(text("DROP TABLE glfs_old;"))
            con.execute(text("DROP TABLE pgdfs_old;"))

            # By this stage, we should be complete

            con.commit()

    except Exception as e:
        print(e)

        # Put the tables back
        with engine.connect() as con:
            con.execute(text("ALTER TABLE glfs_old RENAME TO glfs;"))
            con.execute(text("ALTER TABLE glfs_pk_old RENAME TO glfs_pk;"))
            con.execute(
                text("ALTER TABLE glfs_filename_idx_old RENAME TO glfs_filename_idx;")
            )
            con.execute(text("ALTER TABLE glfs_un_old RENAME TO glfs_un;"))

            con.execute(text("ALTER TABLE pgdfs_old RENAME TO pgdfs;"))
            con.execute(text("ALTER TABLE pgdfs_pk_old RENAME TO pgdfs_pk;"))
            con.execute(
                text("ALTER TABLE pgdfs_filename_idx_old RENAME TO pgdfs_filename_idx;")
            )
            con.execute(text("ALTER TABLE pgdfs_un_old RENAME TO pgdfs_un;"))

            con.execute(text("ALTER TABLE groups_glfs_old RENAME TO groups_glfs;"))
            con.execute(
                text("ALTER TABLE groups_glfs_pk_old RENAME TO groups_glfs_pk;")
            )
            con.execute(
                text(
                    "ALTER TABLE groups_glfs RENAME CONSTRAINT groups_glfs_fk_old TO groups_glfs_fk;"
                )
            )
            con.execute(
                text(
                    "ALTER TABLE groups_glfs RENAME CONSTRAINT groups_glfs_fk1_old TO groups_glfs_fk1;"
                )
            )

            con.execute(text("ALTER TABLE groups_pgdfs_old RENAME TO groups_pgdfs;"))
            con.execute(
                text("ALTER TABLE groups_pgdfs_pk_old RENAME TO groups_pgdfs_pk;")
            )
            con.execute(
                text(
                    "ALTER TABLE groups_pgdfs RENAME CONSTRAINT groups_pgdfs_fk_old TO groups_pgdfs_fk;"
                )
            )
            con.execute(
                text(
                    "ALTER TABLE groups_pgdfs RENAME CONSTRAINT groups_pgdfs_fk1_old TO groups_pgdfs_fk1;"
                )
            )

            con.commit()


if __name__ == "__main__":
    migrate()
