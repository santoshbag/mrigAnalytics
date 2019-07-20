--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.5
-- Dumped by pg_dump version 9.6.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: MRIGWEB; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE "MRIGWEB" IS 'DJANGO WEBSERVICE';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_groups_id_seq OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_id_seq OWNER TO postgres;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_user_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE django_session OWNER TO postgres;

--
-- Name: mrigsession; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE mrigsession (
    sessionid text NOT NULL,
    sessionobj text NOT NULL,
    sessionexpiry numeric NOT NULL
);


ALTER TABLE mrigsession OWNER TO postgres;

--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can add permission	2	add_permission
5	Can change permission	2	change_permission
6	Can delete permission	2	delete_permission
7	Can add group	3	add_group
8	Can change group	3	change_group
9	Can delete group	3	delete_group
10	Can add user	4	add_user
11	Can change user	4	change_user
12	Can delete user	4	delete_user
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_permission_id_seq', 18, true);


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$100000$y3YKMaCOPFhd$hi9yqBbvtaoyF+7XbTQxDgJKIWaobo2by58QyOc5x/g=	2019-01-16 12:27:24.035605+05:30	t	santoshbag			santosh.bag@gmail.com	t	t	2019-01-16 12:27:05.178625+05:30
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_id_seq', 1, true);


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_content_type_id_seq', 6, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2019-01-16 12:13:03.204307+05:30
2	auth	0001_initial	2019-01-16 12:13:04.433196+05:30
3	admin	0001_initial	2019-01-16 12:13:04.686177+05:30
4	admin	0002_logentry_remove_auto_add	2019-01-16 12:13:04.719138+05:30
5	contenttypes	0002_remove_content_type_name	2019-01-16 12:13:04.765769+05:30
6	auth	0002_alter_permission_name_max_length	2019-01-16 12:13:04.778421+05:30
7	auth	0003_alter_user_email_max_length	2019-01-16 12:13:04.801673+05:30
8	auth	0004_alter_user_username_opts	2019-01-16 12:13:04.817557+05:30
9	auth	0005_alter_user_last_login_null	2019-01-16 12:13:04.832595+05:30
10	auth	0006_require_contenttypes_0002	2019-01-16 12:13:04.835603+05:30
11	auth	0007_alter_validators_add_error_messages	2019-01-16 12:13:04.851673+05:30
12	auth	0008_alter_user_username_max_length	2019-01-16 12:13:04.917748+05:30
13	auth	0009_alter_user_last_name_max_length	2019-01-16 12:13:04.932279+05:30
14	sessions	0001_initial	2019-01-16 12:13:05.098274+05:30
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_migrations_id_seq', 14, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
ju4ls8kfzetlwecma0klhiinfogekd9e	ZjE2OGFiNzk5ZjEzOTA4MGNjMTQ0NjhhYzg4N2U1MjE2NWEwNzM1NDp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJlNWE0ZWFjMTI0NjE3NjY5YTY4MWYxZDFmZTI4M2ExZWJhZTkwZDVkIn0=	2019-01-30 12:27:24.037609+05:30
\.


