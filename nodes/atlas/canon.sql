/* THE CANON (v1.0)
  The Digital Constitution of the Ministry of Influence.
  
  Three Pillars:
  1. DISTRICTS (The Map)
  2. CANDIDATES (The Players)
  3. COMMUNICATIONS (The Narrative)
  
  Policy: NO Vendor-Specific Code. Pure PostgreSQL.
*/

-- 1. THE FOUNDATION (Extensions)
-- We enable the senses: Location (PostGIS) and Intuition (pgvector).
create extension if not exists postgis schema public;
create extension if not exists vector schema public;

-- 2. PILLAR I: DISTRICTS (The Map)
-- Defines the physical game board.
create table if not exists public.districts (
  id uuid primary key default gen_random_uuid(),
  code text not null unique, -- e.g. "US-FL-07", "FL-SEN-09"
  name text not null,        -- e.g. "Florida 7th Congressional District"
  type text not null check (type in ('federal', 'state_senate', 'state_house', 'local')),
  state text default 'FL',
  boundary geometry(MULTIPOLYGON, 4326),
  center geometry(POINT, 4326) generated always as (ST_Centroid(boundary)) stored,
  demographics jsonb default '{}'::jsonb, -- Store census data here (agile schema)
  created_at timestamptz default now()
);

-- Indexing for "Who is near me?" speed
create index if not exists districts_geo_idx on public.districts using GIST (boundary);


-- 3. PILLAR II: CANDIDATES (The Players)
-- Defines the actors on the board.
create table if not exists public.candidates (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  party text check (party in ('R', 'D', 'I', 'L', 'G', 'W')),
  status text default 'active' check (status in ('active', 'retired', 'defeated')),
  target_district_id uuid references public.districts(id),
  
  -- The Dossier (Flexible JSON for evolving intel)
  dossier jsonb default '{}'::jsonb, -- e.g. {"brain_actor_id": "..."}
  campaign_headquarters_address text, -- For Geocoding/Linkage
  
  social_handles jsonb default '{}'::jsonb, -- e.g. {"x": "@user", "truth": "@user"}
  biography text,
  
  -- Vectorized Persona (The "Vibe" of the candidate)
  persona_embedding vector(1536), 
  
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Indexing for fast lookups
create index if not exists candidates_district_idx on public.candidates(target_district_id);


-- 4. PILLAR III: COMMUNICATIONS (The Narrative)
-- The atomic unit of influence. Tweets, Speeches, Ads.
create table if not exists public.communications (
  id uuid primary key default gen_random_uuid(),
  
  -- Attribution
  candidate_id uuid references public.candidates(id) on delete cascade,
  district_id uuid references public.districts(id), -- Nullable: Some narratives are global
  
  -- The Content
  source_platform text not null, -- 'x', 'bluesky', 'news', 'press_release'
  source_url text,
  content text not null,
  published_at timestamptz not null,
  
  -- The Resonance (Quantization)
  -- 1536 dimensions compatible with OpenAI/Ollama embeddings
  embedding vector(1536),
  
  -- Metadata (Likes, Retweets, Sentiment Score)
  metrics jsonb default '{}'::jsonb, 
  
  created_at timestamptz default now()
);

-- 5. THE CORTEX INDICES (Semantic Search)
-- Allows the Ministry to ask: "Show me angry tweets about water quality."
create index if not exists communications_embedding_idx 
on public.communications 
using hnsw (embedding vector_cosine_ops);

-- Allows looking up narratives by time (Timeline View)
create index if not exists communications_date_idx on public.communications(published_at);

/* END OF CANON 
  "Reality is now defined." 
*/
