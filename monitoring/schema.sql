--
-- PostgreSQL database dump
--

-- Dumped from database version 11.2 (Debian 11.2-1.pgdg90+1)
-- Dumped by pg_dump version 11.6 (Ubuntu 11.6-1.pgdg16.04+1)

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

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: experiments; Type: TABLE; Schema: public; Owner: jl
--

CREATE TABLE public.experiments (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    update_date timestamp without time zone,
    create_date timestamp without time zone
);


ALTER TABLE public.experiments OWNER TO jl;

--
-- Name: experiments_id_seq; Type: SEQUENCE; Schema: public; Owner: jl
--

CREATE SEQUENCE public.experiments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.experiments_id_seq OWNER TO jl;

--
-- Name: experiments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jl
--

ALTER SEQUENCE public.experiments_id_seq OWNED BY public.experiments.id;


--
-- Name: metrics; Type: TABLE; Schema: public; Owner: jl
--

CREATE TABLE public.metrics (
    id bigint NOT NULL,
    experiment_id integer NOT NULL,
    key character varying(45) NOT NULL,
    value double precision NOT NULL,
    step integer,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "time" double precision
);


ALTER TABLE public.metrics OWNER TO jl;

--
-- Name: metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: jl
--

CREATE SEQUENCE public.metrics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.metrics_id_seq OWNER TO jl;

--
-- Name: metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jl
--

ALTER SEQUENCE public.metrics_id_seq OWNED BY public.metrics.id;


--
-- Name: texts; Type: TABLE; Schema: public; Owner: jl
--

CREATE TABLE public.texts (
    id bigint NOT NULL,
    experiment_id integer NOT NULL,
    key character varying(45) NOT NULL,
    value text NOT NULL,
    step integer,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "time" double precision,
    loss double precision,
    text_en text
);


ALTER TABLE public.texts OWNER TO jl;

--
-- Name: texts_id_seq; Type: SEQUENCE; Schema: public; Owner: jl
--

CREATE SEQUENCE public.texts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.texts_id_seq OWNER TO jl;

--
-- Name: texts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jl
--

ALTER SEQUENCE public.texts_id_seq OWNED BY public.texts.id;


--
-- Name: experiments id; Type: DEFAULT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.experiments ALTER COLUMN id SET DEFAULT nextval('public.experiments_id_seq'::regclass);


--
-- Name: metrics id; Type: DEFAULT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.metrics ALTER COLUMN id SET DEFAULT nextval('public.metrics_id_seq'::regclass);


--
-- Name: texts id; Type: DEFAULT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.texts ALTER COLUMN id SET DEFAULT nextval('public.texts_id_seq'::regclass);


--
-- Name: experiments experiments_name_key; Type: CONSTRAINT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_name_key UNIQUE (name);


--
-- Name: experiments experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_pkey PRIMARY KEY (id);


--
-- Name: metrics metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (id);


--
-- Name: texts texts_pkey; Type: CONSTRAINT; Schema: public; Owner: jl
--

ALTER TABLE ONLY public.texts
    ADD CONSTRAINT texts_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO "gpu_experiments-ro";
GRANT CREATE ON SCHEMA public TO "gpu_experiments-admin";


--
-- Name: TABLE experiments; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON TABLE public.experiments TO "gpu_experiments-ro";
GRANT INSERT,REFERENCES,DELETE,UPDATE ON TABLE public.experiments TO "gpu_experiments-rw";
GRANT TRIGGER,TRUNCATE ON TABLE public.experiments TO "gpu_experiments-admin";
GRANT DELETE ON TABLE public.experiments TO "gpu_experiments-overquota";


--
-- Name: SEQUENCE experiments_id_seq; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON SEQUENCE public.experiments_id_seq TO "gpu_experiments-ro";
GRANT USAGE,UPDATE ON SEQUENCE public.experiments_id_seq TO "gpu_experiments-rw";


--
-- Name: TABLE metrics; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON TABLE public.metrics TO "gpu_experiments-ro";
GRANT INSERT,REFERENCES,DELETE,UPDATE ON TABLE public.metrics TO "gpu_experiments-rw";
GRANT TRIGGER,TRUNCATE ON TABLE public.metrics TO "gpu_experiments-admin";
GRANT DELETE ON TABLE public.metrics TO "gpu_experiments-overquota";


--
-- Name: SEQUENCE metrics_id_seq; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON SEQUENCE public.metrics_id_seq TO "gpu_experiments-ro";
GRANT USAGE,UPDATE ON SEQUENCE public.metrics_id_seq TO "gpu_experiments-rw";


--
-- Name: TABLE texts; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON TABLE public.texts TO "gpu_experiments-ro";
GRANT INSERT,REFERENCES,DELETE,UPDATE ON TABLE public.texts TO "gpu_experiments-rw";
GRANT TRIGGER,TRUNCATE ON TABLE public.texts TO "gpu_experiments-admin";
GRANT DELETE ON TABLE public.texts TO "gpu_experiments-overquota";


--
-- Name: SEQUENCE texts_id_seq; Type: ACL; Schema: public; Owner: jl
--

GRANT SELECT ON SEQUENCE public.texts_id_seq TO "gpu_experiments-ro";
GRANT USAGE,UPDATE ON SEQUENCE public.texts_id_seq TO "gpu_experiments-rw";


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: gpu_experiments-admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE "gpu_experiments-admin" GRANT SELECT ON SEQUENCES  TO "gpu_experiments-ro";
ALTER DEFAULT PRIVILEGES FOR ROLE "gpu_experiments-admin" GRANT USAGE,UPDATE ON SEQUENCES  TO "gpu_experiments-rw";


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: jl
--

ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT SELECT ON SEQUENCES  TO "gpu_experiments-ro";
ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT USAGE,UPDATE ON SEQUENCES  TO "gpu_experiments-rw";


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: gpu_experiments-admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE "gpu_experiments-admin" GRANT SELECT ON TABLES  TO "gpu_experiments-ro";
ALTER DEFAULT PRIVILEGES FOR ROLE "gpu_experiments-admin" GRANT INSERT,REFERENCES,DELETE,UPDATE ON TABLES  TO "gpu_experiments-rw";
ALTER DEFAULT PRIVILEGES FOR ROLE "gpu_experiments-admin" GRANT DELETE ON TABLES  TO "gpu_experiments-overquota";


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: jl
--

ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT SELECT ON TABLES  TO "gpu_experiments-ro";
ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT INSERT,REFERENCES,DELETE,UPDATE ON TABLES  TO "gpu_experiments-rw";
ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT TRIGGER,TRUNCATE ON TABLES  TO "gpu_experiments-admin";
ALTER DEFAULT PRIVILEGES FOR ROLE jl GRANT DELETE ON TABLES  TO "gpu_experiments-overquota";


--
-- PostgreSQL database dump complete
--

