--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Ubuntu 14.15-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.15 (Ubuntu 14.15-0ubuntu0.22.04.1)

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
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: new_session(); Type: FUNCTION; Schema: public; Owner: ollama
--

CREATE FUNCTION public.new_session() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	INSERT INTO messages ("session_id", "content", "role")
	VALUES(NEW.id, 'First message', 'LLM');
RETURN NULL;
END;$$;


ALTER FUNCTION public.new_session() OWNER TO ollama;

--
-- Name: new_user(); Type: FUNCTION; Schema: public; Owner: ollama
--

CREATE FUNCTION public.new_user() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	INSERT INTO sessions ("user_id", "title") VALUES(NEW.id, 'New Session');
RETURN NULL;
END;$$;


ALTER FUNCTION public.new_user() OWNER TO ollama;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: history; Type: TABLE; Schema: public; Owner: ollama
--

CREATE TABLE public.history (
    id integer NOT NULL,
    history text,
    timeadd timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.history OWNER TO ollama;

--
-- Name: history_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.history_id_seq OWNER TO ollama;

--
-- Name: history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.history_id_seq OWNED BY public.history.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: ollama
--

CREATE TABLE public.messages (
    id bigint NOT NULL,
    session_id integer NOT NULL,
    "time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    content text,
    role text NOT NULL
);


ALTER TABLE public.messages OWNER TO ollama;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO ollama;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: messages_session_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.messages_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_session_id_seq OWNER TO ollama;

--
-- Name: messages_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.messages_session_id_seq OWNED BY public.messages.session_id;


--
-- Name: pages; Type: TABLE; Schema: public; Owner: ollama
--

CREATE TABLE public.pages (
    id integer NOT NULL,
    title text,
    doc text NOT NULL,
    link text,
    rating integer DEFAULT 0 NOT NULL,
    embedding public.vector(1024) NOT NULL,
    timeadd timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    timeupdate timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.pages OWNER TO ollama;

--
-- Name: pages_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.pages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pages_id_seq OWNER TO ollama;

--
-- Name: pages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.pages_id_seq OWNED BY public.pages.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: ollama
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title text,
    start_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.sessions OWNER TO ollama;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sessions_id_seq OWNER TO ollama;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: sessions_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.sessions_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sessions_user_id_seq OWNER TO ollama;

--
-- Name: sessions_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.sessions_user_id_seq OWNED BY public.sessions.user_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ollama
--

CREATE TABLE public.users (
    id integer NOT NULL,
    login text NOT NULL,
    time_first_login timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    time_last_login timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.users OWNER TO ollama;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ollama
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO ollama;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ollama
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: history id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.history ALTER COLUMN id SET DEFAULT nextval('public.history_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: messages session_id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.messages ALTER COLUMN session_id SET DEFAULT nextval('public.messages_session_id_seq'::regclass);


--
-- Name: pages id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.pages ALTER COLUMN id SET DEFAULT nextval('public.pages_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: sessions user_id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.sessions ALTER COLUMN user_id SET DEFAULT nextval('public.sessions_user_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: history history_pkey; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: pages pages_pkey; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.pages
    ADD CONSTRAINT pages_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_login; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: pages_embedding_idx; Type: INDEX; Schema: public; Owner: ollama
--

CREATE INDEX pages_embedding_idx ON public.pages USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: sessions new_session; Type: TRIGGER; Schema: public; Owner: ollama
--

CREATE TRIGGER new_session AFTER INSERT ON public.sessions FOR EACH ROW EXECUTE FUNCTION public.new_session();


--
-- Name: users new_user; Type: TRIGGER; Schema: public; Owner: ollama
--

CREATE TRIGGER new_user AFTER INSERT ON public.users FOR EACH ROW EXECUTE FUNCTION public.new_user();


--
-- Name: messages messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id) NOT VALID;


--
-- Name: sessions session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ollama
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) NOT VALID;


--
-- PostgreSQL database dump complete
--

