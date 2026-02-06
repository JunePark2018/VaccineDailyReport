--
-- PostgreSQL database cluster dump
--

\restrict YytTZxz5llb58ySmPbgbqkug0kDfHTcNogo6C4L0hiOVHLoyACZVUqWQJAxxqgE

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE myuser;
ALTER ROLE myuser WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:fqrd00UUJW5dNgTb2z/Zzw==$ipCzkL/gqyEsTH2yK0oSfXcZozhHIgNzoOZ0XpSia6g=:Ow41uYyHc3RNtRulrRKug6GyeB51Wlhqzitqp+ek3yE=';

--
-- User Configurations
--








\unrestrict YytTZxz5llb58ySmPbgbqkug0kDfHTcNogo6C4L0hiOVHLoyACZVUqWQJAxxqgE

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict P229naOaaIdAch6cjAw1grOnq3qfPm2v8l28J6a1Axb7KWQbwQZUeV7lauz0g6y

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

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
-- PostgreSQL database dump complete
--

\unrestrict P229naOaaIdAch6cjAw1grOnq3qfPm2v8l28J6a1Axb7KWQbwQZUeV7lauz0g6y

--
-- Database "mydb" dump
--

--
-- PostgreSQL database dump
--

\restrict IzTnjUN8eqQobfDtEG5ul6U1m1cVHvbXVrnY0H6YWVrPPWccPjxLk8hVrynkUcE

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

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
-- Name: mydb; Type: DATABASE; Schema: -; Owner: myuser
--

CREATE DATABASE mydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE mydb OWNER TO myuser;

\unrestrict IzTnjUN8eqQobfDtEG5ul6U1m1cVHvbXVrnY0H6YWVrPPWccPjxLk8hVrynkUcE
\connect mydb
\restrict IzTnjUN8eqQobfDtEG5ul6U1m1cVHvbXVrnY0H6YWVrPPWccPjxLk8hVrynkUcE

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

SET default_table_access_method = heap;

--
-- Name: ai_generated_news; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.ai_generated_news (
    ai_generated_news_id integer NOT NULL,
    cluster_id integer NOT NULL,
    category_id integer,
    title character varying,
    contents text,
    search_keyword character varying,
    global_search_status character varying,
    search_retry_count integer,
    keywords json,
    analysis_result json,
    created_at timestamp without time zone NOT NULL,
    modified_at timestamp without time zone,
    deleted_at timestamp without time zone,
    like_count integer NOT NULL,
    dislike_count integer NOT NULL
);


ALTER TABLE public.ai_generated_news OWNER TO myuser;

--
-- Name: ai_generated_news_ai_generated_news_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.ai_generated_news_ai_generated_news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_generated_news_ai_generated_news_id_seq OWNER TO myuser;

--
-- Name: ai_generated_news_ai_generated_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.ai_generated_news_ai_generated_news_id_seq OWNED BY public.ai_generated_news.ai_generated_news_id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.categories OWNER TO myuser;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_category_id_seq OWNER TO myuser;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: cluster_news_link; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.cluster_news_link (
    cluster_id integer NOT NULL,
    news_id integer NOT NULL
);


ALTER TABLE public.cluster_news_link OWNER TO myuser;

--
-- Name: clusters; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.clusters (
    cluster_id integer NOT NULL,
    title character varying NOT NULL
);


ALTER TABLE public.clusters OWNER TO myuser;

--
-- Name: clusters_cluster_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.clusters_cluster_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clusters_cluster_id_seq OWNER TO myuser;

--
-- Name: clusters_cluster_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.clusters_cluster_id_seq OWNED BY public.clusters.cluster_id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.companies (
    company_id integer NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(100)
);


ALTER TABLE public.companies OWNER TO myuser;

--
-- Name: companies_company_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.companies_company_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.companies_company_id_seq OWNER TO myuser;

--
-- Name: companies_company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.companies_company_id_seq OWNED BY public.companies.company_id;


--
-- Name: news; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.news (
    news_id integer NOT NULL,
    title character varying,
    contents text,
    url character varying NOT NULL,
    company_id integer NOT NULL,
    img_urls json,
    created_at timestamp without time zone NOT NULL,
    modified_at timestamp without time zone,
    deleted_at timestamp without time zone,
    is_domestic boolean,
    category_id integer
);


ALTER TABLE public.news OWNER TO myuser;

--
-- Name: news_news_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.news_news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.news_news_id_seq OWNER TO myuser;

--
-- Name: news_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.news_news_id_seq OWNED BY public.news.news_id;


--
-- Name: news_reactions; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.news_reactions (
    news_reaction_id integer NOT NULL,
    user_id integer NOT NULL,
    news_id integer NOT NULL,
    value integer NOT NULL,
    CONSTRAINT ck_reaction_value CHECK ((value = ANY (ARRAY[1, '-1'::integer])))
);


ALTER TABLE public.news_reactions OWNER TO myuser;

--
-- Name: news_reactions_news_reaction_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.news_reactions_news_reaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.news_reactions_news_reaction_id_seq OWNER TO myuser;

--
-- Name: news_reactions_news_reaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.news_reactions_news_reaction_id_seq OWNED BY public.news_reactions.news_reaction_id;


--
-- Name: news_views; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.news_views (
    news_view_id integer NOT NULL,
    user_id integer NOT NULL,
    news_id integer NOT NULL,
    category_id integer,
    viewed_at timestamp without time zone NOT NULL
);


ALTER TABLE public.news_views OWNER TO myuser;

--
-- Name: news_views_news_view_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.news_views_news_view_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.news_views_news_view_id_seq OWNER TO myuser;

--
-- Name: news_views_news_view_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.news_views_news_view_id_seq OWNED BY public.news_views.news_view_id;


--
-- Name: search_logs; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.search_logs (
    search_log_id integer NOT NULL,
    user_id integer NOT NULL,
    query character varying(255) NOT NULL,
    searched_at timestamp without time zone NOT NULL
);


ALTER TABLE public.search_logs OWNER TO myuser;

--
-- Name: search_logs_search_log_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.search_logs_search_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.search_logs_search_log_id_seq OWNER TO myuser;

--
-- Name: search_logs_search_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.search_logs_search_log_id_seq OWNED BY public.search_logs.search_log_id;


--
-- Name: user_category_subscriptions; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.user_category_subscriptions (
    user_id integer NOT NULL,
    category_id integer NOT NULL
);


ALTER TABLE public.user_category_subscriptions OWNER TO myuser;

--
-- Name: user_keyword_read_stats; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.user_keyword_read_stats (
    user_id integer NOT NULL,
    keyword character varying(200) NOT NULL,
    count integer NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_keyword_read_stats OWNER TO myuser;

--
-- Name: user_keyword_subscriptions; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.user_keyword_subscriptions (
    user_id integer NOT NULL,
    keyword character varying(200) NOT NULL
);


ALTER TABLE public.user_keyword_subscriptions OWNER TO myuser;

--
-- Name: users; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    login_id character varying(50) NOT NULL,
    user_real_name character varying(50),
    password_hash character varying(255) NOT NULL,
    email character varying(100),
    age_range character varying(30),
    gender character varying(30),
    fcm_token character varying(255),
    created_at timestamp without time zone NOT NULL,
    modified_at timestamp without time zone,
    deleted_at timestamp without time zone,
    marketing_agree boolean NOT NULL,
    user_status integer NOT NULL
);


ALTER TABLE public.users OWNER TO myuser;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO myuser;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: ai_generated_news ai_generated_news_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.ai_generated_news ALTER COLUMN ai_generated_news_id SET DEFAULT nextval('public.ai_generated_news_ai_generated_news_id_seq'::regclass);


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: clusters cluster_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.clusters ALTER COLUMN cluster_id SET DEFAULT nextval('public.clusters_cluster_id_seq'::regclass);


--
-- Name: companies company_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.companies ALTER COLUMN company_id SET DEFAULT nextval('public.companies_company_id_seq'::regclass);


--
-- Name: news news_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news ALTER COLUMN news_id SET DEFAULT nextval('public.news_news_id_seq'::regclass);


--
-- Name: news_reactions news_reaction_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_reactions ALTER COLUMN news_reaction_id SET DEFAULT nextval('public.news_reactions_news_reaction_id_seq'::regclass);


--
-- Name: news_views news_view_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views ALTER COLUMN news_view_id SET DEFAULT nextval('public.news_views_news_view_id_seq'::regclass);


