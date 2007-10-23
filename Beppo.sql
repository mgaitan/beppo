SET client_encoding = 'UNICODE';
SET check_function_bodies = false;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;

SET search_path = public, pg_catalog;

CREATE TABLE person (
    username character varying(80) NOT NULL,
    id integer DEFAULT nextval('pk_seq_person'::text) NOT NULL,
    "password" character varying(255) NOT NULL,
    kind integer NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    "language" integer,
    fk_timezone integer,
    demo bool NOT NULL DEFAULT false
);

CREATE TABLE tutor (
    id integer NOT NULL,
    address1 character varying(255),
    address2 character varying(255),
    zip character varying(80),
    phone1 character varying(255),
    phone2 character varying(255),
    phone3 character varying(255),
    icq character varying(255),
    msn character varying(255),
    aol character varying(255)
);

CREATE TABLE subject (
    id integer DEFAULT nextval('subject_id_seq'::text) NOT NULL,
    name character varying(255)
);


CREATE TABLE tutor_subject (
    id integer DEFAULT nextval('pk_seq_tutor_subject'::text) NOT NULL,
    fk_tutor integer,
    fk_subject integer
);

CREATE SEQUENCE pk_seq_tutor_subject
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

CREATE SEQUENCE pk_seq_person
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

CREATE TABLE client (
    id serial NOT NULL,
    organization character varying(255),
    ai_available numeric(14,6) DEFAULT 0 NOT NULL,
    pc_available numeric(14,6) DEFAULT 0 NOT NULL
);

CREATE TABLE tutor_schedule (
    id serial NOT NULL,
    fk_tutor integer,
    time_start timestamp without time zone NOT NULL,
    time_end timestamp without time zone NOT NULL,
    schedule_type integer NOT NULL
);

CREATE TABLE pupil (
    id integer NOT NULL,
    fk_client integer NOT NULL,
    expires timestamp without time zone NOT NULL,
    ai_total numeric(14,6) DEFAULT 0 NOT NULL,
    ai_available numeric(14,6) DEFAULT 0 NOT NULL,
    pc_available numeric(14,6) DEFAULT 0 NOT NULL,
    pc_total numeric(14,6) DEFAULT 0 NOT NULL
);

CREATE TABLE "session" (
    id serial NOT NULL,
    fk_tutor integer NOT NULL,
    fk_pupil integer,
    session_type integer,
    time_start timestamp without time zone,
    time_end timestamp without time zone,
    error_code integer
);

CREATE SEQUENCE subject_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

CREATE FUNCTION dmin(timestamp without time zone, timestamp without time zone) RETURNS timestamp without time zone
    AS 'select case when $1 < $2 then $1 else $2 end;'
    LANGUAGE sql IMMUTABLE;


CREATE FUNCTION dmax(timestamp without time zone, timestamp without time zone) RETURNS timestamp without time zone
    AS 'select case when $1 > $2 then $1 else $2 end;'
    LANGUAGE sql IMMUTABLE;


CREATE TABLE timezone (
    id serial NOT NULL,
    name character varying(50),
    gmtoffset integer
);

CREATE TABLE prearranged_classes (
    id serial NOT NULL,
    fk_tutor integer,
    fk_pupil integer,
    time_start timestamp without time zone,
    time_end timestamp without time zone,
    fk_subject integer
);

CREATE TABLE offline_questions (
    id serial NOT NULL,
    fk_pupil integer,
    fk_subject integer,
    time_submit timestamp without time zone,
    status text
);

CREATE TABLE pre_archive (
    id serial NOT NULL,
    fk_session integer,
    status text,
    "comment" character varying(1024)
);


CREATE TABLE archive (
    id serial NOT NULL,
    filename character varying(1024),
    fk_session integer,
    "comment" character varying(1024)
);

CREATE TABLE "language" (
    id serial NOT NULL,
    name character varying(255) NOT NULL,
    locale character varying(255) NOT NULL
);

COPY person (username, "password", id, kind, first_name, last_name, email, "language", fk_timezone) FROM stdin;
Admin	d033e22ae348aeb5660fc2140aec35850c4da997	1	3	System	Administrator	root@mybeppo.com	1	1
\.


COPY tutor (id, address1, address2, zip, phone1, phone2, phone3, icq, msn, aol) FROM stdin;
\.


COPY subject (id, name) FROM stdin;
\.


COPY tutor_subject (id, fk_tutor, fk_subject) FROM stdin;
\.


COPY client (id, organization, ai_available, pc_available) FROM stdin;
\.


COPY tutor_schedule (id, fk_tutor, time_start, time_end, schedule_type) FROM stdin;
\.


COPY pupil (id, fk_client, expires, ai_total, ai_available, pc_available, pc_total) FROM stdin;
\.


COPY "session" (id, fk_tutor, fk_pupil, session_type, time_start, time_end, error_code) FROM stdin;
\.


COPY timezone (id, name, gmtoffset) FROM stdin;
1	Argentina	-3
2	España	1
\.

COPY prearranged_classes (id, fk_tutor, fk_pupil, time_start, time_end, fk_subject) FROM stdin;
\.


