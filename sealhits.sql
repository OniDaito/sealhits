--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: sealhits; Type: DATABASE; Schema: -; Owner: sealhits
--

CREATE DATABASE sealhits WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C.UTF-8';


ALTER DATABASE sealhits OWNER TO sealhits;

\connect sealhits

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: diesel_manage_updated_at(regclass); Type: FUNCTION; Schema: public; Owner: sealhits
--

CREATE FUNCTION public.diesel_manage_updated_at(_tbl regclass) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    EXECUTE format('CREATE TRIGGER set_updated_at BEFORE UPDATE ON %s
                    FOR EACH ROW EXECUTE PROCEDURE diesel_set_updated_at()', _tbl);
END;
$$;


ALTER FUNCTION public.diesel_manage_updated_at(_tbl regclass) OWNER TO sealhits;

--
-- Name: diesel_set_updated_at(); Type: FUNCTION; Schema: public; Owner: sealhits
--

CREATE FUNCTION public.diesel_set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF (
        NEW IS DISTINCT FROM OLD AND
        NEW.updated_at IS NOT DISTINCT FROM OLD.updated_at
    ) THEN
        NEW.updated_at := current_timestamp;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.diesel_set_updated_at() OWNER TO sealhits;

--
-- Name: seal_clean(); Type: FUNCTION; Schema: public; Owner: sealhits
--

CREATE FUNCTION public.seal_clean() RETURNS integer
    LANGUAGE plpgsql
    AS $$
declare
	total integer;
BEGIN
 	select count(*) into total from groups where comment is null or code is null;
	update groups set comment = 'None' where comment is null;
	update groups set code = 'None' where code is null;
	return total;
END;
$$;


ALTER FUNCTION public.seal_clean() OWNER TO sealhits;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: __diesel_schema_migrations; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.__diesel_schema_migrations (
    version character varying(50) NOT NULL,
    run_on timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.__diesel_schema_migrations OWNER TO sealhits;

--
-- Name: glfs; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.glfs (
    filename character varying NOT NULL,
    startdate timestamp with time zone NOT NULL,
    enddate timestamp with time zone NOT NULL,
    uid uuid NOT NULL
);


ALTER TABLE public.glfs OWNER TO sealhits;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.groups (
    gid bigint NOT NULL,
    timestart timestamp with time zone NOT NULL,
    interact boolean DEFAULT false NOT NULL,
    mammal integer NOT NULL,
    fish integer NOT NULL,
    bird integer NOT NULL,
    sqlite character varying NOT NULL,
    uid uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    comment text,
    timeend timestamp with time zone NOT NULL,
    sqliteid bigint NOT NULL,
    split integer DEFAULT 0 NOT NULL,
    huid character varying DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.groups OWNER TO sealhits;

--
-- Name: groups_glfs; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.groups_glfs (
    glf_id uuid NOT NULL,
    group_id uuid NOT NULL
);


ALTER TABLE public.groups_glfs OWNER TO sealhits;

--
-- Name: groups_images; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.groups_images (
    image_id uuid NOT NULL,
    group_id uuid NOT NULL
);


ALTER TABLE public.groups_images OWNER TO sealhits;

--
-- Name: groups_pgdfs; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.groups_pgdfs (
    pgdf_id uuid NOT NULL,
    group_id uuid NOT NULL
);


ALTER TABLE public.groups_pgdfs OWNER TO sealhits;

--
-- Name: images; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.images (
    filename character varying NOT NULL,
    uid uuid NOT NULL,
    hastrack boolean DEFAULT false NOT NULL,
    glf character varying NOT NULL,
    "time" timestamp with time zone NOT NULL,
    sonarid integer NOT NULL,
    range double precision DEFAULT 55 NOT NULL
);


ALTER TABLE public.images OWNER TO sealhits;

--
-- Name: pgdfs; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.pgdfs (
    filename character varying NOT NULL,
    startdate timestamp with time zone NOT NULL,
    enddate timestamp with time zone NOT NULL,
    uid uuid NOT NULL
);


ALTER TABLE public.pgdfs OWNER TO sealhits;

--
-- Name: points; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.points (
    "time" timestamp with time zone NOT NULL,
    sonarid integer NOT NULL,
    minbearing real NOT NULL,
    maxbearing real NOT NULL,
    minrange real NOT NULL,
    maxrange real NOT NULL,
    peakbearing real NOT NULL,
    peakrange real NOT NULL,
    maxvalue real NOT NULL,
    occupancy real NOT NULL,
    objsize real NOT NULL,
    track_id uuid NOT NULL,
    uid uuid DEFAULT gen_random_uuid() NOT NULL,
    group_id uuid NOT NULL
);


ALTER TABLE public.points OWNER TO sealhits;

--
-- Name: tracks_groups; Type: TABLE; Schema: public; Owner: sealhits
--

CREATE TABLE public.tracks_groups (
    track_pam_id bigint NOT NULL,
    group_id uuid NOT NULL,
    binfile character varying NOT NULL,
    track_id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.tracks_groups OWNER TO sealhits;

--
-- Name: __diesel_schema_migrations __diesel_schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.__diesel_schema_migrations
    ADD CONSTRAINT __diesel_schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: glfs glfs_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.glfs
    ADD CONSTRAINT glfs_pk PRIMARY KEY (uid);


--
-- Name: glfs glfs_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.glfs
    ADD CONSTRAINT glfs_un UNIQUE (filename);


--
-- Name: groups_glfs groups_glfs_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_glfs
    ADD CONSTRAINT groups_glfs_pk PRIMARY KEY (glf_id, group_id);


--
-- Name: groups_images groups_images_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_images
    ADD CONSTRAINT groups_images_pk PRIMARY KEY (image_id, group_id);


--
-- Name: groups_pgdfs groups_pgdfs_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_pgdfs
    ADD CONSTRAINT groups_pgdfs_pk PRIMARY KEY (pgdf_id, group_id);


--
-- Name: groups groups_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pk PRIMARY KEY (uid);


--
-- Name: groups groups_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_un UNIQUE (gid, sqliteid, split, sqlite);


--
-- Name: images images_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pk PRIMARY KEY (uid);


--
-- Name: images images_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_un UNIQUE (filename);


--
-- Name: pgdfs pgdfs_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.pgdfs
    ADD CONSTRAINT pgdfs_pk PRIMARY KEY (uid);


--
-- Name: pgdfs pgdfs_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.pgdfs
    ADD CONSTRAINT pgdfs_un UNIQUE (filename);


--
-- Name: points points_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.points
    ADD CONSTRAINT points_pk PRIMARY KEY (uid);


--
-- Name: points points_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.points
    ADD CONSTRAINT points_un UNIQUE ("time", sonarid, minbearing, maxbearing, minrange, maxrange, peakbearing, maxvalue, occupancy, objsize, track_id);


--
-- Name: tracks_groups tracks_groups_pk; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.tracks_groups
    ADD CONSTRAINT tracks_groups_pk PRIMARY KEY (track_id);


--
-- Name: tracks_groups tracks_groups_un; Type: CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.tracks_groups
    ADD CONSTRAINT tracks_groups_un UNIQUE (track_pam_id, binfile);


--
-- Name: glfs_filename_idx; Type: INDEX; Schema: public; Owner: sealhits
--

CREATE INDEX glfs_filename_idx ON public.glfs USING btree (filename);


--
-- Name: groups_huid_idx; Type: INDEX; Schema: public; Owner: sealhits
--

CREATE INDEX groups_huid_idx ON public.groups USING btree (huid);


--
-- Name: images_time_idx; Type: INDEX; Schema: public; Owner: sealhits
--

CREATE INDEX images_time_idx ON public.images USING btree ("time");


--
-- Name: pgdfs_filename_idx; Type: INDEX; Schema: public; Owner: sealhits
--

CREATE INDEX pgdfs_filename_idx ON public.pgdfs USING btree (filename);


--
-- Name: points_group_id_idx; Type: INDEX; Schema: public; Owner: sealhits
--

CREATE INDEX points_group_id_idx ON public.points USING btree (group_id);


--
-- Name: groups_glfs groups_glfs_fk; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_glfs
    ADD CONSTRAINT groups_glfs_fk FOREIGN KEY (group_id) REFERENCES public.groups(uid);


--
-- Name: groups_glfs groups_glfs_fk1; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_glfs
    ADD CONSTRAINT groups_glfs_fk1 FOREIGN KEY (glf_id) REFERENCES public.glfs(uid);


--
-- Name: groups_images groups_images_fk; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_images
    ADD CONSTRAINT groups_images_fk FOREIGN KEY (group_id) REFERENCES public.groups(uid);


--
-- Name: groups_images groups_images_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_images
    ADD CONSTRAINT groups_images_fk_1 FOREIGN KEY (image_id) REFERENCES public.images(uid);


--
-- Name: groups_pgdfs groups_pgdfs_fk; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_pgdfs
    ADD CONSTRAINT groups_pgdfs_fk FOREIGN KEY (group_id) REFERENCES public.groups(uid);


--
-- Name: groups_pgdfs groups_pgdfs_fk1; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.groups_pgdfs
    ADD CONSTRAINT groups_pgdfs_fk1 FOREIGN KEY (pgdf_id) REFERENCES public.pgdfs(uid);


--
-- Name: points points_fk_groups; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.points
    ADD CONSTRAINT points_fk_groups FOREIGN KEY (group_id) REFERENCES public.groups(uid);


--
-- Name: points points_fk_track; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.points
    ADD CONSTRAINT points_fk_track FOREIGN KEY (track_id) REFERENCES public.tracks_groups(track_id);


--
-- Name: tracks_groups tracks_groups_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: sealhits
--

ALTER TABLE ONLY public.tracks_groups
    ADD CONSTRAINT tracks_groups_fk_1 FOREIGN KEY (group_id) REFERENCES public.groups(uid);


--
-- PostgreSQL database dump complete
--

