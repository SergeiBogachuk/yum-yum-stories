create table if not exists public.analytics_events (
    id bigint generated always as identity primary key,
    event_name text not null,
    user_email text,
    properties jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists analytics_events_event_name_idx
    on public.analytics_events (event_name);

create index if not exists analytics_events_user_email_idx
    on public.analytics_events (user_email);

create index if not exists analytics_events_created_at_idx
    on public.analytics_events (created_at desc);