--
-- Name: search_logs search_log_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.search_logs ALTER COLUMN search_log_id SET DEFAULT nextval('public.search_logs_search_log_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: ai_generated_news; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.ai_generated_news (ai_generated_news_id, cluster_id, category_id, title, contents, search_keyword, global_search_status, search_retry_count, keywords, analysis_result, created_at, modified_at, deleted_at, like_count, dislike_count) FROM stdin;
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.categories (category_id, name) FROM stdin;
1	정치
2	경제
3	사회
4	생활/문화
5	세계
6	IT/과학
\.


--
-- Data for Name: cluster_news_link; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.cluster_news_link (cluster_id, news_id) FROM stdin;
\.


--
-- Data for Name: clusters; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.clusters (cluster_id, title) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.companies (company_id, name, display_name) FROM stdin;
1	SBS	\N
2	JTBC	\N
3	한국일보	\N
4	연합뉴스	\N
5	한국경제	\N
6	한겨레	\N
7	연합뉴스TV	\N
8	경향신문	\N
9	MBC	\N
10	조선비즈	\N
11	KBS	\N
\.


--
-- Data for Name: news; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.news (news_id, title, contents, url, company_id, img_urls, created_at, modified_at, deleted_at, is_domestic, category_id) FROM stdin;
1	[정치쇼] 한민수 "김건희 1심? 충격과 분노…항소하면 뒤집힐 것"	김건희 1년 8개월 징역 선고? 충격과 분노 尹 녹취 있는데 공천 개입 무죄 납득 안 돼 코스피 5000 시대에 주가 조작 단죄 안 해 비상식적 특검 항소하면 2심서 뒤집힐 것 권성동 유죄, 통일교 신천지 특검 힘 실릴 것 민주 혁신 합당, 전 당원 토론 투표로 결정 방법 거칠다? 당 대표 결단 생각 다를 수도 왜 지금이냐? 총선 대선 때는 더 어려워 민주당 혁신당 합당, 李 정부 뒷받침에 효용 방송 SBS 김태현의 정치쇼 FM 103.5MHz 7 00 9 00 일자 2026년 1월 29일 목 진행 김태현 변호사 출연 한민수 더불어민주당 의원 당대표 비서실장 김태현 김건희 여사의 1심 선고가 있었습니다. 특검의 구형보다는 크게 못 미치는 형량이 선고되었는데요. 이에 민주당은 어떤 입장인지 한민수 더불어민주당 의원과 전화로 연결해서 이야기 나눠보겠습니다. 의원님, 안녕하세요. 한민수 안녕하세요. 서울 강북을 국회의원 한민수입니다. 김태현 의원님, 15년 구형인데 1년 8개월이거든요. 한민수 네. 김태현 그리고 3개 혐의 중에서 2개 무죄, 그다음에 통일교 관련된 건 하나만 유죄가 나왔습니다. 이거 어떻게 보셨어요? 어제 재판부 선고요. 한민수 정말 충격과 분노로 압축될 수 있을 것 같습니다. 말씀하신 것처럼 특검이 15년 구형했고요. 거기에 비해서 1년 8개월이 나왔는데요. 재판장이 김건희 씨에 대해서 이런 얘기를 합니다. 자신의 지위를 영리추구의 수단으로 오용했다. 그 지위라는 것은 윤석열 전 대통령의 배우자 영부인 신분을 이렇게 오용했다는 거지요, 악용했다는 얘기입니다. 김태현 네. 한민수 그리고 청탁과 결부된 고가의 사치품을 뿌리치지 못하고 수수해 자신의 치장에 급급했다. 이런 표현으로 질타를 하면서 이런 형량을 구형할 수 있는지 저는 도무지 이해할 수가 없습니다. 언론에서도 지금 전직 대통령 부부가 동시에 실형을 받은 헌정사 최초라고 하는 범죄를 저지른 것 아닙니까. 김태현 네. 한민수 저는 도대체 이해가 안 되는 게 보면 명품가방도 하나는 알선수재가 해당되고, 하나는 또 해당이 안 된다고 하고 있지요. 김태현 네. 한민수 그리고 도이치모터스 주가조작은 어제 1심 수사팀으로 활동했던 김태훈 대전고검장도 이건 부당한 판결이라고 하지 않았습니까. 증거가 차고 넘쳐요, 사실. 우리 국민들 다 알고 있습니다. 윤석열 검찰이 제대로 수사 안 했고, 이제 정권이 바뀌어가면서 수사를 하니까 바로 당시에 녹취됐던 녹취록도 다시 드러났고. 공소시효가 끝난 부분을 제외하더라도 이런 범죄를 단죄하지 않고 우리 지금 코스피 5000 시대에 그러면 뭘 어떻게 하라는 겁니까. 그래서 어제 정말 자조적인 우스갯소리 같은 거 알고 계시지요? 오늘 증권시장이, 주식시장이 좋지 않을 거다. 왜냐하면 대한민국의 1심 재판부가 앞으로는 주가조작해도 처벌하지 않는다 이걸 보여줬다는 거 아닙니까. 이런 판결을 어떻게 하는가 싶고요. 김태현 네. 한민수 그리고 윤석열 전 대통령이 분명히 얘기하지 않았습니까. 김영선 전 의원 공천과정에서 공천 좀 내가 해 줘라 하는데 당이 말이 많네. 내가 윤상현이한테 얘기했어. 이렇게 녹취록까지 나오는데 이게 공천개입이 없다? 명태균 여론조작 의혹은 무죄다. 이렇게 판결을 하면 우리 국민들이 저 판결에 대해서 어떻게 납득할 수 있을지. 제가 말씀드리다 보니까 또다시 분노가 치밀고 있는데요. 정말 이런 판결을 하는 건 아닌 것 같습니다. 김태현 의원님, 결국은 김건희 여사를 둘러싼 여러 가지 의혹들 중에서 가장 많이 알려졌던 게 두 개잖아요. 도이치모터스하고 명태균 씨요. 그 두 개가 다 무죄가 나온 건데요. 한민수 그렇습니다. 김태현 민주당 보기에 재판부가 소위 말해서 피고인 김건희 여사 쪽을 봐주기 판결해서 무죄가 나온 걸로 보세요, 아니면 민중기 특검의 수사능력 부족으로 그래서 이런 결과를 초래했다 이렇게 보세요? 어느 쪽에 책임이 크다고 보십니까? 한민수 어느 쪽을 딱 양단으로 한다기보다는요. 지금 보면 우리 국민들이 느끼는 건 특검이 15년 구형했을 때 그 형량도, 김건희 씨가 우리 국민들을 배신한 행위에 대해서는 그 구형 자체도 뭐 높지 않다 이런 판단을 한 거 아닙니까. 물론 김건희 씨 지금 재판이 두 개 정도 더 남아 있는 걸로 알고 있습니다, 1심이 또 있는데요. 이번 사법부 판단에 대해서 용납을 못 하겠다는 거지요. 그렇지 않습니까? 이게 단순히 특검이 무슨 지금 김건희 씨 변호인이 주장하는 것처럼 정치적으로 접근한 건 아니잖아요. 우리 5,000만 국민들이 모두 보고 들은 거 아닙니까. 다 들었어요, 그리고 눈으로 봤습니다. 그런데 여기에 대해서 변호인들의 그 논리라 할지, 뭐 어떤 부분은 상당히 이해... 예를 들어서 한번 말씀드려 보겠습니다. 도이치모터스 주가조작 혐의에 대해서 김건희 씨가 미필적으로나마 자기 자금이 시세조정에 동원될 것이라는 것을 인지하면서도 용인했다고 볼 여지가 없지 않다. 이게 무슨 말인지 잘 이해가 되십니까? 김태현 그러니까 재판부 얘기는 만약에 주가조작 방조범으로 기소했으면 유죄일 수 있다 뭐 이런 느낌인데요. 특검이 그냥 아예 방조범은 예비적으로도 생각을 안 해서. 한민수 그런데 이런 부분들은 항소하겠다고 특검이 밝혔으니까 저는 2심에서 바로잡힐 거라고 보는데요. 이게 보면 너무 많은 증거들과 이런 진술이라 할지. 김건희 씨 아까 말씀드린 대로 증권사 직원하고 통화할 때 녹음됐다는 것도 다 있었지 않습니까. 일관되지도 않고, 그다음에 주가조작 일당들에게 이례적으로 높은 수수료를 지급하기로 약정까지 했고요. 김태현 네. 한민수 그런데 이게 주가조작이 아니라고 무죄를 선고하는 건 저는 상식적이지 않은 것 같습니다. 김태현 의원님, 권성동 의원은 실형이 선고됐잖아요. 한민수 맞습니다. 김태현 통일교 관련된 거 징역 2년, 추징금 1억. 그러면 1억을 불법정치자금으로 받았다 이거를 재판부가 인정을 한 건데요. 이건 어떻게 평가하고 계세요? 한민수 물론 이 부분도 4년 구형해서 2년이 된 거지요. 형량이 제가 볼 때는 이 역시 좀 부족하지 않나 이런 생각이 듭니다. 하지만 2심에 가서 저는 더 무거운 처벌을 받을 거라고 보고요. 김태현 네. 한민수 이제 시작됐다고 봅니다. 왜냐하면 아시는 것처럼 우리나라 헌법 20조 2항은 분명하게 종교와 정치가 분리돼 있다고 하는 거 아닙니까. 이번 사건은 그 윤영호 통일교 전 세계본부장 씨나 권성동 의원 같은 경우는 우리 헌법을 정면으로 위배한 정교유착 사건입니다. 그래서 1심에서는 구형 선고가 이제 앞으로. 지금 검경합동수사본부도 발족돼서 수사를 활발하게 하지 않았습니까. 그리고 지금 국회에서 우리 민주당이 해야 된다고 요구하고 있는 통일교 신천지특검의 추진 당위성에도 더 힘이 실리지 않을까 이런 생각을 해 봅니다. 김태현 그러면 결국 이거 때문에 국민의힘이라는 정당 자체는 더 어려워질 거다 이 말씀이신 건데요. 그런데 전재수 의원도 본인은 당연히 지금 부인합니다. 그렇지만 어쨌든 통일교한테 금품받은 혐의로 지금 수사 중인 거잖아요. 그러면 실체관계야 수사 끝나는 거 보고 재판 봐야 되겠지만, 전재수 의원 수사에도 안 좋은 영향을 끼치는 거 아니에요? 한민수 저는 그렇게 보지 않습니다. 그건 뭐 여야의 문제도 아니고요. 제가 말씀드린 대로 정교유착을 근절하는 문제이고요. 저는 전재수 장관님 믿습니다. 장관직 던질 때는 너무 성급하지 않았나라는 판단을 했는데 지금 나오는 걸 보십시오. 전재수 장관처럼 떳떳한 사람이 있습니까? 그렇지 않습니까. 그래서 저는 전재수 장관이 전혀 관련되지 않았을 거라고 믿고 있고요. 김태현 네. 한민수 이 부분에 대해서는 저는 정치적으로 접근할 문제는 아니라고 봅니다. 국민의힘도 이게 본인들이 유착돼 있으면 이번 기회에 끊어내고, 새롭게 환골탈태할 생각을 해야지 이걸 가지고 정치적으로 통일교 특검만 하자 그러다가 신천지 관련된 정말 오랫동안 유착된 국민의힘과 신천지 간의 유착관계가 지금 백일하에 다 드러나고 있는 거 아닙니까. 그러다 보니까 뒤늦게 통일교와 신천지를 나눠서 특검을 하자 이걸 우리 국민들이 어떻게 받아들일 수 있겠습니까. 꼼수를 부리는 거거든요. 김태현 네. 한민수 그래서 권성동 의원이 누구입니까. 국민의힘이 그렇게 떠받들던, 국민의힘 의원들이 줄을 섰던 친윤 윤핵관의 핵심 중의 핵심 아닙니까. 이분이 1심에서 정교유착 혐의, 뇌물 혐의로 유죄를 받았습니다. 그러면 지금이라도 반성하고 제대로 된 수사에 협조를 하든지, 아니면 저희들이 요구하는 통일교 신천지 특검을 받든지 해야 된다고 봅니다. 김태현 알겠습니다. 당내 얘기 질문을 드려볼게요. 이해찬 전 총리 애도기간이 지나면 다 끝나면 민주당하고 조국혁신당 합당논의 이게 또다시 시작이 될 건데요. 민주당의 경우에 합당 여부를 전 당원 투표로 결정하는 거 맞아요? 한민수 누가 뭐 이렇게 전 당원으로 하자, 아니면 이거는 그냥 중앙위로 하자 그렇게 할 수 있는 게 아니고요. 우리 민주당 당헌에 명확하게, 정당의 합당과 해산은 중요한 문제 아닙니까. 그래서 거기에 대해서는 전 당원토론을 하고, 그다음에 전 당원 투표로 결정을 하도록 되어 있습니다. 그래서 우리 당원주권시대에 특히나 우리 당의 주인인 당원들께 의사를 물어야지요, 이렇게 중요한 문제는요. 그래서 찬성을 하면 거기에 따라서 수임기간을 정하든, 아니면 전 당원대회를 열든 이런 과정들을 밟아갈 것이고요. 김태현 네. 한민수 전 당원 투표를 했는데 우리 당원들께서 합당에 반대한다는 의견을 내시면 그 순간 멈추게 될 것입니다. 김태현 의원님, 이거 전 당원 투표의 정족수가 뭐 어떻게 돼요? 투표한 사람의 과반이면 되는 거예요? 왜냐하면 지난번 1인 1표 때도 과반은 넘었는데 그게 당헌당규에 따른 정족수 미달로 부결된 거잖아요. 한민수 규정을 제가 지금 정확하게 모르겠는데요. 이거는 찬반에 대한 의결 권한이기 때문에 당규에 결정기준이 있습니다. 따로 있고요. 김태현 그 기준이요. 한민수 조금 전에 우리 김 앵커 말씀하신 1인 1표 관련된 건 당무위와 중앙위를 거쳐서 확정되는 거기 때문에 이건 당에서 우리 당원들이 어떤 생각을 하는 건지 의견을 들어보는 겁니다. 그래서 성격에는 좀 차이가 있습니다. 김태현 어쨌든 전 당원 투표는 당헌당규에 규정된 정족수를 넘어야 통과가 되는 거란 말씀이신 거잖아요, 이게 효력 요건이니까요. 한민수 그렇게 알고 있습니다. 김태현 어떠세요? 찬성률이 높게 나올 걸로 보세요? 한민수 그거는 글쎄요. 지금 뭐 제가 보니까 여러, 김태현 반대하는 당원들도 꽤 계신 것 같아서요. 한민수 그럼요. 반대하시는 분들 당연히 있을 거라고 보고요. 그리고 우리 일부 최고위원들이나 의원님들 중에서도 합당 자체를 반대하시는 분들은 뭐 많지는 않은 것 같습니다. 김태현 네. 한민수 그런데 다만 이번에 합당이 제안되는 과정, 절차에 대한 이런 말씀들을 하시는 분들이 많이 있는데요. 저는 그런데 이게 합당을 제안하는 단계에서는 어떤 당대표, 저희 당내에서도 정무적으로 이렇게 많이 판단하시는 분들은 그런 의견을 의총에서도 내셨어요. 왜냐하면 이건 당대표의 정치적 결단으로 제안을 할 수밖에 없다. 사전에 이게 문제가 됐을 때는 성공할 확률이 더 낮아지지 않겠느냐, 공론화됐을 때. 그런 말씀들을 했는데요. 저는 지금부터는 정말로 저희들이 말씀하신 대로 이해찬 총리님 애도기간이 끝나면 17개 시도에서 일제히 당원들 토론이 있을 겁니다. 그래서 거기서 당원들께서 찬성과 반대에 대한, 아니면 본인이 생각하시는 의견들을 주시면 그 주신 의견들을 소중하게 받고, 그다음에 투표 절차가 있기 때문에 전 당원 투표를 하시면 거기에 따라 결정을 하면 될 것 같습니다. 김태현 그런데 의원님, 당이 정말 중요한 일을 결정하는 거니까 당연히 민주정당이니까 다양한 의견이 있을 수 있는데요. 한민수 그렇습니다. 김태현 어제 한준호 의원을 제가 인터뷰를 했습니다. 그런데 한준호 의원 얘기는 기본적으로 민주개혁정당이 하나가 돼야 된다는 건 동의한다. 그런데 시기하고 속도, 방법이 너무 거칠다. 왜 이해당사자가 많은 지방선거를 앞두고 해야 되느냐. 이렇게 얘기했거든요. 그런데 한준호 의원만이 아니고 김민석 총리도 다른 방송에서 인터뷰 얘기한 거 보면 시점과 방식에 논란이 있을 수 있다. 이렇게 얘기해요. 주로 이재명 대통령하고 가까운 정치인 쪽에서 이런 얘기들이 계속 나오거든요. 합당 자체는 동의하지만 시기와 방식의 문제. 이런 얘기 계속 나오는 건 어떻게 생각하세요? 한민수 일단 방식이라는 건 지금 말씀드린 대로 어느 당대표가 되든 합당을 조국혁신당이 됐든 우리 같은 진보진영, 민주진영이 모두 힘을 합쳐야 된다는 그 당위성에 대해서는 모두 인정하시는 거 아니겠습니까. 김태현 네. 한민수 그런데 방식은 당대표가 합당을 제안하기 전에 그러면 내가 합당을 제안할 생각이니까 한번 논의를 해 보자 이런 방식이 있을 테고, 지금 방식을 따진다면요. 아니면 전격적으로 합당을 제안해놓고 본격적으로 논의하는 것이 있을 겁니다. 그러면 실제로 제가 조금 전에 말씀드린 것처럼 어느 방법이 합당을 성사시키는 데 더 높이는 방법일 건가 이건 생각들이 다를 겁니다. 그렇지요? 김태현 네. 한민수 그런 부분에 대해서는 지금 당대표가 결단을 하고 제안한 다음에 논의하는 부분들이 그전보다 미리 얘기했을 때 반대하는 의견들이 많이 나오지 않겠습니까. 그런 과정에서 실제 합당을 추진도 못 하고 무산될 가능성도 예전 사례도 보면 적지 않아 있었던 것 같습니다. 그래서 그런 부분들이 있고요. 그러면 시기는 어떠냐 이런 게 남지 않겠습니까. 그런데 저는 우리 당내 의원님들하고도 많이 소통을 해 봤는데 더 빨리 했어야 된다는 의견도 있거든요. 그런데 지방선거를 앞두고 저는 지금이 아니면 다음 2028년도 총선이라 할지 2030년 대선을 가서는 더 어렵지 않겠나 이런 쪽에 더 무게를 두고 있습니다. 김태현 왜요? 한민수 이게 지방선거 거치면 김 앵커도 아시겠습니다마는 선거를 17개 시도에서, 이번 지방선거도 또 작은 단위에서 다 이루어지지 않겠습니까? 그러면 거기에도 조국혁신당 후보가 나올 것이고, 그러면 또 치열한 경쟁을 하다 보면 일종의 어떤 이견이라 할지 감정의 골도 더 깊어지는 경우도 많이 있습니다. 그리고 지금 무엇보다도 이번 6.3 지방선거에 대해서는 우리 민주당 정말 이재명 정부 성공을 위한 저는 가장 중요한 분수령, 출발점, 계기라고 보고 있습니다. 그렇기 때문에 6.3 지방선거 승리를 위해서는 한 사람의 힘이라도 모두 힘을 뭉쳐서요. 김태현 네. 한민수 지금 보십시오. 아까 앞서서, 그러니까 국민의힘은 지금 뺄셈의 정치를 하고 있는 거 아닙니까. 잘 되지도 않는 정당에서 누구 자르겠다 그러고 있는데요. 우리 민주진영인 민주당은 한 사람의 힘이라도 모아서 우리 이재명 대통령님 성공을 위해서 뒷받침하겠다. 그게 목표이자 지상과제라고 생각합니다. 김태현 알겠습니다. 의원님, 합당 관련해서 마지막으로 질문 하나 더 드릴 건데요. 이게 아마 근본적인 문제일 수도 있는데요. 어제 한준호 의원의 얘기입니다. 이재명 대통령이 당대표 시절부터 실용과 중도우파를 말해왔는데 그 점에 대한 논의가 충분했느냐 여기서부터 이야기를 시작해야 된다. 이 얘기는 조국혁신당이 민주당보다 훨씬 더 진보적인데, 조국혁신당이 지금 민주당에 들어오는 게 이재명 대통령이 지금 추구하고 있는 국정운영 방향과 맞느냐 이걸 한번 봐야 된다는 얘기인 것 같거든요. 이거 어떻게 보세요? 한민수 물론 그런 의견이 있을 수도 있는데요. 가령 저희들이 최근 들어서 국회에서 여러 현안, 법안들이 있지 않습니까. 처리를 하려고 할 때 대통령도 여러 차례 지적하셨던 가령 옥외광고물법이라는 게 있습니다. 정말 말도 안 되는 중국과 관련된다든지, 대통령 사생활을 아주 모욕적으로 왜곡해서 정말 모욕감을 주는 현수막들이 많이 붙었잖아요. 그걸 저희들이 처리하려면 옥외광고물법을 처리해야 됩니다. 그리고 국회에 말도 안 되는 국민의힘에 필리버스터, 무제한 토론을 좀 개선하기 위해서는 국회법부터 처리해야 됩니다. 그리고 제가 소속된 과방위의 허위조작정보 근절을 위한 정보통신망법 개정할 때도 우리 조국혁신당이 다 관점이 좀 달랐습니다. 그리고 처리하는 의견도 달랐고요. 그래서 저희들이 지금 처리가 안 되는 개혁법안도 많이 있습니다. 김태현 네. 한민수 그러면 합당을 제안하고, 우리 당원들께서 찬성을 해서 정말 한 민주당으로 다 모였을 때 그런 쟁점법안도 내부에서 치열하게 논의하고 또 결론을 냅니다. 그래서 힘 있게 추진하고요. 이게 개혁 민생 실용법안인 겁니다. 그렇게 해서 이재명 정부를 뒷받침하는 것이 훨씬 더 효용적이지 않겠나 저는 그런 생각을 해 봅니다. 김태현 의원님, 알겠습니다. 오늘 인터뷰는 여기서 마무리하도록 하겠습니다. 지금까지 더불어민주당 당대표 비서실장인 한민수 의원이었습니다. 감사합니다. 한민수 고맙습니다. 인터뷰 자료의 저작권은 SBS 라디오에 있습니다. 전문 게재나 인터뷰 인용 보도 시, 아래와 같이 채널명과 정확한 프로그램명을 밝혀주시기 바랍니다. SBS 김태현의 정치쇼	https://n.news.naver.com/mnews/article/055/0001328483?sid=100	1	["https://imgnews.pstatic.net/image/055/2026/01/29/0001328483_002_20260129103710683.jpg?type=w860"]	2026-01-29 10:35:36	2026-01-29 01:38:49.21284	\N	t	1
2	박원석 "김건희 선고, 술 마셨고 운전도 한 것 같은데 음주운전이 아닌 것 같다고 한 것"	서울중앙지방법원은 어제 28일 김건희 씨에게 적용된 세 가지 혐의 중 두 가지를 무죄로 판단하고 징역 1년 8개월을 선고했습니다. 무죄로 판단된 혐의는 도이치모터스 주가조작 가담 혐의와 명태균 여론조사 수수 혐의입니다. 박원석 전 의원은 재판부 판결 과정을 두고 술은 마셨지만 음주운전은 아니라는 것 같다 고 평가했습니다. 핵심 의혹들에 내려진 무죄 판결을 두고 재판부의 모순을 지적하기도 했습니다 . 김건희 씨는 1심 재판에서 징역 1년 8개월에 추징금 1281만원을 선고받았습니다. 특검의 구형량이었던 징역 15년에 훨씬 못 미치는 수준이었습니다. 박원석 전 의원은 판결 전반에 대해 이렇게 평가했습니다. 박원석 전 정의당 의원 SBS 라디오 김태현의 정치쇼 전체적인 느낌이 그 생각이 났어요. 술은 마셨고 운전도 한 것 같은데 음주운전이 아닌 것 같다. 김건희 씨가 받는 의혹과 관련해 무죄가 선고된 걸 비판한 겁니다. 재판부는 김건희 씨에게 적용된 모두 세 가지 혐의 중 두 가지에 대해선 무죄를 선고했습니다. 박 전 의원은 김건희 씨의 도이치모터스 주가조작 가담 혐의를 인정하지 않은 것은 재판부의 모순이라 지적했습니다. 박원석 전 정의당 의원 SBS 라디오 김태현의 정치쇼 재판장 낭독한 내용에 보면, 주가조작을 인지했다, 그러고 수용했다, 본인이 맡긴 돈이 이용됐다는 걸 알지만 공동정범이 아니다? 이건 형용 모순이잖아요. 명태균 씨에게 무상으로 여론조사를 제공받은 혐의에 대해 무죄가 선고된 것 역시 납득하기 어렵다고 설명했습니다. 박원석 전 정의당 의원 SBS 라디오 김태현의 정치쇼 그게 무죄면, 도대체 내가 윤 상현이한테 얘기해서 주라고 할게 그건 뭐가 됩니까? 그런 식으로 그럼 공천에 개입해도 돼요? 어제 28일 선고 직후 김건희 특검팀은 법리적, 상식적으로 납득이 어렵다며 항소 의사를 밝혔습니다.	https://n.news.naver.com/mnews/article/437/0000475826?sid=100	2	["https://imgnews.pstatic.net/image/437/2026/01/29/0000475826_001_20260129103511865.jpg?type=w860"]	2026-01-29 10:35:11	2026-01-29 01:38:49.219577	\N	t	1
3	민주·조국혁신당, 합당 실익 집중 분석 [오늘 이슈전파사]	1부선 정원오 서울 성동구청장 출연 정원오 서울 성동구청장이 29일 한국일보 시사 유튜브 이슈전파사 를 찾는다. 정 구청장은 더불어민주당 서울시장 후보로 거론되는 인물 중 하나다. 이날 2부에선 여의도 브라더스 김정현ㆍ김도형 기자가 출연해 민주당과 조국혁신당 합당의 이해득실을 과거 선거 득표 수 분석을 통해 설명한다. 이슈전파사 는 매주 화ㆍ수ㆍ목 오전 11시부터 유튜브와 다음에서 실시간 시청할 수 있다. 2월부터는 평일 저녁 6시로 방송 시간을 옮길 예정이다. 전체 인터뷰 내용은 한국일보 유튜브 이슈전파사 에서 확인하실 수 있습니다. 이슈전파사 의 콘텐츠 저작권은 한국일보에 있습니다. 인용 시 한국일보 유튜브 이슈전파사 출처를 반드시 밝혀주시기 바랍니다. 시사 유튜브 이슈전파사 구독하기 www.youtube.com thehankookilbo 만든 사람들 진행ㆍ구성 김지은 기자 출연 1부 정원오 성동구청장, 여의도 브라더스 김정현ㆍ김도형 기자 2부 여의도 브라더스 PD 안재용 김광영 박채원 PD AD 이예원 최지원 인턴PD 디자인 전세희 모션그래퍼	https://n.news.naver.com/mnews/article/469/0000911632?sid=100	3	["https://imgnews.pstatic.net/image/469/2026/01/29/0000911632_001_20260129103713092.jpg?type=w860", "https://imgnews.pstatic.net/image/469/2026/01/29/0000911632_002_20260129103713172.png?type=w860"]	2026-01-29 10:37:13	2026-01-29 01:38:49.223204	\N	t	1
4	반크 "한류는 세계 문화"…한국 홍보 '청년 공공외교대사' 모집	사이버 외교사절단 반크와 국가기간뉴스통신사 연합뉴스는 한국의 역사와 문화 등을 세계에 바르게 알릴 제13기 청년 공공외교대사 를 모집한다고 29일 밝혔다. 반크는 다음 달 8일까지 국내외 중 고등학생 및 대학생을 대상으로 지원서를 받는다. 희망자는 온라인 안내 페이지 http prkorea.com yna 내 신청하기 메뉴로 들어간 뒤 지원서를 작성해서 제출하면 된다. 심사를 거쳐 다음 달 13일에 100명을 선발할 예정이다. 합격자는 2월 25일 오전 11시 서울 종로구 연합뉴스 본사 17층 연우홀에서 열리는 발대식과 교육에 참여해야 한다. 이들은 이후 3월 27일까지 약 한 달 동안 한국 역사와 문화 디지털 콘텐츠 기획 및 제작에 참여하고, 디지털 홍보 기획 및 활동을 하게 된다. 우수한 활동을 한 청년에게는 청년 공공외교대사 임명장이 수여된다. 반크와 연합뉴스는 매년 한국을 국내외에 제대로 알려 국가의 브랜드를 높이자는 취지로 진행하는 국가브랜드업 전시회 를 열면서 청년 공공외교대사를 양성해왔다. 올해는 2월 25일부터 3월 2일까지 서울 용산구 국립중앙박물관 지하보도 나들길에서 한류, 세계 문화가 되다 를 주제로 전시회를 선보인다. 반크는 한류는 이제 K팝과 드라마를 넘어 한국의 역사와 정신을 전하는 디지털 공공외교의 무대로 확장하고 있다 며 한국 문화의 확장과 세계와의 연결은 기관이나 콘텐츠의 힘만이 아니라 일상에서 한국을 소개하고 교류하는 시민과 청년의 참여로 완성된다 고 설명했다. 그러면서 100년 전 독립운동가들이 세계에 조국의 진실을 알렸듯, 오늘의 우리는 공공외교대사로서 한류가 세계 문화의 중심이 되도록 한국의 진실과 가치를 세계에 전해야 한다 고 덧붙였다. 반크는 2026 국가브랜드업 전시회 전시해설사 30명도 모집한다. 다음 달 8일까지 신청을 받으며, 2월 13일 대상자를 최종 선정한다. 이들은 전시회 기간에 외국인 및 한국인에게 전시회를 안내하고, 반크 활동을 소개하며, 이벤트를 진행하는 등의 활동을 하게 된다. 신청 희망자는 구글 폼 prkorea.com ynads 을 통해 지원서를 작성하면 된다.	https://n.news.naver.com/mnews/article/001/0015873426?sid=100	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129073500371_01_i_P4_20260129103717558.jpg?type=w860", "https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129073500371_02_i_P4_20260129103717561.jpg?type=w860"]	2026-01-29 10:36:49	2026-01-29 01:38:49.226753	\N	t	1
5	SK하이닉스 "메모리 수요 폭증을 공급이 못 따라가는 실정"	AI 인프라 투자 확대로 수요 폭증했지만 업계 공급 능력 못 따라가 불균형 극심 SK하이닉스는 인공지능 AI 인프라 투자 확대에 따른 극심한 메모리 수급 불균형이 발생하고 있다 고 29일 밝혔다. SK하이닉스는 이날 지난해 4분기 실적발표 컨퍼런스콜에서 AI 인프라 투자 확대로 수요가 폭발적으로 증가하고 있으나 업계 공급 능력이 이를 따라가지 못하고 있다 면서 이같이 전했다. SK하이닉스는 고객사 대부분이 메모리 확보에 어려움을 겪고 있어 하반기로 갈수록 재고 부족 현상이 심화할 것으로 전망했다. 특히 서버 고객의 경우 물량이 확보되는 즉시 세트 제작으로 이어져 재고 수준이 지속적으로 하락하고 있다는 설명이다. PC와 모바일 분야 역시 서버향 수요 강세에 따른 공급 제약의 영향을 받고 있다고 회사는 전했다. SK하이닉스는 서버 D램을 중심으로 한 타이트한 재고 추세가 연중 지속될 것 이라며 대부분 고객이 메모리 물량 확보에 어려움을 겪고 공급 확대를 요구하고 있다 고 했다. HBM4 시장에 대한 자신감도 드러냈다. SK하이닉스는 HBM4 역시 HBM3나 HBM3E와 마찬가지로 압도적 시장 점유율을 목표로 한다 며 그동안 쌓아온 양산 경험과 품질에 대한 고객 신뢰는 단기간에 추월할 수 없는 영역 이라고 강조했다. 현재 고객사와의 협의 일정에 맞춰 양산을 준비 중이며, 독자적인 MR MUF 패키징 기술을 통해 수율과 성능을 동시에 확보한다는 방침이다. 경쟁사인 삼성전자의 HBM4 시장 진입 가능성에 대해서는 현재 생산력을 극대화해도 고객 수요를 100 충족하기 어려운 상황이라 일부 경쟁사의 진입이 예상된다 면서도 성능과 양산성 기반의 주도적 공급사 지위는 지속될 것 이라고 밝혔다. 한편 SK하이닉스는 지난해 연결 기준 매출 97조1467억원, 영업이익 47조2063억원을 기록하며 역대 최고 연간 실적을 경신했다. 4분기 매출은 32조8267억원, 영업이익은 19조1696억원으로 집계됐다. 각각 기존 최고 실적이었던 직전 분기 대비 34 , 68 증가한 수치다.	https://n.news.naver.com/mnews/article/015/0005243899?sid=101	5	["https://imgnews.pstatic.net/image/015/2026/01/29/0005243899_001_20260129103720837.jpg?type=w860"]	2026-01-29 10:37:20	2026-01-29 01:38:49.230972	\N	t	2
26	[컨콜] 삼성전자 “HBM4 등 차별화된 경쟁력 입증… 파운드리 대형 수주 연이어 성공”	삼성전자는 29일 열린 2025년 4분기 실적발표 컨퍼런스 콜에서 6세대 고대역폭메모리 HBM4 , 그래픽D램 GDDR7 등 글로벌 경쟁력을 갖춘 제품을 개발해 고객들이 삼성이 돌아왔다는 평가를 주고 있다. 차별화된 성능 경쟁력을 입증했다고 생각한다 며 파운드리 반도체 위탁생산 는 기술과 신뢰를 바탕으로 대형 글로벌 고객사 수주를 연이어 성공하면서 본격적인 도약을 시작했다 고 했다.	https://n.news.naver.com/mnews/article/366/0001139177?sid=105	10	[]	2026-01-29 10:33:14	2026-01-29 01:38:49.332569	\N	t	6
6	'서민금융 잇다' 앱으로 지난해 이자비용 376억원 절감	서민금융 종합플랫폼인 서민금융 잇다 앱을 통해 지난해 380억원에 가까운 이자비용이 절감됐다고 29일 서민금융진흥원이 추산했다. 이 앱은 67개 금융회사의 105개 정책서민금융과 일반신용대출상품의 지원대상 금리 한도 등 상품조건을 고객에게 유리한 최적 상품 순서로 한 번에 안내해주고, 고용복지 복합지원을 비대면으로 제공해주는 플랫폼이다. 서금원에 따르면 지난해 이 앱의 이용자 수는 총 665만명이었고, 이들에게 지원한 서민금융 서비스 건수는 총 259만건으로 집계됐다. 월평균 이용 건수는 21만6천건으로 전년 19만1천건 보다 13 이상 늘었다. 지난해 이 앱에서 금융상품을 비교한 뒤 실행한 대출 금액은 6천292억원이었고, 평균 금리는 8.2 수준이었다. 서금원은 대출 중개금액 6천292억원 과 고금리 대부업 대출의 평균 이자 14.2 에서 이 앱의 대출상품 평균 금리 8.2 를 뺀 금리 인하 효과분 6 p 을 고려할 때 총 376억원의 이자비용이 절감됐다고 봤다. 인당 이자비용 절감액은 28만4천원이다. 서민금융 잇다 앱 서비스 이용자 중 대다수 92.8 는 신용평점 600 800점대의 중 저신용자였다고, 연령대는 비대면 서비스에 익숙한 20 30대 61.5 가 절반 이상이었다. 대출 용도는 생활자금 목적이 72.2 로 가장 많았고, 신청 금액은 1천만원 이하가 65 를 차지했다. 김은경 서금원장은 서민금융 잇다 앱이 서민들의 금융뿐 아니라 복합적 어려움을 해소할 수 있는 플랫폼으로 자리잡아가고있다 면서 연계상품을 확대하고 서비스도 지속해서 개선해 서민들의 금융 접근성과 편의성을 강화하겠다 라고 말했다.	https://n.news.naver.com/mnews/article/001/0015873430?sid=101	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129071000002_01_i_P4_20260129103820813.jpg?type=w860"]	2026-01-29 10:37:36	2026-01-29 01:38:49.240573	\N	t	2
7	현빈, 48억 빌딩 투자…13년 만에 196억 됐다 [집코노미-핫!부동산]	배우 현빈이 꼬마빌딩 으로 최소 150억원가량의 시세 차익을 거둘 수 있다는 관측이 나왔다. 29일 부동산 플랫폼 밸류맵에 따르면 지난 27일 기준 현빈의 꼬마 빌딩 예상 시세는 196억9000만원이었다. 이는 인근 지역 매매 가격과 지형, 건물 가치 등을 고려해 책정됐다. 현빈이 해당 건물을 2013년 9월 48억원에 매입한 점을 고려하면 13년 만에 150억원가량의 시세 차익을 기대할 수 있다. 현빈의 건물은 서울 강남구 청담동 도산대로 이면에 위치하고 있다. 당시 현빈은 대지면적 109.66평 노후 다세대 주택을 가족 법인 명의로 매입했고, 2015년 지하 4층 지상 7층 높이의 꼬마빌딩 연면적 481평 을 직접 신축했다. 현재 이 건물의 3개 층은 현빈의 소속사가 사용하고 있다. 식당과 미용실 등 상업 시설 임차인도 들어와 있다. 현빈은 대출 없이 전액 현금으로 건물을 새로 지었고, 현재도 대출금은 없는 상태다. 매입가 48억원과 철거 설계 감리 비용과 예상 신축 비용 25억원, 기타 부대비용까지 더한 매입 원가는 당시 약 80억원 정도로 추정됐다. 더불어 해당 건물의 디자인을 인정받아 2017년 서울시 건축 우수상을 받았다. 현빈은 꾸준히 안정적으로 부동산 투자를 해왔다는 평을 받아 왔다. 2009년에는 서울 동작구 흑석동의 한 고급 빌라를 27억원에 매입해 2021년 40억원에 매각했다. 또한 2020년 6월 경기 구리시 아천동 워커힐포도빌 펜트하우스 전용면적 330 약 100평 를 매입했다. 분양받은 이후 소유권 이전은 다음 해인 2021년 1월6일에 마무리됐다. 당시에도 현빈은 전액 현금으로 잔금을 지불했고, 배우 손예진과 결혼 후 신접살림을 차렸다. 이후 2024년 70억원에 해당 집을 매물로 내놓은 사실이 알려졌다. 현빈은 최근 진행된 디즈니플러스 메이드 인 코리아 인터뷰에서 해당 자택 매각 여부에 노코멘트 하겠다 고 답했지만, 현재 거주 중인 것은 아니다 라고 말했다. 현빈의 아내 손예진 역시 연예계 부동산 투자의 귀재로 불린다. 2008년 30억원에 매입한 서울 강남구 삼성동 빌라를 2023년 48억원에 매도해 18억원의 양도차익을 얻어 화제가 됐다. 당시 손예진은 현빈과 결혼한 직후였는데, 부동산업계에서는 이들 부부가 혼인한 날로부터 5년 내 주택 하나를 매도할 경우 1가구 1주택 12억원의 비과세 적용을 받을 수 있어 매도를 결정한 것으로 봤다. 손예진은 2015년에는 마포구 서교동 빌딩을 93억5000만원에 사들여 2018년 2월 135억원에 매도했다. 이후 2020년 강남구 신사동 빌딩을 160억원에 매입했고, 2022년 강남구 역삼동 빌딩을 244억원에 매입했다.	https://n.news.naver.com/mnews/article/015/0005243898?sid=101	5	["https://imgnews.pstatic.net/image/015/2026/01/29/0005243898_001_20260129103716094.jpg?type=w860"]	2026-01-29 10:37:16	2026-01-29 01:38:49.245878	\N	t	2
8	코레일, 지난해 '지역사랑 철도여행' 22만명 이용	한국철도공사 코레일 는 대표 여행상품인 지역사랑 철도여행 을 이용한 고객이 지난해 22만명을 넘어섰다고 29일 밝혔다. 2024년 8월 출시한 이 상품은 협약을 맺은 인구감소지역 42곳의 열차 운임을 50 할인해 주고, 관광명소 체험 혜택 등을 결합한 상품이다. 지난해 월평균 이용 인원은 판매 첫해 약 1만명의 2배인 약 2만명으로 늘었으며, 누적 이용객은 26만명을 달성했다. 지역사랑 철도여행과 임시열차 등을 포함해 기차여행으로 42개 인구감소지역을 찾은 인원도 약 2배 증가했다. 경제적 파급효과로 환산하면 모두 825억원의 생산유발효과를 낸 것으로 추산된다고 코레일 측은 설명했다. 가장 많이 찾은 지역은 전북 남원 2만3천여명 이고, 경남 밀양 2만여명 , 충북 영동 1만9천여명 순이다. 코레일은 지자체뿐만 아니라 한국농어촌공사, 한국관광공사 등 관계기관과 협력해 디지털관광주민증 연계, 농촌투어패스 시행 등 상품을 다각화한 것을 인기 요인으로 꼽았다. 이민성 코레일 고객마케팅단장은 인구감소지역 생활인구 증가에 실질적인 도움이 될 수 있도록 지자체, 유관기관과 협력을 확대하고 지역 균형 발전을 적극 지원하겠다 고 말했다.	https://n.news.naver.com/mnews/article/001/0015873428?sid=102	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129074300063_01_i_P4_20260129103817215.jpg?type=w860"]	2026-01-29 10:37:19	2026-01-29 01:38:49.251558	\N	t	3
9	'차명' 공천헌금 부탁한 김경…전 후원회장마저 "거절했다"	김경 전 서울시의원이 정치인들에게 차명 후원을 했다는 의혹이 제기된 가운데, 자신의 후원회장을 맡았던 인물에게 대신 후원금을 입금해달라고 요청한 정황이 드러났습니다. 28일 YTN은 2023년 강서구청장 보궐선거 공천 로비 의혹과 관련한 녹취에 김 전 시의원이 지인에게 차명 후원을 부탁한 정황이 담긴 것으로 파악됐다고 보도했습니다. 매체에 따르면 당시 전화를 받은 인물은 숭실대 교수 A 씨입니다. A 씨는 재작년 9월쯤부터 반년 정도 김 전 시의원의 후원회장을 맡았던 것으로 전해졌습니다. 통화 시점은 2023년 7월 4일로, 김 전 시의원이 더불어민주당 소속 B의원을 면담한 날인 것으로 알려졌습니다. 김 전 시의원은 A 씨에게 자신이 돈을 보내면 해당 의원 후원 계좌에 대신 입금해줄 수 있느냐고 물었고, A 씨는 자신의 남편 계좌로 송금하면 돈을 보내겠다는 취지로 답한 것으로 전해졌습니다. A 씨는 당시 김 전 시의원이 전화해 특정 계좌로 돈을 넣어달라고 요구한 건 맞다고 밝혔다고 매체는 보도했습니다. 다만 이런 부탁이 부적절해 보여 분명히 거절했다며, 후원 대상이 누구였는지도 기억나지 않는다고 설명한 것으로 전해졌습니다. A 씨는 또 김 전 시의원이 불특정 다수 아무에게나 전화했던 거라며, 자신은 시의회 일을 몇 번 돕다 후원회장을 맡게 됐을 뿐 실질적인 권한이나 이익도 없었고 김 전 시의원과는 업무상 안면이 있는 수준이라고 밝혔다고 매체는 전했습니다. 그런데 같은 날 김 전 시의원의 또 다른 지인 이름으로 B 의원 후원 계좌에 500만 원이 입금된 사실이 확인된 것으로 알려졌습니다. B 의원은 당시 김 전 시의원을 면담했지만, 강서구청장 출마 의사가 있는 사람들을 잇따라 만나던 중이라고 밝혔다고 매체는 전했습니다. B 의원은 또 출마 의사를 밝히는 김 전 시의원에게 현역 시의원인 만큼 출마를 만류했으며, 500만원 후원자가 김 전 시의원의 지인인 것도 몰랐다는 입장인 것으로 전해졌습니다. 김 전 시의원이 강선우 의원에게 이른바 쪼개기 후원을 했다는 의혹이 제기된 데 대 이어 차명 후원 의혹까지 불거지면서 경찰 수사가 확대될 것으로 보입니다.	https://n.news.naver.com/mnews/article/437/0000475827?sid=102	2	["https://imgnews.pstatic.net/image/437/2026/01/29/0000475827_001_20260129103711953.jpg?type=w860"]	2026-01-29 10:37:11	2026-01-29 01:38:49.2562	\N	t	3
10	[게시판] KB국민카드, 교육비 특화 'KB NEED 에듀 카드' 출시	KB국민카드가 교육 관련 업종 중심으로 할인 혜택을 강화한 KB NEED Edu 카드 를 출시한다고 29일 밝혔다. 해당 상품은 KB국민카드가 최근 브랜드 체계를 올 유 니드 ALL YOU NEED 3개 라인으로 개편한 데 맞춰 내놓은 것으로 교육 관련 소비가 많은 고객을 타깃으로 한다. 할인 대상에 일반학원 업종뿐 아니라 학습지 업종도 포함된다. 전월 이용실적에 따라 교육 관련 업종 결제 금액의 5 가 할인된다. 병원 약국 커피 등 생활 밀착형 업종에서도 각종 할인 혜택을 받을 수 있다. 연회비는 국내 전용 2만5천원, 국내외 겸용 2만6천원이다. 서울 연합뉴스	https://n.news.naver.com/mnews/article/001/0015873432?sid=102	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129073700002_01_i_P4_20260129103824127.jpg?type=w860"]	2026-01-29 10:37:53	2026-01-29 01:38:49.261049	\N	t	3
11	경찰, ‘김병기 인사 개입’ 연루 의혹 쿠팡 압수수색	김병기 무소속 의원 전 더불어민주당 의 쿠팡에 대한 업무방해 혐의를 수사 중인 경찰이 강제수사에 나섰다. 서울경찰청 공공범죄수사대 대장 박삼현 는 29일 오전 9시40분부터 서울 송파구 쿠팡 본사와 서초구 쿠팡 사회공헌위원회 사무실을 압수수색하고 있다고 밝혔다. 김 의원은 지난해 9월 국회 국정감사를 앞두고 박대준 당시 쿠팡 대표와 안병기 대외협력총괄부사장 등을 서울 여의도의 한 호텔에서 만나 오찬을 함께 했다. 김 의원은 당시 오찬에서 쿠팡에 취업한 자신의 전직 보좌직원들과 관련된 자료를 건네며, 이들에 대한 인사상 불이익을 압박했다는 의혹을 받는다. 당시 김 의원은 집권여당인 민주당의 원내대표였고, 총 오찬 비용이 70만원에 달해 청탁금지법 위반 의혹도 제기됐다. 다만 김 의원은 당시 자신의 식사 비용이 3만8천원이라고 반박한 바 있다. 이날 본사와 함께 압수수색이 진행된 쿠팡 사회공헌위원회는 쿠팡의 대외협력조직인 대관팀 이 주로 근무하던 곳으로, 김 의원의 전직 보좌관 중 일부도 이곳에서 일했던 것으로 알려졌다. 오찬 뒤 실제로 이들 전직 보좌직원들은 해외로 발령되거나 해고 처리된 것으로 전해졌다.	https://n.news.naver.com/mnews/article/028/0002788918?sid=102	6	["https://imgnews.pstatic.net/image/028/2026/01/29/0002788918_001_20260129103816253.jpg?type=w860"]	2026-01-29 10:38:16	2026-01-29 01:38:49.264436	\N	t	3
12	크라운해태, 국악 공연 '한음회' 개최…전국 순회 돌입	크라운해태제과는 임직원이 참여한 국악 공연인 제7회 크라운해태 한음회 를 어제 28일 광주예술의전당 대극장에서 열었다고 오늘 29일 밝혔습니다. 이번 공연은 종묘제례일무 전폐희문 으로 시작해 가곡 우조우편 봉황대상 , 12가사 중 매화가 , 판소리 인생백년 , 농부가 , 진도아리랑 등 무대로 이어졌습니다. 윤상미 명무는 궁중정재 춘앵전 으로 관객과 만나 공연의 완성도를 높였습니다. 크라운해태제과는 지난해 광역시를 중심으로 4회 열렸던 한음회 공연을 올해 전국 중소도시까지 포함해 총 16회로 대폭 늘릴 예정입니다. 크라운해태제과 관계자는 올해 한음회 공연의 첫 시작을 광주 고객들과 함께해 기쁘다 며 광주를 시작으로 전국을 순회하며 고객들에게 울림 있는 우리 소리를 들려드리도록 노력할 것 이라고 밝혔습니다. 크라운해태제과 국악공연 한음회 연합뉴스TV 기사문의 및 제보 카톡 라인 jebo23	https://n.news.naver.com/mnews/article/422/0000827979?sid=103	7	["https://imgnews.pstatic.net/image/422/2026/01/29/AKR20260129103354AhX_01_i_20260129103415000.jpg?type=w860"]	2026-01-29 10:34:15	2026-01-29 01:38:49.268106	\N	t	4
13	평창군-원주세브란스기독병원, 공공보건의료 협력 강화 협약	강원 평창군보건의료원은 연세대학교 원주세브란스기독병원과 지역 의료서비스의 질적 향상과 공공보건의료 기능 강화 및 상호 협력을 위한 업무협약 MOU 을 했다고 29일 밝혔다. 양 기관은 비대면으로 진행한 협약을 통해 상호 존중과 신의 성실의 원칙을 바탕으로 지역 주민의 건강 증진과 지속 가능한 의료체계 구축을 위해 공동 노력을 기울이기로 했다. 협약의 주요 내용은 평창군보건의료원 내 미충족 진료과에 대한 원주세브란스기독병원 의료진의 파견 진료, 건강 증진 관련 연구 및 교육사업 수행, 상호 환자의뢰 및 회송 체계 구축, 공공보건의료 관련 사업 추진 등이다. 또 양 기관은 협약의 목적을 성실히 수행하기 위해 긴밀히 협의하고, 사업 추진 과정에서 취득한 개인정보 및 기관 보안 사항을 철저히 보호하기로 합의했다. 이번 협약을 통해 평창군은 지역 내 공백 진료과목의 문제를 완화하고, 양질의 의료 서비스를 제공할 수 있을 것으로 기대한다. 원주세브란스기독병원 역시 지역 공공보건의료의 발전에 이바지함으로써 상생의 의료 생태계를 구축하는 데 힘을 보탤 예정이다. 박건희 평창군보건의료원장은 이번 협약은 지역 의료 접근성 향상에 큰 도움이 될 것 이라며 앞으로도 공공의료 역량 강화와 군민 건강 증진을 위해 최선을 다하겠다 고 말했다.	https://n.news.naver.com/mnews/article/001/0015873408?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129073900062_01_i_P4_20260129103414780.jpg?type=w860"]	2026-01-29 10:34:03	2026-01-29 01:38:49.272992	\N	t	4
14	“눈꽃이 길이 되는 곳, 대관령 옛길로 설경 감상하러 오세요”···강릉시 2월 추천 여행지 선정	강원 강릉시는 2월의 추천 여행지로 대관령 옛길 을 선정했다고 29일 밝혔다. 강릉은 바다와 산악 지형을 동시에 품은 도시다. 겨울철에는 해안과 내륙의 풍경이 뚜렷한 대비를 이루는 것이 특징이다. 특히 2월의 경우 대관령을 비롯한 백두대간 고지대에 아름다운 설경이 펼쳐져 눈꽃 트레킹을 즐기기 좋은 시기다. 이에 따라 강릉시는 겨울의 매력을 가장 잘 체감할 수 있는 대관령 옛길 을 추천 여행지로 선정했다. 대관령 옛길 은 예로부터 숱한 사연을 간직해온 곳이다. 길 자체가 문화유산인 대관령 옛길은 고려 시대부터 강릉의 관문이었다. 이곳에는 천년 축제인 강릉단오제의 출발지인 국사서낭당과 산신각이 자리 잡고 있다. 대관령 휴게소에서 강릉시 성산면 어흘리 마을 어귀까지 이어지는 대관령 옛길 주변에는 아름다운 자태를 뽐내는 금강소나무가 울창하게 들어서 있고, 경사도 가파르지 않아 최근 트래킹 코스로 주목을 받고 있다. 겨울철에는 나뭇가지마다 눈꽃이 피어나고, 고원 특유의 탁 트인 설경이 어우러져 고요하면서도 깊이 있는 겨울 풍경을 만들어낸다. 눈꽃 트레킹을 마친 뒤 강릉 도심의 음식점에서 쫀득한 식감을 자랑하는 감자옹심이를 비롯해 얼큰한 맛이 살아 있는 장칼국수, 그리고 담백한 국물의 해물칼국수 등을 맛볼 수 있는 것도 겨울철 여행의 만족도를 높이는 핵심 요소다. 강릉시 관계자는 대관령 옛길 주변엔 선자령과 국립 대관령 치유의 숲, 대관령자연휴양림, 대관령박물관 등 명소뿐 아니라 성산 먹거리촌도 자리 잡고 있어 여행하기 좋은 곳 이라며 2026 2027 강릉 방문의 해 기간 동안 계절별 자연환경과 지역의 관광자원을 연계한 월별 추천 여행지를 지속해서 선보일 계획 이라고 말했다.	https://n.news.naver.com/mnews/article/032/0003424556?sid=103	8	["https://imgnews.pstatic.net/image/032/2026/01/29/0003424556_001_20260129103310500.jpg?type=w860"]	2026-01-29 10:32:01	2026-01-29 01:38:49.276338	\N	t	4
15	울산쇠부리축제 5월 8∼10일 달천철장·북구청서 개최	울산 연합뉴스 장지현 기자 제22회 울산쇠부리축제가 5월 8 10일 달천철장과 북구청 광장에서 이천년 철의 역사! 문화로 타오르다! 를 주제로 열린다. 두 개의 공간, 두 배의 즐거움 이라는 콘셉트로 달천철장에서는 울산쇠부리문화의 정체성을 담은 프로그램을, 북구청 광장에서는 울산쇠부리문화를 재해석한 프로그램을 선보인다. 울산쇠부리대장간, 타악페스타, 시민콘서트, 쇠부리 흥가요제, 철철철 노리터, 쇠부리체험존, RC카 레이싱, 정크아트 등 다양한 체험 프로그램이 준비된다.	https://n.news.naver.com/mnews/article/001/0015873427?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/PYH2025051113740005700_P4_20260129103814812.jpg?type=w860"]	2026-01-29 10:37:10	2026-01-29 01:38:49.281252	\N	t	4
16	겨울 강릉의 진짜 매력 '대관령 옛길'…"눈꽃이 길이 되는 곳"	강원 강릉시는 2월의 테마로 눈꽃 트레킹과 고원 설경을, 2월의 추천 여행지로 대관령 옛길을 선정했다고 29일 밝혔다. 강릉은 동해 바다 와 산악 지형을 동시에 품은 도시로, 겨울철에는 해안과 내륙의 풍경이 뚜렷한 대비를 이루는 것이 특징이다. 특히 2월은 고지대 설경이 가장 안정적으로 형성되는 시기로 겨울 강릉 관광의 본모습을 가장 선명하게 느낄 수 있다. 시는 이에 2026 2027 강릉 방문의 해 를 맞아 겨울 자연환경의 매력을 가장 잘 체감할 수 있는 공간으로, 대관령 옛길을 2월 추천 여행지로 선정했다. 대관령 옛길은 과거 영동과 영서를 잇는 주요 교통로로 사용되던 역사적인 길이다. 현재는 울창한 숲과 완만한 산길이 잘 보존된 걷기 여행명소로 자리 잡고 있다. 겨울철에는 나뭇가지마다 눈꽃이 피어나고, 고원 특유의 탁 트인 설경이 어우러져 고요하면서도 깊이 있는 겨울 풍경을 만들어낸다. 대관령 옛길은 비교적 경사가 완만하고 동선이 안정적이어서 전문 산악인이 아니어도 누구나 겨울 트레킹을 즐길 수 있다. 눈꽃 트레킹을 마친 뒤에는 겨울 강릉의 식문화를 함께 경험할 수 있다는 점도 2월 여행의 중요한 매력이다. 겨울 강릉을 대표하는 음식으로는 쫀득한 식감의 감자옹심이, 강릉 특유의 얼큰한 맛이 살아 있는 장칼국수, 그리고 담백한 국물의 해물칼국수가 있다. 이들 음식은 특히 겨울철에 선호도가 높아 여행 만족도를 높이는 핵심 요소로 자리하고 있다. 엄금문 관광정책과장은 앞으로도 2026 2027 강릉 방문의 해 기간 계절별 자연환경과 지역의 고유한 자원을 연계한 월별 추천 여행지를 지속해 선보일 계획 이라고 말했다.	https://n.news.naver.com/mnews/article/001/0015873422?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/PYH2023011610580006200_P4_20260129103629157.jpg?type=w860", "https://imgnews.pstatic.net/image/001/2026/01/29/PYH2023011603150006200_P4_20260129103629162.jpg?type=w860", "https://imgnews.pstatic.net/image/001/2026/01/29/PYH2022032004730006200_P4_20260129103629165.jpg?type=w860"]	2026-01-29 10:35:55	2026-01-29 01:38:49.286049	\N	t	4
17	제주 올해 입도객 100만명 돌파…설연휴로 상승세 지속 전망	제주를 찾는 관광객이 꾸준히 늘어나면서 올해 제주 입도객이 지난 28일 기준 100만명을 넘어섰다. 29일 제주도에 따르면 이는 지난해 같은 기간보다 약 15 많은 수치로, 도는 겨울방학을 맞아 가족 단위 여행객이 늘고 소규모 자유여행이 확산한 영향이 컸던 것으로 보고 있다. 최근 3년간 입도객 100만명 돌파일은 2023년 1월 30일, 2024년 1월 29일, 2025년 2월 1일이었다. 도는 다음 달에도 5일간의 설 연휴가 있어서 1분기 관광시장에 활력을 불어넣을 것으로 기대하고 있다. 도 관계자는 100만명 조기 돌파라는 외형적 성장에 안주하지 않고 상승 추세를 차분히 이어가면서 시장별 맞춤형 전략으로 내실 있는 성장을 도모할 방침 이라고 밝혔다.	https://n.news.naver.com/mnews/article/001/0015873415?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/PYH2026011803580005600_P4_20260129103614913.jpg?type=w860"]	2026-01-29 10:35:16	2026-01-29 01:38:49.291027	\N	t	4
18	산림청, 내달 13일까지 설 성수품 수급 안정 대책반 운영	산림청은 설을 대비해 밤 대추 공급에 차질이 없도록 설 연휴 전날인 2월 13일까지 설 성수품 임산물 수급 안정 대책반 을 운영한다고 29일 밝혔다. 대책반은 물가 안정과 수급 조절을 위해 임산물 가격 동향과 공급 상황을 매일 점검하고, 성수품 수요가 늘어나는 설 2주 전부터 밤 대추를 평상시보다 10배 늘린 2천580t 밤 2천400t, 대추 180t 공급한다. 대책반은 오는 2월 20일까지 각종 온오프라인 소비 촉진 행사도 병행한다. 온라인에서는 산림조합중앙회 임산물 쇼핑몰인 푸른장터누리집 sanrim.com 을 통해 10 30 할인 행사를 하고, 네이버스토어와 우체국쇼핑몰 등에서도 지리적표시 등록품을 포함한 숲푸드 마켓 설 명절 기획전 을 운영해 최대 20 할인 판매한다. 임산물 판매장이 설치된 전국 산림조합 15곳에서도 밤 대추 감 곶감 고사리 등 명절 성수품을 최대 30 할인한 가격으로 구매할 수 있다. 이상익 산림청 산림산업정책국장은 이번 설에는 밤 대추 등 다양한 할인 행사와 안정적인 공급으로 차례상 부담이 줄어들길 바란다 며 품질 좋은 국내산 설 성수품을 저렴한 가격에 구매할 수 있도록 최선을 다하겠다 고 말했다.	https://n.news.naver.com/mnews/article/001/0015873400?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129071700063_01_i_P4_20260129103230022.jpg?type=w860", "https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129071700063_02_i_P4_20260129103230030.jpg?type=w860"]	2026-01-29 10:31:53	2026-01-29 01:38:49.29605	\N	t	4
19	제주관광공사, 한국마사회와 말(馬) 활용 특화 콘텐츠 만든다	붉은 말의 해 를 맞아 제주관광공사가 한국마사회 제주본부와 손잡고 말을 활용한 굿즈 제작 등 특화 콘텐츠 개발에 나선다. 제주관광공사는 한국마사회 제주본부와 지난 28일 렛츠런파크 제주에서 제주 말 馬 문화 특화 콘텐츠 개발 및 제주관광 활성화를 위한 업무협약 을 체결했다고 29일 밝혔다. 이번 업무협약은 2026년 병오년 붉은 말의 해 를 맞아 제주 고유문화이자 핵심 자산인 말 문화를 관광 자원화함으로써 제주관광의 새로운 성장 동력을 확보하기 위해 마련됐다. 양 기관은 이번 업무협약을 통해 한국마사회의 공식 캐릭터인 말마 프렌즈 를 적극 활용해 올 한해 다양한 협업 굿즈를 선보일 예정이다. 또 주요 관광 거점에서 말 관련 다채로운 현장 이벤트를 개최해 제주만의 친근하고 매력적인 말 문화 경험을 선사할 계획이다. 고승철 제주관광공사 사장은 제주 고유의 말 문화 가치를 현대적 관광 콘텐츠로 재해석하여 제주가 글로벌 말 문화 관광의 메카로 도약할 수 있도록 노력하겠다 고 말했다.	https://n.news.naver.com/mnews/article/001/0015873412?sid=103	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129073000056_01_i_P4_20260129103519333.jpg?type=w860"]	2026-01-29 10:34:42	2026-01-29 01:38:49.301077	\N	t	4
20	유쾌 발랄 영·프 정상…'탑건 선글라스' 흉내 스타머에 마크롱 화답	키어 스타머 영국 총리가 한 행사장에서 에마뉘엘 마크롱 프랑스 대통령처럼 탑건 선글라스를 쓰고 등장해 좌중에 큰 웃음을 자아냈습니다. 현지시간 27일 프랑스 르파리지앵에 따르면 스타머 총리는 이날 틱톡 계정에 9초 분량의 짧은 영상을 올렸습니다. 런던의 한 극장에서 팟캐스트 정당 녹화 중 촬영된 것으로, 스타머 총리는 검은색 탑건 선글라스를 쓴 뒤 영어식 발음으로 봉주르 Bonjour 안녕하세요 라고 인사했습니다. 현장은 곧바로 웃음바다가 됐습니다. 스타머 총리는 이 영상을 올리며 영화 탑건 속 톰 크루즈의 대사 톡 투 미 구스 Talk to me goose 라고 캡션을 달았습니다. 구스는 톰 크루즈가 연기한 매버릭의 파트너이자 절친 인데, 스타머 총리가 인용한 대사는 매버릭이 친구의 죽음 후에도 비행 때 두려움을 잊으려고 한 혼잣말입니다. 마크롱 대통령은 스타머 총리의 농담을 받아들여 이 게시물에 For sure 확실히 라는 답글을 달았습니다. For sure 는 마크롱 대통령이 다보스 포럼 영어 연설에서 한 말로, 그는 유럽이 가끔은 확실히 for sure 너무 느리다. 그리고 확실히 for sure 개혁이 필요하다 고 언급했습니다. 마크롱 대통령의 이 프랑스식 영어 발음은 소셜네트워크상에서 놀림거리가 되며 밈과 패러디의 소재가 됐습니다. 이 유행에 당사자인 마크롱 대통령도 유쾌하게 편승한 모양새입니다. 스타머 총리는 마크롱 대통령의 답변에 대댓글 로 두 사람이 조종사 복장에 탑건 선글라스를 쓴 합성 이미지를 올려 화답했습니다. 마크롱 대통령은 오른쪽 눈 실핏줄이 터져 불가피하게 선글라스를 쓰고 다보스 포럼에 참석했는데, 이를 두고 도널드 트럼프 미국 대통령은 강경하게 보이려고 애썼다 고 조롱했었습니다. 스타머 마크롱 선글라스 영국 프랑스 탑건 연합뉴스TV 기사문의 및 제보 카톡 라인 jebo23	https://n.news.naver.com/mnews/article/422/0000827978?sid=104	7	["https://imgnews.pstatic.net/image/422/2026/01/29/AKR20260129103255CfK_01_i_20260129103312034.jpg?type=w860"]	2026-01-29 10:33:12	2026-01-29 01:38:49.306237	\N	t	5
27	조이시티, 레드징코게임즈와 '프로젝트 임진' 퍼블리싱 계약	조이시티는 국내 게임사 엔드림 관계사인 레드징코게임즈가 개발 중인 다중접속역할수행게임 MMORPG 프로젝트 임진 퍼블리싱 계약을 체결했다고 29일 밝혔다. 프로젝트 임진 은 임진록 , 천하제일거상 , 군주 온라인 등 역사 배경의 전략 게임 거장으로 불리는 김태곤 디렉터가 제작을 총괄한 대규모 전쟁 MMORPG다. 임진왜란을 배경으로 조선, 왜, 명 3국의 실존 장수 36명을 수집하고 육성할 수 있으며 실제 병기를 활용한 해상전과 공성전 등 입체적인 전투 콘텐츠를 갖췄다. 조이시티는 그간 건쉽배틀 토탈워페어 , 캐리비안의 해적 전쟁의 물결 등 다수의 전쟁 시뮬레이션 게임을 성공시킨 노하우를 바탕으로, 프로젝트 임진 을 국내 시장에서 전쟁 MMORPG로 안착시킬 계획이다. 프로젝트 임진 은 오는 2월 9일까지 레드징코게임즈 공식 홈페이지를 통해 2차 알파 테스트 참가자를 모집하고 있다. 2월 10일부터 17일까지 진행되는 이번 2차 알파 테스트는 지난 11월 진행된 1차 테스트의 피드백을 바탕으로 게임의 완성도와 신규 콘텐츠를 점검하기 위해 마련됐다. 프로젝트 임진 은 2026년 상반기 모바일과 PC 플랫폼을 통해 정식 출시될 예정이다.	https://n.news.naver.com/mnews/article/001/0015873406?sid=105	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129070600017_01_i_P4_20260129103323092.jpg?type=w860"]	2026-01-29 10:33:01	2026-01-29 01:38:49.337398	\N	t	6
21	"유럽 주요도시 평균소득, 월세 감당 어려워"…기준치 이상 8곳 불과	대다수 유럽 주요 도시에서는 평균 소득자가 월세를 감당하기 어려운 수준이라는 분석이 나왔습니다. 현지시간 28일 시사주간지 이코노미스트는 평균적인 소득으로 혼자 월세를 감당하며 살 수 있는지를 평가하는 캐리 브래드쇼 지수 가 기준치인 1을 넘은 유럽 도시는 조사 대상 39곳 중 8곳에 불과했다고 보도했습니다. 미국 드라마 섹스 앤 더 시티 의 독신 여성 주인공 이름을 딴 이 지수는 유럽연합 EU 통계기구 유로스타트의 도시별 침실 1개짜리 아파트 평균 월세와 싱크탱크 경제연구소 ERI 가 계산한 도시별 평균 임금을 비교해 산출합니다. 이코노미스트는 주거 비용의 적정성을 판단하는 기준으로 흔히 쓰이는 소득의 30 이내로 월세를 해결하려면 세입자가 얼마를 벌어야 하는지 계산했습니다. 2025년 기준 침실 1개 아파트 평균 월세를 감당할 수 있는 연봉 수준이 가장 높은 5개 도시는 스위스 제네바 10만 2천 유로 1억 7,500만 원 , 영국 런던 9만 4천 유로 1억 6,100만 원 , 스웨덴 스톡홀름 8만 4천 유로 1억 4,400만 원 , 아일랜드 더블린 노르웨이 오슬로 각 8만 유로 1억 3,700만 원 였습니다. 캐리 브래드쇼 지수가 1보다 낮을수록 월세가 감당 못 할 수준이고 높을수록 소득에 여유가 있는 것으로 여겨집니다. 런던의 경우 평균 연봉 5만5,530파운드 1억 900만 원 중 44 를 월세 평균 월세 기준 로 써야 하는데, 이를 지수로 환산하면 0.68입니다. 이 지수가 가장 낮아 임금 대비 월세가 높은 곳은 조지아의 트빌리시, 체코 프라하, 세르비아 베오그라드, 헝가리 부다페스트, 포르투갈 리스본입니다. 스톡홀름과 런던, 더블린, 스페인 마드리드도 0.7에 미치지 못하며 독일 뮌헨, 프랑스 파리, 제네바, 덴마크 코펜하겐도 그보다는 높지만 0.9는 안 됩니다. 독일 베를린은 1.01로 가까스로 기준을 넘었고 룩셈부르크의 룩셈부르크, 오스트리아 빈, 핀란드 헬싱키, 벨기에 브뤼셀, 스위스 베른, 프랑스 리옹, 독일 본은 월세 대비 임금 수준이 비교적 높았습니다. 유럽 도시 월세 캐리브래드쇼지수 연합뉴스TV 기사문의 및 제보 카톡 라인 jebo23	https://n.news.naver.com/mnews/article/422/0000827980?sid=104	7	["https://imgnews.pstatic.net/image/422/2026/01/29/AKR20260129103435NIT_01_i_20260129103512051.jpg?type=w860"]	2026-01-29 10:35:12	2026-01-29 01:38:49.310889	\N	t	5
22	美, 이란 공격 준비됐나‥중동지역 군사자산 뚜렷한 증강	최근 중동 지역에서 카타르와 걸프 해역을 중심으로 미군 병력과 군사 자산 증강이 잇따르면서, 미국이 이란에 대한 추가 군사 작전을 준비하고 있는 것 아니냐는 관측이 제기되고 있습니다. 영국 BBC는 현지시간 28일, 트럼프 대통령의 대이란 경고 발언과 군사 동향을 분석해 미국이 다시 무력 사용에 나설 가능성이 있다고 보도했습니다. 트럼프 대통령은 이란이 핵 프로그램 제한 협상에 응하지 않을 경우 다음 공격은 훨씬 더 강력할 것 이라며 대규모 함대가 이란으로 향하고 있다고 밝혔습니다. 현재 중동 지역에는 약 5만 명의 미군이 주둔 중이며, 카타르 알우데이드 공군기지에는 1만여 명이 배치돼 있습니다. 위성사진 분석에서는 기지 외곽의 신규 구조물과 방공망 확충 정황이 포착됐고, F 15 전투기와 공중급유기, P 8 해상초계기 등 항공 전력이 중동에 전개된 사실도 확인됐습니다. 항공모함 에이브러햄 링컨호 전단은 F 35 전투기와 토마호크 미사일을 탑재한 채 걸프 해역으로 이동 중입니다. 트럼프 대통령은 이란이 핵 프로그램 제한에 합의할 경우 사태를 외교적으로 해결할 가능성을 열어둔 상태로 이란 정부는 침략에 강력히 대응할 준비가 돼 있다 면서도 핵 협상에 열려있다는 뜻을 표명했습니다.	https://n.news.naver.com/mnews/article/214/0001477335?sid=104	9	["https://imgnews.pstatic.net/image/214/2026/01/29/0001477335_001_20260129103414689.jpg?type=w860"]	2026-01-29 10:33:21	2026-01-29 01:38:49.31424	\N	t	5
23	[그래픽] 미국 주요 기업 실적발표 현황	일론 머스크가 이끄는 전기차업체 테슬라의 지난해 4분기 실적이 시장 전망치를 소폭 웃돌았다. 28일 현지시간 테슬라가 발표한 2025년 4분기 실적 보고서에 따르면 매출은 249억달러, 주당순이익 EPS 은 0.50달러를 기록했다. 마이크로소프트 MS 는 회계연도 2분기 지난해 10 12월 매출액이 전년도 같은 기간 대비 17 오른 812억7천만 달러 약 116조원 를 기록했고 페이스북 인스타그램 운영사 메타는 작년 4분기 10 12월 매출액이 598억9천만 달러 약 85조7천억원 로 전년 같은 기간 대비 24 상승했다고 28일 현지시간 공시했다. X 트위터 yonhap_graphics 페이스북 tuney.kr LeYN1	https://n.news.naver.com/mnews/article/001/0015873416?sid=104	4	["https://imgnews.pstatic.net/image/001/2026/01/29/GYH2026012900100004400_P2_20260129103617016.jpg?type=w860"]	2026-01-29 10:35:15	2026-01-29 01:38:49.319095	\N	t	5
24	이란 외무 "침략에는 강력 대응‥공정한 핵 협상은 환영"	이란 정부가 미국을 향해 침략에 강력히 대응할 준비가 돼 있다 면서도 핵 협상에 열려있다는 뜻을 표명했습니다. 아바스 아라그치 이란 외무장관은 현지시간 28일 소셜미디어 엑스를 통해 우리의 용감한 군대는 방아쇠에 손가락을 얹고 사랑하는 조국과 하늘, 바다에 대한 어떠한 침략에도 즉각적이고 강력히 대응할 준비가 돼 있다 고 밝혔습니다. 아라그치 장관은 12일 전쟁 에서 얻은 소중한 교훈 덕에 우리는 더 강력하고 신속하며 심도 있게 대응할 수 있게 됐다 면서도 동시에 이란은 언제나 상호 이익이 되고 공정하며 평등한 핵 협상을 환영해 왔다 고 덧붙였습니다. 12일 전쟁 은 지난해 6월 이스라엘이 이란 수도 테헤란 등 주요 도시와 핵 시설을 공습하고 이란이 미사일로 반격했던 무력충돌을 뜻합니다.	https://n.news.naver.com/mnews/article/214/0001477336?sid=104	9	["https://imgnews.pstatic.net/image/214/2026/01/29/0001477336_001_20260129103815786.jpg?type=w860"]	2026-01-29 10:36:21	2026-01-29 01:38:49.32372	\N	t	5
25	'귀칼'이 끌고 '국보'가 밀었다…日 영화 흥행수입 역대 최고	귀멸의 칼날 애니메이션과 재일교포 이상일 감독의 실사 영화 국보 의 폭발적인 흥행에 힘입어 지난해 일본 내 영화 흥행 수입이 역대 최고를 기록했다. 29일 일본영화제작자연맹이 홈페이지에 공개한 2025년 영화산업 현황 자료에 따르면 일본 영화와 외화를 합산한 전체 수입은 전년 대비 32.6 증가한 2천744억5천200만엔 약 2조5천597억원 으로 집계됐다. 이는 종전 최고액이었던 2019년 2천611억엔을 넘어 연맹이 통계를 발표하기 시작한 2000년 이후 사상 최고액이다. 흥행 일등 공신은 애니메이션 극장판 귀멸의 칼날 무한성편 제1장 이었다. 이 작품은 무려 391억4천만엔의 수입을 올리며 전체 1위를 차지했다. 귀멸의 칼날 시리즈는 전 세계 흥행 수입 1천억엔을 돌파하며 일본 영화 사상 최초의 기록을 세우기도 했다. 2위는 재일교포 이상일 감독이 연출하고 요시자와 료가 주연한 국보 가 차지했다. 가부키의 세계를 다룬 이 영화는 195억5천만엔의 수입을 기록했다. 2003년 춤추는 대수사선 2 가 세웠던 일본 실사 영화 역대 최고 기록을 22년 만에 경신했다. 이 외에도 명탐정 코난 척안의 잔상 147억4천만엔 , 극장판 체인소맨 레제편 104억3천만엔 등 흥행 수입 100억 엔을 돌파한 메가 히트작이 4편에 달하며 시장 성장을 이끌었다. 부문별로는 일본 영화가 2천75억6천900만엔으로 역대 최고치를 기록하며 전체 시장을 주도했다. 반면 외화 수입은 668억8천300만엔에 머물렀다. 외화 중에서는 미션 임파서블 파이널 레코닝 이 52억8천만엔으로 1위를 기록했다. 지난해 극장을 찾은 전체 관객 수는 전년보다 30.7 늘어난 1억8천875만6천명으로 역대 2위였다. 개봉 편수는 1천305편으로 사상 최다를 기록했다. 시마타니 요시시게 연맹 회장은 NHK에 지난해에는 남녀노소 가리지 않고 전 세대가 균형 있게 극장을 찾았다 며 올해 개봉작들의 흥행 여부가 일본 영화계의 저력을 확인할 시험대가 될 것 이라고 말했다.	https://n.news.naver.com/mnews/article/001/0015873433?sid=104	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129072400009_02_i_P4_20260129103825879.jpg?type=w860", "https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129072400009_03_i_P4_20260129103825882.jpg?type=w860"]	2026-01-29 10:37:55	2026-01-29 01:38:49.328719	\N	t	5
28	“문제는 설탕이 아니고 소금이야!”…대통령이 던진 ‘설탕세’에 야당 반응 [지금뉴스]	29일, 국민의힘 최고위원회의 중 김재원 국민의힘 최고위원 이재명 대통령이 설탕세를 거론했습니다. 당뇨가 포함된 식품에 세금 또는 부과금을 징수함으로써 설탕 소비를 줄이고 당류 소비로 인한 비만 당뇨병 등 건강 유해 요인을 억제하겠다는 취지에서 선진 서방 각국에서 설탕 부담금을 도입해서 운영하고 있는 것이 사실입니다. 우리나라에서 설탕세를 논의한 적은 있습니다만, 입법화되지도 않았고, 그것이 정책적으로 크게 거론되지 못한 이유는 우리나라의 당뇨 환자 비만 환자가 설탕에 설탕 소비에 기인했다기보다는 오히려 과도한 소금 섭취에 기인한다는 그런 의견이 많습니다. 우리나라는 식생활 환경이 좀 다릅니다. 아시아에서도 설탕 소비세를 부과하거나 또는 설탕 부담금을 부과하는 나라는 주로 말레이시아, 인도네시아, 태국 이런 동남아시아 국가들입니다. 동북아시아의 중국이나 일본이나 한국의 경우에는 설탕의 소비보다는 오히려 소금의 섭취가 늘 문제가 되는 나라입니다. 그런데도 이재명 대통령이 굳이 설탕세를 거론하면서 지역 의료 사업에 쓰는 것이 어떠냐고 제안했는데 이것은 시장을 극도로 왜곡하고 특정 제품에 대한 세금을 부과함으로써 결국은 소비 구조를 왜 부과하고 더 나아가서 주로 저소득층에게 부담을 주는 그런 아주 나쁜 세금으로 악용될 가능성이 큽니다. 단순히 아이디어 차원을 넘어서서 대통령 한마디는 관련 공무원들이 모두 찬양하는 보고서를 쓰게 만드는 효과가 있습니다. 행여 내용도 뻔히 알면서 또다시 국민들의 건강을 위협하는 내용으로 설탕세를 도입하고 그것을 통해서 저소득층에게 도리어 불이익을 주고자 하는 이런 설탕세는 즉각 거두시기 바랍니다. 영상편집 백성현 제보하기 전화 02 781 1234, 4444 이메일 카카오톡 KBS제보 검색, 채널 추가 네이버, 유튜브에서 KBS뉴스를 구독해주세요!	https://n.news.naver.com/mnews/article/056/0012114784?sid=100	11	[]	2026-01-29 10:38:34	2026-01-29 01:40:22.67391	\N	t	1
29	美대입시험 문제, '中사이트 거래' 등 부정행위 의심	미국의 표준화 대입 시험 SAT에서 출제 문항이 유출돼 중국 사이트에서 거래되는 등 부정행위 의심 사례들이 잇따르고 있다고 미국 일간 뉴욕타임스 NYT 가 현지시간 28일 보도했습니다. NYT에 따르면 유럽의 유명 기숙학교 학생들을 가르치는 한 SAT 과외교사는 지난해 11월 SAT를 시행하는 비영리기관 칼리지 보드 에 부정행위가 자행되고 있다는 의혹을 알려주는 이메일을 보냈습니다. 이 과외교사는 현재 사용되고 있는 시험 문항들이 다년간 유출됐고, 유출 문항들이 국제적인 규모로 유포됐다고 칼리지 보드에 설명했습니다. 그는 유출 문항들을 검토해 본 결과, 적어도 일부는 실제로 최근에 치러진 디지털 SAT에 실제로 출제된 문항들이라는 점을 확인했다고 밝혔습니다. 중국에서 운영되는 것으로 추정되는 블루북 플러스 bluebook.plus 라는 SAT 대비 사이트가 유료 가입자들에게 제공하는 연습용 문제 중 실제 출제 문항으로 보이는 것들이 포함돼 있었다는 전언입니다. 웹 트래픽 추정집계 사이트 시밀러웹에 따르면 블루북 플러스의 지난해 11월 방문자 수는 87만 5천 명이었습니다. 이와 별도로 코딩 사이트들이나 SAT 대비 사이트들에는 SAT 응시용 컴퓨터 프로그램인 블루북 의 보안을 우회하는 방법이라고 주장하는 게시물들이 종종 올라옵니다. 마우스로 위장한 영상 캡처용 플러그인, 컴퓨터의 다른 부분과 분리된 샌드박스 환경, 블루북이 설치된 컴퓨터를 원격으로 조종하는 방법 등 진위가 확인되지 않는 여러 수법이 나와 있습니다. 칼리지 보드는 NYT의 질의에 SAT 부정행위는 1 의 몇분의 1 수준으로 매우 드물고, 시험이 디지털로 전환된 후에도 전체적 시험 점수가 안정적으로 유지됐다면서 부정행위 가능성에 대해서는 항상 경계하고 있다고 답했습니다. 그러면서도 일부 학생들은 중요한 평가에서 부정행위를 하려는 유혹을 항상 받기 마련이며, 악의적 행위자들은 매우 끈질기다 며 일부 미국 외 시장에서 악의적 행위자들이 학생과 학부모의 불안감을 이용하기 위해 시험 문항을 입수 공유하고 심지어 문항을 조작하려고 오랫동안 조직적인 노력을 기울여 왔다 고 인정했습니다. SAT 응시자는 각자 랩톱 컴퓨터에 블루북 이라는 프로그램을 미리 설치한 뒤 정해진 시험장에서 시험을 치릅니다. SAT는 1년에 7회 또는 8회 치러지며, 시험장은 187개국에 모두 1,700곳이 있습니다. 이런 디지털 방식의 SAT 시험은 미국에서는 2024년 3월부터, 미국 외 나라들에서는 2023년 3월부터 도입됐습니다. 응시자마다 푸는 문제가 달라지는 적응형 시험 인 디지털 SAT의 특성상 일부 문항 유출에 따르는 타격이 다른 문제은행식 표준화 시험만큼 심각하지는 않다는 지적도 있습니다. 시험 앞부분에서 정답률이 높아 실력이 뛰어난 것으로 추정되는 응시자에게는 까다로운 문제가 나옵니다. 또 출제 문항은 문항 수십만 개가 있는 문제은행에서 추출된다는 게 칼리지 보드의 설명입니다. 현재 SAT는 중국 정부의 제한 방침으로 중국 내에서는 시행되지 않고 있으며, 중국에 사는 응시자들은 홍콩, 마카오, 한국 등 다른 나라에 있는 시험장에서 시험을 봐야 합니다. 과거에도 SAT와 같은 표준화 시험에서 대리시험, 시험지 절도, 시험문제 유출 후 시차가 있는 지역에서 응시 등 다양한 수법의 부정행위 시도는 계속 있었습니다. 최근에는 미국 법학전문대학원과 대학원 입학 지원자 평가에 각각 쓰이는 LSAT와 GRE에서 부정행위 의혹이 적발되기도 했습니다. 다만 이런 적발 사례들은 정해진 시험장이 아니라 응시자의 집에서 원격으로 치러진 경우였습니다. 의혹 적발을 계기로 지난해 8월부터 LSAT의 중국 내 시험이 중단됐습니다. 당시 LSAT을 시행하는 법학전문대학원입학위원회 LSAC 의 수전 크린스키 집행부회장은 시험 부정행위를 부추기려는 중국 본토 내 개인들과 회사들에 의한 조직적 노력에 대해 우려가 갈수록 커지고 있다 고 말했습니다. 그는 이런 행위는 LSAT에만 한정된 것이 아니다. 이런 업체들은 사실상 모든 표준화 시험에 대해 부정행위 서비스를 제공한다고 주장하고 있다 고 덧붙였습니다. 대입 대입시험 SAT 부정행위 문제거래 연합뉴스TV 기사문의 및 제보 카톡 라인 jebo23	https://n.news.naver.com/mnews/article/422/0000827982?sid=102	7	["https://imgnews.pstatic.net/image/422/2026/01/29/AKR20260129103821jAB_01_i_20260129103912225.jpg?type=w860"]	2026-01-29 10:39:12	2026-01-29 01:40:22.679583	\N	t	3
30	조길형 시장 "교통대 양보 통합안은 바람직하지 않아"	조길형 충북 충주시장은 29일 국립한국교통대학교가 대폭 양보하는 협의안의 변경은 당초 통합의 전제를 무너지게 하는 바람직하지 않은 모습 이라고 말했다. 조 시장은 이날 현안 점검 회의에서 교통대와 충북대의 통합 문제와 관련해 충주시가 통합을 지지한 것은 통합안 내용의 합리성과 대학 내부의 자율적이고 민주적 절차를 존중했기 때문 이라며 이같이 밝혔다. 그는 대등한 통합이라는 당초 원칙에 부합하는 합리적 방향으로 추진되길 바란다 고 덧붙였다. 충북대는 내부 투표 부결 이후 통합 재추진을 위해 기존에 만든 통합 합의서의 핵심 조항 수정을 요구하고 있지만, 교통대는 이에 반대하고 있어 통합의 불씨가 꺼져가고 있는 형국이다. 충북도지사 선거 도전을 위해 오는 30일 퇴임하는 조 시장은 공직사회가 쌓아온 행정 경험과 통찰력을 바탕으로 충주의 지속 가능한 미래를 단단하게 만들어 올 수 있었다. 당초 계획된 방향대로 앞으로도 흔들림 없이 추진해 주기를 바란다 고 당부했다.	https://n.news.naver.com/mnews/article/001/0015873438?sid=102	4	["https://imgnews.pstatic.net/image/001/2026/01/29/AKR20260129063500064_02_i_P4_20260129103921196.jpg?type=w860"]	2026-01-29 10:38:28	2026-01-29 01:40:22.684846	\N	t	3
31	미국 '슈퍼볼' 경기장서 이민 단속?…스포츠로 단속 확대 움직임	미국 프로풋볼 슈퍼볼 경기 미국 이민세관단속국 ICE 이 다음 달 8일 현지 시간 캘리포니아주 샌타클래라에서 열리는 슈퍼볼 에 단속 요원을 배치할 것으로 전망된다고 영국 일간 가디언이 보도했습니다. 민주당 소속인 맷 마한 캘리포니아주 새너제이 시장은 현지 언론과의 인터뷰에서 정부로부터 슈퍼볼에 ICE 요원을 배치할 의사가 있다는 소식을 들었다 며 이것이 단순히 말에 불과한 것인지는 모르겠다 고 말했습니다. 슈퍼볼은 미국에서 가장 인기 있는 스포츠인 미국프로풋볼 NFL 의 챔피언 결정전입니다. 슈퍼볼 경기 시간에는 미국 전체가 사실상 멈춰 선다는 말이 있을 정도로 순도 높은 인기를 자랑합니다. 올해는 11년 전 명승부를 펼친 뉴잉글랜드 패트리어츠와 시애틀 시호크스의 재대결로 관심이 더욱 뜨거운 상황입니다. 수많은 팬이 모이기 때문에 관람객의 안전을 위해 안전 요원을 배치하는 건 흔하지만, 이민자 단속을 전담하는 ICE 요원을 배치하는 건 이례적인 경우라고 신문은 지적했습니다. 지역 사회를 중심으로 슈퍼볼에서 이민자 단속이 강화할 것이란 우려가 나오고 있는 상황이지만, 미국 국토안보부 DHS 는 단속 여부에 대해 확답은 하지 않고 있습니다. 트리시아 매클로플린 DHS 차관보는 28일 현지 시간 월드컵을 포함한 다른 주요 스포츠 행사와 마찬가지로, 슈퍼볼이 안전한 행사가 될 수 있도록 지역 및 연방 파트너들과 협력하는 데 전념하고 있다 는 원론적인 답변만 내놨습니다. 정부의 이런 움직임은 ICE의 이민자 단속 여파가 일파만파로 번지고 있는 가운데 나온 것이어서 지역 사회, 특히 취약 계층 가족들 사이에서 우려를 낳고 있다고 신문은 전했습니다. 사진 게티이미지	https://n.news.naver.com/mnews/article/055/0001328484?sid=104	1	["https://imgnews.pstatic.net/image/055/2026/01/29/0001328484_001_20260129103910560.jpg?type=w860"]	2026-01-29 10:38:52	2026-01-29 01:40:22.689612	\N	t	5
32	"이력서 해체가 미래" 30주년 잡코리아, 간판도 바꿨다…새 이름 '웍스피어'	잡코리아, 사명 웍스피어 로 30주년 행사서 AI 서비스 공개 커리어 에이전트 시대 선언 윤현준 제안받는 경험으로 이력서의 해체. 저희가 예상하고 그리는 채용의 미래는 이력서의 해체에서 시작될 것입니다. 윤현준 잡코리아 대표 잡코리아가 30주년을 맞아 사명을 웍스피어 로 변경했다. 웍스피어는 단순한 일자리 매칭을 넘어 개인 기업이 처한 상황과 맥락을 이해하면서 선택을 제안하는 커리어 에이전트 시대 를 열겠다고 선언했다. 잡코리아는 29일 오전 그랜드 인터컨티넨탈 서울 파르나스에서 30주년 기념 콘퍼런스를 개최했다. 이 자리에선 잡코리아의 새로운 사명인 웍스피어 가 공개됐다. 서비스명은 잡코리아를 사용하지만 사명만 변경하는 것이다. 웍스피어는 이날 AI 커리어 에이전트 중심의 플랫폼 전환 을 공식화했다. 웍스피어는 일 Work 경험 Experience 영역 세계 Sphere 를 결합한 명칭이다. 일하는 모두를 위한 하나의 세계를 만들겠다 는 잡코리아 방향성을 담아냈다는 설명이다. 일자리를 단순 매칭하는 단계를 뛰어넘어 일을 둘러싼 모든 경험을 AI와 데이터로 재설계하고 새로운 일의 문화 생태계를 조성하겠단 의미를 담고 있다. 웍스피어는 컨텍스트 링크 를 향후 30년을 이끌 핵심 개념으로 제시했다. 컨텍스트 링크는 개인 이력과 역량, 관심사 행동 데이터 등 다양한 맥락을 종합적으로 이해하고 사람 일, 정보 기회를 더 정교하게 연결하는 방식을 뜻한다. 이를 통해 구직자가 공고를 직접 검색하지 않더라도 개인에게 의미 있는 기회가 선제적으로 제안되는 채용 경험을 구현하겠다는 구상이다. 웍스피어는 잡코리아, 알바몬, 잡플래닛, 나인하이어, 클릭 등 기존 서비스를 한 그룹 체계로 재편한다. 채용 커리어 전반에 걸쳐 조직 성장을 지원하는 풀 스펙트럼 인적자원 HR 테크 생태계로 확장하기 위해서다. 올 상반기 중으로는 AI 기반 차세대 커리어 에이전트 2종을 출시한다. AI 커리어 에이전트는 개인과 기업이 처한 상황과 맥락을 이해하고 다음 선택을 제안하는 구조로 설계됐다. 탤런트 에이전트 는 인사 담당자를 위한 추론 기반 대화형 인재 탐색 서비스다. 조직이 처한 상황과 필요한 인재상을 자연어로 입력할 경우 AI가 과거 채용 데이터, 내 외부 인재 정보를 종합해 최적의 후보를 제안한다. 커리어 에이전트 는 구직자를 위한 초개인화 커리어 추천 서비스다. 공고 조회 지원이력 활동 패턴 등 행동 데이터를 분석해 개인에게 맞는 기회를 선제적으로 제안하는 것이 골자다. 모두가 같은 공고를 시대를 뛰어넘어 개인에게 가장 의미 있는 정보만 도달하는 채용 경험을 구현하겠다는 것이다. 기업용 통합 비즈센터 하이어링 센터 도 상반기 중 공개한다. 정규직 비정규직 채용을 별도 플랫폼에서 관리해야 했던 불편을 해소하겠다는 목표다. 한 창구에서 공고 등록, 지원자 관리, 채용 성과 분석을 지원하는 올인원 채용 환경을 제공하겠다는 설명이다. 잡플래닛의 기업 리뷰 조직 문화 데이터를 연계해 채용 이후도 관리하는 풀필먼드 HR 경험 을 구현한다는 목표도 제시됐다. 잡코리아는 누적 통합회원 수가 3000만명을 넘어선 국내 최대 커리어 플랫폼이다. AI 추천 매칭 과정 고도화 이후 주요 서비스 전반에 걸쳐 사용자 지표가 성장세를 나타내고 있다. 실제 잡코리아 알바몬의 지난해 누적 월간활성사용자 MAU 수는 5933만명을 기록했다. AI 추천을 고도화하면서 구직자 서비스 체류 시간과 매칭 성사율도 개선됐다. 기업 대상 AI 기반 인재 탐색 제안 서비스 이용 지표도 개선되고 있다. 윤현준 웍스피어 대표는 이제 채용은 기다리는 과정 이 아니라 제안받는 경험 으로 바뀌고 있다 며 웍스피어는 방대한 데이터와 AI 기술을 기반으로 기업과 개인 모두가 더 나은 선택을 할 수 있는 선순환 구조를 만들어 채용을 넘어 커리어 전반의 가치를 키우는 플랫폼으로 진화해 나갈 것 이라고 말했다.	https://n.news.naver.com/mnews/article/015/0005243900?sid=105	5	["https://imgnews.pstatic.net/image/015/2026/01/29/0005243900_001_20260129103918190.jpg?type=w860"]	2026-01-29 10:39:18	2026-01-29 01:40:22.694382	\N	t	6
\.


--
-- Data for Name: news_reactions; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.news_reactions (news_reaction_id, user_id, news_id, value) FROM stdin;
\.


--
-- Data for Name: news_views; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.news_views (news_view_id, user_id, news_id, category_id, viewed_at) FROM stdin;
\.


--
-- Data for Name: search_logs; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.search_logs (search_log_id, user_id, query, searched_at) FROM stdin;
\.


--
-- Data for Name: user_category_subscriptions; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.user_category_subscriptions (user_id, category_id) FROM stdin;
\.


--
-- Data for Name: user_keyword_read_stats; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.user_keyword_read_stats (user_id, keyword, count, updated_at) FROM stdin;
\.


--
-- Data for Name: user_keyword_subscriptions; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.user_keyword_subscriptions (user_id, keyword) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.users (user_id, login_id, user_real_name, password_hash, email, age_range, gender, fcm_token, created_at, modified_at, deleted_at, marketing_agree, user_status) FROM stdin;
\.


--
-- Name: ai_generated_news_ai_generated_news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.ai_generated_news_ai_generated_news_id_seq', 1, false);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 6, true);


--
-- Name: clusters_cluster_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.clusters_cluster_id_seq', 1, false);


--
-- Name: companies_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.companies_company_id_seq', 11, true);


--
-- Name: news_news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.news_news_id_seq', 32, true);


--
-- Name: news_reactions_news_reaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.news_reactions_news_reaction_id_seq', 1, false);


--
-- Name: news_views_news_view_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.news_views_news_view_id_seq', 1, false);


--
-- Name: search_logs_search_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.search_logs_search_log_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, false);


