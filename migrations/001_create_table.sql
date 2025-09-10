create table if not exists public.analyses (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  text text not null,
  title text null,
  summary text not null,
  topics text[] not null,
  sentiment text not null check (sentiment in ('positive','neutral','negative')),
  keywords text[] not null,
  confidence double precision not null check (confidence >= 0.0 and confidence <= 1.0)
);

create index if not exists idx_analyses_topics_gin on public.analyses using gin (topics);
create index if not exists idx_analyses_keywords_gin on public.analyses using gin (keywords);