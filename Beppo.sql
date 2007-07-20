SET client_encoding = 'UNICODE';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'postgres';

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;

SET SESSION AUTHORIZATION 'postgres';

SET search_path = public, pg_catalog;

CREATE TABLE person (
    username character varying(80) NOT NULL,
    "password" character varying(80) NOT NULL,
    id integer DEFAULT nextval('pk_seq_person'::text) NOT NULL,
    kind integer NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    "language" integer,
    fk_timezone integer
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


SET SESSION AUTHORIZATION 'waldo';

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


SET SESSION AUTHORIZATION 'postgres';

COPY person (username, "password", id, kind, first_name, last_name, email, "language", fk_timezone) FROM stdin;
Root	root	6	3	Sys	Admin	a@b.c	1	1
Matias	matias	5	1	Matias	Bordese	a@b.c	1	1
Mati	mati	2	2	Mati	Bor	a@b.c	1	1
Guest	guest	4	2	Invi	Tado	a@b.c	1	1
aaaaaaaaaaaaaaaa	a	45	1	a	a	a@b.c	1	1
ab	a	43	1	a	a	a@b.c	1	1
Tutor	tutor	10	1	Tutor	Bueno	a@b.c	1	1
Nestor	nestor	42	4	Nestorw	Gonzalez	a@b.c	1	1
b	b	44	1	b	b	a@b.c	1	1
lolo	l	55	1	l	l	a@b.c	1	1
Cli	cli	9	4	Cli	Bue	a@b.c	1	1
ForTestPupil1	f	66	2	For	TestPupil	ftp@client.com	2	2
ForTestPupil2	f	67	2	For	TestPupil	fortest@client.com	2	2
ForTestPupil3	f	68	2	For	TestPupil	fortest@client.com	2	2
Cliente	cliente	8	4	Cliente	Bueno	a@b.c	1	1
Waldo	waldo	1	2	Walter	Alini	a@b.c	2	2
Achuni	achuni	3	1	Anthony	Lenton	a@b.c	1	1
ForTest	f	65	4	For	Test	fortest@client.com	2	2
\.


COPY tutor (id, address1, address2, zip, phone1, phone2, phone3, icq, msn, aol) FROM stdin;
5	Tupac Amaru 6877	\N	X5000HHJ	0351-4247244	\N	\N	\N	matias@hotmail.com	matias@uol.com
10	Tupac Amaru 6877			0351-4247244					
45	a	a	a	a	a	a	a	a	a
43	a	a	a	a	a	a	a	a	a
44	b		b	b	b	b	b	b	b
55	l	l	l	l	l	l	l	l	l
3	Av. Leopoldo Lugones 176		X5000GHN	0351-4584585				achuni@msn.com	
\.


COPY subject (id, name) FROM stdin;
1	Álgebra
2	Probabilidad y Estadística
3	Geometría Básica
4	Combinatorias
5	Matemática Básica
15	Psicología
\.


COPY tutor_subject (id, fk_tutor, fk_subject) FROM stdin;
36	5	5
43	3	1
44	3	4
45	10	2
46	10	3
47	10	4
\.


COPY client (id, organization, ai_available, pc_available) FROM stdin;
42	Nestitor	108.000000	0.000000
65	Client SRL	48.800000	29.400000
9	Clientes Buenos SA	90.500000	0.000000
8	Clientes Buenos SA	99.200000	0.000000
\.


COPY tutor_schedule (id, fk_tutor, time_start, time_end, schedule_type) FROM stdin;
194	5	2005-05-02 16:00:00	2005-05-02 19:00:00	1
195	5	2005-05-02 21:00:00	2005-05-02 23:00:00	1
196	5	2005-05-03 08:00:00	2005-05-03 12:00:00	1
197	5	2005-05-04 12:00:00	2005-05-04 13:00:00	1
198	5	2005-05-04 16:00:00	2005-05-04 18:00:00	1
199	5	2005-05-05 08:00:00	2005-05-05 12:00:00	1
200	5	2005-05-06 08:00:00	2005-05-06 12:00:00	1
185	10	2005-05-02 19:00:00	2005-05-02 20:00:00	1
186	10	2005-05-04 13:00:00	2005-05-04 16:00:00	1
236	3	2005-05-01 00:00:00	2005-05-08 00:00:00	1
\.


COPY pupil (id, fk_client, expires, ai_total, ai_available, pc_available, pc_total) FROM stdin;
66	65	2006-01-16 08:44:33.85	10.000000	10.000000	15.000000	15.000000
67	65	2006-01-16 08:44:57.85	10.000000	10.000000	15.000000	15.000000
68	65	2006-01-16 08:45:29.16	10.000000	10.000000	15.000000	15.000000
1	42	2006-01-16 08:44:33.85	0.000000	0.000000	0.000000	0.000000
2	42	2006-01-16 08:44:33.85	0.000000	0.000000	0.000000	0.000000
4	42	2006-01-16 08:44:33.85	0.000000	0.000000	0.000000	0.000000
\.


COPY "session" (id, fk_tutor, fk_pupil, session_type, time_start, time_end, error_code) FROM stdin;
239	3	\N	8	2005-10-05 17:10:19	2005-10-05 17:10:32	0
240	3	\N	5	2005-10-05 17:10:32	2005-10-05 17:10:37	0
241	3	\N	8	2005-10-05 17:10:37	2005-10-05 17:10:38	0
242	3	\N	5	2005-10-05 17:10:38	2005-10-05 17:10:54	0
243	3	4	1	2005-10-05 17:10:54	2005-10-05 17:11:02	0
244	3	\N	8	2005-10-03 17:10:37	2005-10-03 17:10:48	0
238	5	\N	8	2005-10-05 17:11:02	2005-10-06 15:14:16	99
245	45	\N	1	2005-10-05 17:10:19	2005-10-05 20:10:19	\N
233	5	\N	8	2005-10-05 17:10:19	2005-10-05 17:10:32	0
234	5	\N	5	2005-10-05 17:10:32	2005-10-05 17:10:37	0
235	5	\N	8	2005-10-05 17:10:37	2005-10-05 17:10:38	0
236	5	\N	5	2005-10-05 17:10:38	2005-10-05 17:10:54	0
237	5	4	1	2005-10-05 17:10:54	2005-10-05 17:11:02	0
250	10	\N	8	2005-11-02 14:52:15	2005-11-02 15:10:11	7
251	10	\N	8	2005-11-02 15:10:12	2005-11-02 15:51:47	7
252	10	\N	8	2005-11-02 15:51:48	2005-11-02 15:56:23	7
253	10	\N	8	2005-11-02 15:56:24	2005-11-02 16:00:00	1
254	5	\N	8	2005-11-02 15:58:00	2005-11-10 15:09:06	7
255	3	\N	8	2005-11-10 15:09:07	2005-11-10 15:16:01	7
256	3	\N	8	2005-11-10 15:16:02	2005-11-10 15:16:37	7
257	3	\N	8	2005-11-10 15:16:38	2005-11-10 15:17:14	7
258	3	\N	8	2005-11-10 15:17:14	2005-11-10 15:20:16	7
267	3	\N	8	2005-11-16 09:58:34	2005-11-16 11:18:43	7
259	3	\N	8	2005-11-10 15:20:16	2005-11-16 08:39:27	7
260	3	\N	8	2005-11-16 08:39:28	2005-11-16 08:51:01	7
261	3	\N	8	2005-11-16 08:51:02	2005-11-16 09:06:30	7
262	3	\N	8	2005-11-16 09:06:30	2005-11-16 09:10:15	7
263	3	\N	8	2005-11-16 09:10:15	2005-11-16 09:12:20	7
264	3	\N	8	2005-11-16 09:12:20	2005-11-16 09:49:27	7
265	3	\N	8	2005-11-16 09:49:27	2005-11-16 09:50:06	7
266	3	\N	8	2005-11-16 09:50:07	2005-11-16 09:58:33	7
268	3	\N	8	2005-11-16 11:18:44	2005-11-30 16:06:39	7
269	5	\N	8	2005-11-30 16:06:39	2005-11-30 16:22:15	7
270	3	\N	8	2005-11-30 16:06:40	2005-11-30 16:22:15	7
272	3	\N	8	2005-11-30 16:22:16	\N	\N
271	5	\N	8	2005-11-30 16:22:16	\N	\N
\.


COPY timezone (id, name, gmtoffset) FROM stdin;
1	Argentina	-3
2	España	1
\.

COPY prearranged_classes (id, fk_tutor, fk_pupil, time_start, time_end, fk_subject) FROM stdin;
\.


SET SESSION AUTHORIZATION 'waldo';

COPY offline_questions (id, fk_pupil, fk_subject, time_submit, status) FROM stdin;
6	2	4	2005-10-10 10:00:00	Convocado por la profesora
7	2	3	2005-10-10 10:00:00	Convocado por la profesora
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


SET SESSION AUTHORIZATION 'postgres';

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


SET SESSION AUTHORIZATION 'waldo';

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


SET SESSION AUTHORIZATION 'postgres';

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

SELECT pg_catalog.setval('pk_seq_tutor_subject', 47, true);


SELECT pg_catalog.setval('pk_seq_person', 81, true);


SELECT pg_catalog.setval('client_id_seq', 1, false);


SELECT pg_catalog.setval('tutor_schedule_id_seq', 236, true);

SELECT pg_catalog.setval('session_id_seq', 272, true);

SELECT pg_catalog.setval('subject_id_seq', 18, true);

SELECT pg_catalog.setval('timezone_id_seq', 3, false);

SELECT pg_catalog.setval('prearranged_classes_id_seq', 1, false);


SET SESSION AUTHORIZATION 'waldo';

SELECT pg_catalog.setval('offline_questions_id_seq', 7, true);

SELECT pg_catalog.setval('pre_archive_id_seq', 3, true);

SELECT pg_catalog.setval('archive_id_seq', 1, false);

SELECT pg_catalog.setval('language_id_seq', 3, true);


SET SESSION AUTHORIZATION 'postgres';

COMMENT ON SCHEMA public IS 'Standard public schema';