--
-- Name: ai_generated_news ai_generated_news_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.ai_generated_news
    ADD CONSTRAINT ai_generated_news_pkey PRIMARY KEY (ai_generated_news_id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: cluster_news_link cluster_news_link_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cluster_news_link
    ADD CONSTRAINT cluster_news_link_pkey PRIMARY KEY (cluster_id, news_id);


--
-- Name: clusters clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_pkey PRIMARY KEY (cluster_id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (company_id);


--
-- Name: news news_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_pkey PRIMARY KEY (news_id);


--
-- Name: news_reactions news_reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_reactions
    ADD CONSTRAINT news_reactions_pkey PRIMARY KEY (news_reaction_id);


--
-- Name: news_views news_views_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views
    ADD CONSTRAINT news_views_pkey PRIMARY KEY (news_view_id);


--
-- Name: search_logs search_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.search_logs
    ADD CONSTRAINT search_logs_pkey PRIMARY KEY (search_log_id);


--
-- Name: news_reactions uq_user_news_reaction; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_reactions
    ADD CONSTRAINT uq_user_news_reaction UNIQUE (user_id, news_id);


--
-- Name: news_views uq_user_news_view; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views
    ADD CONSTRAINT uq_user_news_view UNIQUE (user_id, news_id);


--
-- Name: user_category_subscriptions user_category_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_category_subscriptions
    ADD CONSTRAINT user_category_subscriptions_pkey PRIMARY KEY (user_id, category_id);


--
-- Name: user_keyword_read_stats user_keyword_read_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_keyword_read_stats
    ADD CONSTRAINT user_keyword_read_stats_pkey PRIMARY KEY (user_id, keyword);


--
-- Name: user_keyword_subscriptions user_keyword_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_keyword_subscriptions
    ADD CONSTRAINT user_keyword_subscriptions_pkey PRIMARY KEY (user_id, keyword);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: ix_ai_generated_news_ai_generated_news_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_ai_generated_news_ai_generated_news_id ON public.ai_generated_news USING btree (ai_generated_news_id);


--
-- Name: ix_ai_generated_news_category_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_ai_generated_news_category_id ON public.ai_generated_news USING btree (category_id);


--
-- Name: ix_ai_generated_news_cluster_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_ai_generated_news_cluster_id ON public.ai_generated_news USING btree (cluster_id);


--
-- Name: ix_categories_name; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_categories_name ON public.categories USING btree (name);


--
-- Name: ix_clusters_cluster_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_clusters_cluster_id ON public.clusters USING btree (cluster_id);


--
-- Name: ix_companies_name; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_companies_name ON public.companies USING btree (name);


--
-- Name: ix_news_category_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_category_id ON public.news USING btree (category_id);


--
-- Name: ix_news_company_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_company_id ON public.news USING btree (company_id);


--
-- Name: ix_news_is_domestic; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_is_domestic ON public.news USING btree (is_domestic);


--
-- Name: ix_news_news_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_news_id ON public.news USING btree (news_id);


--
-- Name: ix_news_reactions_news_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_reactions_news_id ON public.news_reactions USING btree (news_id);


--
-- Name: ix_news_reactions_user_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_reactions_user_id ON public.news_reactions USING btree (user_id);


--
-- Name: ix_news_url; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_news_url ON public.news USING btree (url);


--
-- Name: ix_news_views_category_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_views_category_id ON public.news_views USING btree (category_id);


--
-- Name: ix_news_views_news_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_views_news_id ON public.news_views USING btree (news_id);


--
-- Name: ix_news_views_user_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_news_views_user_id ON public.news_views USING btree (user_id);


--
-- Name: ix_search_logs_user_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_search_logs_user_id ON public.search_logs USING btree (user_id);


--
-- Name: ix_users_login_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_users_login_id ON public.users USING btree (login_id);


--
-- Name: ai_generated_news ai_generated_news_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.ai_generated_news
    ADD CONSTRAINT ai_generated_news_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE RESTRICT;


--
-- Name: ai_generated_news ai_generated_news_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.ai_generated_news
    ADD CONSTRAINT ai_generated_news_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;


--
-- Name: cluster_news_link cluster_news_link_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cluster_news_link
    ADD CONSTRAINT cluster_news_link_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;


--
-- Name: cluster_news_link cluster_news_link_news_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cluster_news_link
    ADD CONSTRAINT cluster_news_link_news_id_fkey FOREIGN KEY (news_id) REFERENCES public.news(news_id) ON DELETE CASCADE;


--
-- Name: news news_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: news news_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(company_id) ON DELETE RESTRICT;


--
-- Name: news_reactions news_reactions_news_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_reactions
    ADD CONSTRAINT news_reactions_news_id_fkey FOREIGN KEY (news_id) REFERENCES public.ai_generated_news(ai_generated_news_id) ON DELETE CASCADE;


--
-- Name: news_reactions news_reactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_reactions
    ADD CONSTRAINT news_reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: news_views news_views_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views
    ADD CONSTRAINT news_views_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: news_views news_views_news_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views
    ADD CONSTRAINT news_views_news_id_fkey FOREIGN KEY (news_id) REFERENCES public.ai_generated_news(ai_generated_news_id) ON DELETE CASCADE;


--
-- Name: news_views news_views_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.news_views
    ADD CONSTRAINT news_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: search_logs search_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.search_logs
    ADD CONSTRAINT search_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_category_subscriptions user_category_subscriptions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_category_subscriptions
    ADD CONSTRAINT user_category_subscriptions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE CASCADE;


--
-- Name: user_category_subscriptions user_category_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_category_subscriptions
    ADD CONSTRAINT user_category_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_keyword_read_stats user_keyword_read_stats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_keyword_read_stats
    ADD CONSTRAINT user_keyword_read_stats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: user_keyword_subscriptions user_keyword_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.user_keyword_subscriptions
    ADD CONSTRAINT user_keyword_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict IzTnjUN8eqQobfDtEG5ul6U1m1cVHvbXVrnY0H6YWVrPPWccPjxLk8hVrynkUcE

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict crY7RnaDCOjQ0hanNAgz6tsfq3AtUmwnimqp5IuMBYpjFXDOWzBuzSIQj5KFItz

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

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
-- PostgreSQL database dump complete
--

\unrestrict crY7RnaDCOjQ0hanNAgz6tsfq3AtUmwnimqp5IuMBYpjFXDOWzBuzSIQj5KFItz

--
-- PostgreSQL database cluster dump complete
--