--
-- Data for Name: mrigsession; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY mrigsession (sessionid, sessionobj, sessionexpiry) FROM stdin;
5QjxOIHsdb18Y0kGM8Ug1550725906_591395	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "494.45", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725906.558308
0tupHz3drMN1CWJPWkua1550725907_06835	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.10666666666666667", "Net_Credit": "11200.0", "Max_Risk": "93800.0", "Max_Yield": "0.11940298507462686", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.037795
q7F6bIehDB1WujK3GJNK1550725907_408991	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.185", "Net_Credit": "6475.0", "Max_Risk": "28525.0", "Max_Yield": "0.22699386503067484", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.376905
9htg5jYBMb4Hjvzw4Qya1550726210_799534	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "495.85", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726210.769095
EgN5C9yvL9TVOM9Y6hMu1550726211_156142	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.175", "Net_Credit": "15312.5", "Max_Risk": "72187.5", "Max_Yield": "0.21212121212121213", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.126256
taiK6NGlhTb5ISHbgLyu1550726211_534306	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "190.0", "PUT_LTP": "7.4", "PUT_OI": "173250.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "7.3", "PUT_AskPrice": "7.6", "PUT_AskQty": "1750.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "5162.499999999999", "Max_Risk": "12337.5", "Max_Yield": "0.4184397163120567", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.497708
LaBpe7pbHkpfLLGA2T9y1550728172_029478	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.0", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728171.998367
vx1CCB5PwWKnPE1tBFXi1550728172_3874	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.19", "Net_Credit": "13300.0", "Max_Risk": "56700.0", "Max_Yield": "0.2345679012345679", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.354313
UyCnUb6U2Gq2vhCQ9qxt1550728172_753376	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "448.75", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "300.0", "PUT_LTP": "1.75", "PUT_OI": "16900.0", "PUT_BidQty": "1300.0", "PUT_BidPrice": "1.7", "PUT_AskPrice": "2.7", "PUT_AskQty": "7800.0", "Initial_Yield": "0.1425", "Net_Credit": "18525.0", "Max_Risk": "111475.0", "Max_Yield": "0.1661807580174927", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.719283
F2lWWCjoPiyQCXwwbYM71550728173_121355	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "448.75", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "390.0", "PUT_LTP": "13.05", "PUT_OI": "13000.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "12.5", "PUT_AskPrice": "14.7", "PUT_AskQty": "11700.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "3834.999999999999", "Max_Risk": "9165.0", "Max_Yield": "0.4184397163120566", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728173.087262
oJydRfD8wKcKnPSYtiqj1550728380_280568	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.05", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.250489
v5k7p5DlqdXUsrufZK0U1550728380_66997	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.19", "Net_Credit": "13300.0", "Max_Risk": "56700.0", "Max_Yield": "0.2345679012345679", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.629856
2q60fF6wHd8dx8OrbQrj1550728381_041953	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "449.25", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "300.0", "PUT_LTP": "1.75", "PUT_OI": "16900.0", "PUT_BidQty": "1300.0", "PUT_BidPrice": "1.7", "PUT_AskPrice": "2.7", "PUT_AskQty": "7800.0", "Initial_Yield": "0.1425", "Net_Credit": "18525.0", "Max_Risk": "111475.0", "Max_Yield": "0.1661807580174927", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728381.005857
ZfQm2GjikwZ8FFDbSCe11550728381_402743	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "449.25", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "390.0", "PUT_LTP": "13.05", "PUT_OI": "13000.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "12.5", "PUT_AskPrice": "14.7", "PUT_AskQty": "11700.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "3834.999999999999", "Max_Risk": "9165.0", "Max_Yield": "0.4184397163120566", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728381.369657
SGnzOOObErHHFlbpppc01550725906_806177	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "494.45", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725906.769078
TtKlDWLfbXx2rbmtwYFc1550725907_152576	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.128", "Net_Credit": "11200.0", "Max_Risk": "76300.0", "Max_Yield": "0.14678899082568808", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.121491
pxuhUQDsB8iYbKHHm2UO1550725907_494245	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.18500000000000005", "Net_Credit": "3237.500000000001", "Max_Risk": "14262.5", "Max_Yield": "0.22699386503067492", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.463135
gAQmDEVJdOaYxplaZkmC1550726210_88724	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "495.85", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726210.855179
45sQq8jOvEuqYkhKBL8a1550726211_248044	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.19", "Net_Credit": "13300.0", "Max_Risk": "56700.0", "Max_Yield": "0.2345679012345679", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.211449
ciVKa57Cd4ycIPYWGAam1550728171_656463	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.0", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728171.509076
kLuR8Ik2RHEHqV0F0Dm61550728172_117683	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.13357142857142856", "Net_Credit": "16362.5", "Max_Risk": "106137.5", "Max_Yield": "0.15416323165704865", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.083591
dT74jw2JAtuBsH7iNaZ61550728172_483656	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.22166666666666665", "Net_Credit": "11637.499999999998", "Max_Risk": "40862.5", "Max_Yield": "0.2847965738758029", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.446557
QSzTE608dAiyzNthgDV91550728172_841612	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "448.75", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "350.0", "PUT_LTP": "7.0", "PUT_OI": "3900.0", "PUT_BidQty": "6500.0", "PUT_BidPrice": "6.0", "PUT_AskPrice": "7.3", "PUT_AskQty": "5200.0", "Initial_Yield": "0.18", "Net_Credit": "11700.0", "Max_Risk": "53300.0", "Max_Yield": "0.21951219512195122", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.80752
1SPKLgxp43y2taZfmx5q1550728379_85048	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.05", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728379.809405
RFR5Dn3phuHRmxmMJgG31550728380_366156	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.13357142857142856", "Net_Credit": "16362.5", "Max_Risk": "106137.5", "Max_Yield": "0.15416323165704865", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.334711
38SRFuGYHNJGzcZXp1SU1550728380_767223	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.22166666666666665", "Net_Credit": "11637.499999999998", "Max_Risk": "40862.5", "Max_Yield": "0.2847965738758029", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.729122
HLDskmZGIpBHgnwsva7H1550728381_133196	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "449.25", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "350.0", "PUT_LTP": "7.0", "PUT_OI": "3900.0", "PUT_BidQty": "6500.0", "PUT_BidPrice": "6.0", "PUT_AskPrice": "7.3", "PUT_AskQty": "5200.0", "Initial_Yield": "0.18", "Net_Credit": "11700.0", "Max_Risk": "53300.0", "Max_Yield": "0.21951219512195122", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728381.097099
9nSVqFoWJ9yBlyLBoysF1550729946_324088	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.251835
tyOkHa9uqibMyW9T3uG71550725906_901432	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "494.45", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725906.87135
TkPUPa4yHC0ArRCMagtV1550725907_238536	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.14500000000000002", "Net_Credit": "10150.000000000002", "Max_Risk": "59850.0", "Max_Yield": "0.16959064327485382", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.206718
4n7cbWqpHiAeUVAy9tUo1550726210_489275	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "495.85", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726210.45604
IvoH1V5qGeeDisY92vn41550726210_981881	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.13357142857142856", "Net_Credit": "16362.5", "Max_Risk": "106137.5", "Max_Yield": "0.15416323165704865", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726210.950031
ptQJXTU14t5fjM6hb3VC1550726211_340819	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.22166666666666665", "Net_Credit": "11637.499999999998", "Max_Risk": "40862.5", "Max_Yield": "0.2847965738758029", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.302691
JYXRBzUUZ2FjdqcEIypv1550728171_850005	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.0", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728171.818888
ur9tTlafBRt8V9IE8IVW1550728172_21093	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.15583333333333332", "Net_Credit": "16362.5", "Max_Risk": "88637.5", "Max_Yield": "0.18460019743336623", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.17183
6MeGWGe5PgYWktjmESTn1550728172_577908	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.24", "Net_Credit": "8400.0", "Max_Risk": "26600.0", "Max_Yield": "0.3157894736842105", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.537799
qDM6aG3qF2BhdZbjB4ph1550728172_935859	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "448.75", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "360.0", "PUT_LTP": "7.7", "PUT_OI": "7800.0", "PUT_BidQty": "7800.0", "PUT_BidPrice": "7.25", "PUT_AskPrice": "8.8", "PUT_AskQty": "5200.0", "Initial_Yield": "0.20750000000000002", "Net_Credit": "10790.000000000002", "Max_Risk": "41210.0", "Max_Yield": "0.26182965299684546", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.903777
jnRBMpT9s7cYs0yAuUNS1550728380_090512	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.05", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.056443
wMsVgwWQPIk9L1Qlh4zC1550728380_458403	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.15583333333333332", "Net_Credit": "16362.5", "Max_Risk": "88637.5", "Max_Yield": "0.18460019743336623", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.425312
rjfTjsrZHT9a1ftBU4dU1550728380_86047	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.24", "Net_Credit": "8400.0", "Max_Risk": "26600.0", "Max_Yield": "0.3157894736842105", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.82237
fO4KMacjV1BbLXAA0SxX1550728381_224268	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "449.25", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "360.0", "PUT_LTP": "7.7", "PUT_OI": "7800.0", "PUT_BidQty": "7800.0", "PUT_BidPrice": "7.25", "PUT_AskPrice": "8.8", "PUT_AskQty": "5200.0", "Initial_Yield": "0.20750000000000002", "Net_Credit": "10790.000000000002", "Max_Risk": "41210.0", "Max_Yield": "0.26182965299684546", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728381.19018
rhMv4gtykBqRcMBgsTZ41550729946_349787	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "420.0", "PUT_LTP": "3.0", "PUT_OI": "4244.0", "PUT_BidQty": "3183.0", "PUT_BidPrice": "2.15", "PUT_AskPrice": "3.7", "PUT_AskQty": "1061.0", "Initial_Yield": "0.14750000000000002", "Net_Credit": "6259.900000000001", "Max_Risk": "36180.1", "Max_Yield": "0.17302052785923755", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.305634
3mJMgMiThDdTljnaMFa51550725906_984654	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "494.45", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725906.955575
TFMsAEkLSWH3dusxlOV11550725907_322761	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "214.95", "Lot": "1750", "Higher_Strike": "190.0", "Higher_Strike_LTP": "7.4", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.155", "Net_Credit": "8137.500000000001", "Max_Risk": "44362.5", "Max_Yield": "0.18343195266272191", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550725907.293684
f1O5cAdyZHQXkqGOVBjR1550726210_705572	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "495.85", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726210.66924
5847iodsI6TkYYfhhhPP1550726211_069939	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.15583333333333332", "Net_Credit": "16362.5", "Max_Risk": "88637.5", "Max_Yield": "0.18460019743336623", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.036307
gslbMKbezROXY4AfuBVH1550726211_441058	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.2", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.24", "Net_Credit": "8400.0", "Max_Risk": "26600.0", "Max_Yield": "0.3157894736842105", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550726211.396438
wwy0yUSAtIR1PM9qT1zQ1550728171_943218	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.0", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728171.912169
k1KxXfFXlXEaYv2fGDbO1550728172_299165	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.175", "Net_Credit": "15312.5", "Max_Risk": "72187.5", "Max_Yield": "0.21212121212121213", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.266078
72TZYhhNPOfwre7pHf5W1550728172_666142	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.6", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "190.0", "PUT_LTP": "7.4", "PUT_OI": "173250.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "7.3", "PUT_AskPrice": "7.6", "PUT_AskQty": "1750.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "5162.499999999999", "Max_Risk": "12337.5", "Max_Yield": "0.4184397163120567", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.632052
oe3Kr5XZLvrjx3fMmynD1550728173_033117	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "448.75", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "380.0", "PUT_LTP": "12.0", "PUT_OI": "3900.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "10.35", "PUT_AskPrice": "12.4", "PUT_AskQty": "9100.0", "Initial_Yield": "0.2", "Net_Credit": "5200.0", "Max_Risk": "20800.0", "Max_Yield": "0.25", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728172.998027
md90xtjqYRnovRa5ubl91550728380_196342	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "496.05", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.160701
z7iSPo3LQQ8EgKCWcJsV1550728380_562679	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.175", "Net_Credit": "15312.5", "Max_Risk": "72187.5", "Max_Yield": "0.21212121212121213", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.522575
dmGhoRVRgF0Uf55zL7XF1550728380_949708	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.65", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "190.0", "PUT_LTP": "7.4", "PUT_OI": "173250.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "7.3", "PUT_AskPrice": "7.6", "PUT_AskQty": "1750.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "5162.499999999999", "Max_Risk": "12337.5", "Max_Yield": "0.4184397163120567", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728380.916623
Qer5aElBrBNphqLL6Gng1550728381_312506	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "449.25", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "380.0", "PUT_LTP": "12.0", "PUT_OI": "3900.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "10.35", "PUT_AskPrice": "12.4", "PUT_AskQty": "9100.0", "Initial_Yield": "0.2", "Net_Credit": "5200.0", "Max_Risk": "20800.0", "Max_Yield": "0.25", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550728381.279415
g3KfescgFgD7RZkkXuL21550729946_597914	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.529467
SX7UOlq23vBJ6yFuuDwM1550729946_59992	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "430.0", "PUT_LTP": "3.9", "PUT_OI": "9549.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "3.05", "PUT_AskPrice": "4.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.16666666666666666", "Net_Credit": "5305.0", "Max_Risk": "26525.0", "Max_Yield": "0.2", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.53914
XU1w2ALmpRAt10FGYnN01550729946_700598	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.662417
msSHJqZF7uhsEC3pvqMU1550729946_70567	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "440.0", "PUT_LTP": "5.25", "PUT_OI": "6366.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "4.6", "PUT_AskPrice": "5.3", "PUT_AskQty": "1061.0", "Initial_Yield": "0.18250000000000002", "Net_Credit": "3872.6500000000005", "Max_Risk": "17347.35", "Max_Yield": "0.22324159021406734", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.665115
NZyXkEty24kfc14o0pLG1550729946_786749	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.702857
YP7ib8K7BPLMy0rd3A3v1550729946_814716	{"Expiry": "28032019", "Symbol": "TATASTEEL", "Underlying": "498.1", "Lot": "1061", "Higher_Strike": "460.0", "Higher_Strike_LTP": "8.9", "Strike_Price": "450.0", "PUT_LTP": "7.0", "PUT_OI": "35013.0", "PUT_BidQty": "1061.0", "PUT_BidPrice": "6.4", "PUT_AskPrice": "7.0", "PUT_AskQty": "2122.0", "Initial_Yield": "0.19000000000000003", "Net_Credit": "2015.9000000000003", "Max_Risk": "8594.1", "Max_Yield": "0.23456790123456792", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.780143
K8lTfsL8ieLYpwCssmcW1550729946_902447	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.13357142857142856", "Net_Credit": "16362.5", "Max_Risk": "106137.5", "Max_Yield": "0.15416323165704865", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.796269
r9yxHVmb6noFWFu8pz031550729946_961563	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "130.0", "PUT_LTP": "1.0", "PUT_OI": "12250.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "0.55", "PUT_AskPrice": "0.95", "PUT_AskQty": "3500.0", "Initial_Yield": "0.13357142857142856", "Net_Credit": "16362.5", "Max_Risk": "106137.5", "Max_Yield": "0.15416323165704865", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.889472
c1tmGyy4jxtixsfUVJyi1550729946_968883	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.15583333333333332", "Net_Credit": "16362.5", "Max_Risk": "88637.5", "Max_Yield": "0.18460019743336623", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729946.916327
bLtx5aGK1vN93eQaU6gf1550729947_081828	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.175", "Net_Credit": "15312.5", "Max_Risk": "72187.5", "Max_Yield": "0.21212121212121213", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.027669
3Ye7ni4fahM2KzUpW4WH1550729947_083832	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "140.0", "PUT_LTP": "1.0", "PUT_OI": "59500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "1.1", "PUT_AskPrice": "1.3", "PUT_AskQty": "5250.0", "Initial_Yield": "0.15583333333333332", "Net_Credit": "16362.5", "Max_Risk": "88637.5", "Max_Yield": "0.18460019743336623", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.034052
jrLfQr0SAtzko6Elmx0O1550729947_183896	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.19", "Net_Credit": "13300.0", "Max_Risk": "56700.0", "Max_Yield": "0.2345679012345679", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.094863
K5gbD04n70li97F7Ehpq1550729947_220101	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "150.0", "PUT_LTP": "1.6", "PUT_OI": "89250.0", "PUT_BidQty": "3500.0", "PUT_BidPrice": "1.55", "PUT_AskPrice": "1.8", "PUT_AskQty": "1750.0", "Initial_Yield": "0.175", "Net_Credit": "15312.5", "Max_Risk": "72187.5", "Max_Yield": "0.21212121212121213", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.175031
EF82vAIB9BTWXmRFPSoj1550729947_293033	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.22166666666666665", "Net_Credit": "11637.499999999998", "Max_Risk": "40862.5", "Max_Yield": "0.2847965738758029", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.199791
PC2yQrPMVVFnmdhz5cwT1550729947_326066	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "160.0", "PUT_LTP": "2.75", "PUT_OI": "115500.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "2.5", "PUT_AskPrice": "2.7", "PUT_AskQty": "1750.0", "Initial_Yield": "0.19", "Net_Credit": "13300.0", "Max_Risk": "56700.0", "Max_Yield": "0.2345679012345679", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.288055
DKFMuYB8EsTMoB1Qewnt1550729947_332202	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.24", "Net_Credit": "8400.0", "Max_Risk": "26600.0", "Max_Yield": "0.3157894736842105", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.297043
6NcKsFDuBPcyKTciE6RE1550729947_43732	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "190.0", "PUT_LTP": "7.4", "PUT_OI": "173250.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "7.3", "PUT_AskPrice": "7.6", "PUT_AskQty": "1750.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "5162.499999999999", "Max_Risk": "12337.5", "Max_Yield": "0.4184397163120567", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.39127
DkmPNWbNQHGaOjgI5GxS1550729947_43732	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "170.0", "PUT_LTP": "3.7", "PUT_OI": "120750.0", "PUT_BidQty": "1750.0", "PUT_BidPrice": "3.8", "PUT_AskPrice": "3.95", "PUT_AskQty": "1750.0", "Initial_Yield": "0.22166666666666665", "Net_Credit": "11637.499999999998", "Max_Risk": "40862.5", "Max_Yield": "0.2847965738758029", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.394818
mJNZP0Q8mw6BPDszD9m11550729947_516691	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "300.0", "PUT_LTP": "1.75", "PUT_OI": "16900.0", "PUT_BidQty": "1300.0", "PUT_BidPrice": "1.7", "PUT_AskPrice": "2.7", "PUT_AskQty": "7800.0", "Initial_Yield": "0.1425", "Net_Credit": "18525.0", "Max_Risk": "111475.0", "Max_Yield": "0.1661807580174927", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.439461
waZWt6OBfVbgpSxNKNv61550729947_554339	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "180.0", "PUT_LTP": "5.55", "PUT_OI": "246750.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "5.15", "PUT_AskPrice": "5.85", "PUT_AskQty": "3500.0", "Initial_Yield": "0.24", "Net_Credit": "8400.0", "Max_Risk": "26600.0", "Max_Yield": "0.3157894736842105", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.510482
zlX8ZbN4YOHJyOykMeg91550729947_620792	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "350.0", "PUT_LTP": "7.0", "PUT_OI": "3900.0", "PUT_BidQty": "6500.0", "PUT_BidPrice": "6.0", "PUT_AskPrice": "7.3", "PUT_AskQty": "5200.0", "Initial_Yield": "0.18", "Net_Credit": "11700.0", "Max_Risk": "53300.0", "Max_Yield": "0.21951219512195122", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.528268
QG6oGZwv8f6dNEtknEId1550729947_665577	{"Expiry": "28032019", "Symbol": "YESBANK", "Underlying": "215.35", "Lot": "1750", "Higher_Strike": "200.0", "Higher_Strike_LTP": "10.35", "Strike_Price": "190.0", "PUT_LTP": "7.4", "PUT_OI": "173250.0", "PUT_BidQty": "5250.0", "PUT_BidPrice": "7.3", "PUT_AskPrice": "7.6", "PUT_AskQty": "1750.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "5162.499999999999", "Max_Risk": "12337.5", "Max_Yield": "0.4184397163120567", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.622796
pXggUJap7H88DucggGV61550729947_670031	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "360.0", "PUT_LTP": "7.7", "PUT_OI": "7800.0", "PUT_BidQty": "7800.0", "PUT_BidPrice": "7.25", "PUT_AskPrice": "8.8", "PUT_AskQty": "5200.0", "Initial_Yield": "0.20750000000000002", "Net_Credit": "10790.000000000002", "Max_Risk": "41210.0", "Max_Yield": "0.26182965299684546", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.631907
oH5atK4Il0ZDaeLKgR7Y1550729947_777801	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "380.0", "PUT_LTP": "12.0", "PUT_OI": "3900.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "10.35", "PUT_AskPrice": "12.4", "PUT_AskQty": "9100.0", "Initial_Yield": "0.2", "Net_Credit": "5200.0", "Max_Risk": "20800.0", "Max_Yield": "0.25", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.733638
5ITr0Re0h2z7573SMHYP1550729947_782042	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "300.0", "PUT_LTP": "1.75", "PUT_OI": "16900.0", "PUT_BidQty": "1300.0", "PUT_BidPrice": "1.7", "PUT_AskPrice": "2.7", "PUT_AskQty": "7800.0", "Initial_Yield": "0.1425", "Net_Credit": "18525.0", "Max_Risk": "111475.0", "Max_Yield": "0.1661807580174927", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.736763
nA4PoragzHku06NavRCa1550729947_857294	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "390.0", "PUT_LTP": "13.05", "PUT_OI": "13000.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "12.5", "PUT_AskPrice": "14.7", "PUT_AskQty": "11700.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "3834.999999999999", "Max_Risk": "9165.0", "Max_Yield": "0.4184397163120566", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.780038
BFR8IybIDigAyIajtEiT1550729947_89927	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "350.0", "PUT_LTP": "7.0", "PUT_OI": "3900.0", "PUT_BidQty": "6500.0", "PUT_BidPrice": "6.0", "PUT_AskPrice": "7.3", "PUT_AskQty": "5200.0", "Initial_Yield": "0.18", "Net_Credit": "11700.0", "Max_Risk": "53300.0", "Max_Yield": "0.21951219512195122", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.850702
OyKGJXh3v0yxyryKC2AF1550729948_02043	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "360.0", "PUT_LTP": "7.7", "PUT_OI": "7800.0", "PUT_BidQty": "7800.0", "PUT_BidPrice": "7.25", "PUT_AskPrice": "8.8", "PUT_AskQty": "5200.0", "Initial_Yield": "0.20750000000000002", "Net_Credit": "10790.000000000002", "Max_Risk": "41210.0", "Max_Yield": "0.26182965299684546", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729947.984229
b6gFmi3ayQ3qfuU7jEZ01550729948_218106	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "380.0", "PUT_LTP": "12.0", "PUT_OI": "3900.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "10.35", "PUT_AskPrice": "12.4", "PUT_AskQty": "9100.0", "Initial_Yield": "0.2", "Net_Credit": "5200.0", "Max_Risk": "20800.0", "Max_Yield": "0.25", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729948.178594
xEoj703ITi9Pof57Ny3J1550729948_327107	{"Expiry": "28032019", "Symbol": "ZEEL", "Underlying": "447.7", "Lot": "1300", "Higher_Strike": "400.0", "Higher_Strike_LTP": "16.0", "Strike_Price": "390.0", "PUT_LTP": "13.05", "PUT_OI": "13000.0", "PUT_BidQty": "15600.0", "PUT_BidPrice": "12.5", "PUT_AskPrice": "14.7", "PUT_AskQty": "11700.0", "Initial_Yield": "0.29499999999999993", "Net_Credit": "3834.999999999999", "Max_Risk": "9165.0", "Max_Yield": "0.4184397163120566", "ExpiryDUP": "2019-03-28", "Id": "", "strategyname": "bullputspread"}	1550729948.290536
\.


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: mrigsession mrigsession_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY mrigsession
    ADD CONSTRAINT mrigsession_pkey PRIMARY KEY (sessionid);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_groups_group_id_97559544 ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_username_6821ab7c_like ON auth_user USING btree (username varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