COPY offline_questions (id, fk_pupil, fk_subject, time_submit, status) FROM stdin;
\.

COPY pre_archive (id, fk_session, status, "comment") FROM stdin;
\.


COPY archive (id, filename, fk_session, "comment") FROM stdin;
\.

COPY "language" (id, name, locale) FROM stdin;
1	Español (Argentina)	es_AR
2	English (American)	en_US
3	Español (España)	es_ES
\.


ALTER TABLE ONLY person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);
ALTER TABLE ONLY tutor
    ADD CONSTRAINT tutor_pkey PRIMARY KEY (id);
ALTER TABLE ONLY subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (id);
ALTER TABLE ONLY tutor_subject
    ADD CONSTRAINT tutor_subject_pkey PRIMARY KEY (id);
ALTER TABLE ONLY client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);
ALTER TABLE ONLY pupil
    ADD CONSTRAINT pupil_pkey PRIMARY KEY (id);
ALTER TABLE ONLY "session"
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);
ALTER TABLE ONLY timezone
    ADD CONSTRAINT timezone_pkey PRIMARY KEY (id);
ALTER TABLE ONLY person
    ADD CONSTRAINT unique_username UNIQUE (username);
ALTER TABLE ONLY "language"
    ADD CONSTRAINT language_pkey PRIMARY KEY (id);
ALTER TABLE ONLY offline_questions
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_pupil) REFERENCES pupil(id) ON DELETE RESTRICT;
ALTER TABLE ONLY offline_questions
    ADD CONSTRAINT "$2" FOREIGN KEY (fk_subject) REFERENCES subject(id) ON DELETE RESTRICT;
ALTER TABLE ONLY pre_archive
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_session) REFERENCES "session"(id) ON DELETE RESTRICT;
ALTER TABLE ONLY archive
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_session) REFERENCES "session"(id) ON DELETE RESTRICT;
ALTER TABLE ONLY tutor_subject
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_tutor) REFERENCES tutor(id) ON DELETE RESTRICT;
ALTER TABLE ONLY tutor_subject
    ADD CONSTRAINT "$2" FOREIGN KEY (fk_subject) REFERENCES subject(id) ON DELETE CASCADE;
ALTER TABLE ONLY tutor
    ADD CONSTRAINT tutor_id FOREIGN KEY (id) REFERENCES person(id) ON DELETE RESTRICT;
ALTER TABLE ONLY client
    ADD CONSTRAINT client_id FOREIGN KEY (id) REFERENCES person(id) ON DELETE RESTRICT;
ALTER TABLE ONLY tutor_schedule
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_tutor) REFERENCES tutor(id) ON DELETE RESTRICT;
ALTER TABLE ONLY "session"
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_tutor) REFERENCES tutor(id) ON DELETE RESTRICT;
ALTER TABLE ONLY "session"
    ADD CONSTRAINT "$2" FOREIGN KEY (fk_pupil) REFERENCES pupil(id) ON DELETE RESTRICT;
ALTER TABLE ONLY pupil
    ADD CONSTRAINT "$2" FOREIGN KEY (fk_client) REFERENCES client(id) ON DELETE RESTRICT;
ALTER TABLE ONLY person
    ADD CONSTRAINT timezone_id FOREIGN KEY (fk_timezone) REFERENCES timezone(id) ON DELETE RESTRICT;
ALTER TABLE ONLY prearranged_classes
    ADD CONSTRAINT "$1" FOREIGN KEY (fk_tutor) REFERENCES tutor(id) ON DELETE RESTRICT;
ALTER TABLE ONLY prearranged_classes
    ADD CONSTRAINT "$2" FOREIGN KEY (fk_pupil) REFERENCES pupil(id) ON DELETE RESTRICT;
ALTER TABLE ONLY prearranged_classes
    ADD CONSTRAINT "$3" FOREIGN KEY (fk_subject) REFERENCES subject(id) ON DELETE RESTRICT;
ALTER TABLE ONLY person
    ADD CONSTRAINT "$3" FOREIGN KEY ("language") REFERENCES "language"(id) ON DELETE RESTRICT;

SELECT pg_catalog.setval('pk_seq_tutor_subject', 1, true);
SELECT pg_catalog.setval('pk_seq_person', 2, true);
SELECT pg_catalog.setval('client_id_seq', 1, false);
SELECT pg_catalog.setval('tutor_schedule_id_seq', 1, true);
SELECT pg_catalog.setval('session_id_seq', 1, true);
SELECT pg_catalog.setval('subject_id_seq', 1, true);
SELECT pg_catalog.setval('timezone_id_seq', 1, false);
SELECT pg_catalog.setval('prearranged_classes_id_seq', 1, false);
SELECT pg_catalog.setval('offline_questions_id_seq', 1, true);
SELECT pg_catalog.setval('pre_archive_id_seq', 1, true);
SELECT pg_catalog.setval('archive_id_seq', 1, false);
SELECT pg_catalog.setval('language_id_seq', 1, true);

COMMENT ON SCHEMA public IS 'Standard public schema';
