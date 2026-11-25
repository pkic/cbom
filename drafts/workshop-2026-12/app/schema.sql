-- CBOM Tabletop Live: Supabase setup.
-- Run once in the Supabase SQL editor (Dashboard > SQL editor > New query).
-- Then change the facilitator PIN in the last statement before you run it.

create table if not exists ws_state (
  id int primary key default 1 check (id = 1),
  data jsonb not null default '{"stage":"lobby"}',
  updated_at timestamptz not null default now()
);
insert into ws_state (id) values (1) on conflict do nothing;

create table if not exists ws_people (
  id text primary key,
  name text not null check (length(name) between 1 and 80),
  table_no int check (table_no between 1 and 60),
  role text,
  updated_at timestamptz not null default now()
);

create table if not exists ws_items (
  id text primary key check (length(id) < 120),
  kind text not null check (kind in ('plan','gap','inject','prio','poll')),
  table_no int check (table_no between 1 and 60),
  person text,
  payload jsonb not null check (pg_column_size(payload) < 4000),
  updated_at timestamptz not null default now()
);
create index if not exists ws_items_updated on ws_items (updated_at);
create index if not exists ws_items_table on ws_items (table_no);
create index if not exists ws_people_updated on ws_people (updated_at);

-- Email addresses live in their own table. Participants can add a row but nobody can read it
-- except through ws_export_signups, which needs the facilitator PIN.
create table if not exists ws_signups (
  person text primary key,
  name text,
  email text check (length(email) < 200),
  table_no int,
  created_at timestamptz not null default now()
);

create table if not exists ws_secret (pin text not null);

-- The server sets the timestamp, so a phone with a wrong clock cannot confuse the polling.
create or replace function ws_touch() returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists ws_items_touch on ws_items;
create trigger ws_items_touch before insert or update on ws_items for each row execute function ws_touch();
drop trigger if exists ws_people_touch on ws_people;
create trigger ws_people_touch before insert or update on ws_people for each row execute function ws_touch();

alter table ws_state   enable row level security;
alter table ws_people  enable row level security;
alter table ws_items   enable row level security;
alter table ws_signups enable row level security;
alter table ws_secret  enable row level security;

drop policy if exists "read state" on ws_state;
create policy "read state" on ws_state for select to anon using (true);

drop policy if exists "people read" on ws_people;
drop policy if exists "people insert" on ws_people;
drop policy if exists "people update" on ws_people;
create policy "people read"   on ws_people for select to anon using (true);
create policy "people insert" on ws_people for insert to anon with check (true);
create policy "people update" on ws_people for update to anon using (true) with check (true);

drop policy if exists "items read" on ws_items;
drop policy if exists "items insert" on ws_items;
drop policy if exists "items update" on ws_items;
create policy "items read"   on ws_items for select to anon using (true);
create policy "items insert" on ws_items for insert to anon with check (true);
create policy "items update" on ws_items for update to anon using (true) with check (true);

drop policy if exists "signups insert" on ws_signups;
drop policy if exists "signups update" on ws_signups;
drop policy if exists "signups upsert read" on ws_signups;
create policy "signups insert" on ws_signups for insert to anon with check (true);
-- No select policy: the upsert from the page uses return=minimal, so anon never reads emails.

-- Facilitator functions. Each checks the PIN.
create or replace function ws_check_pin(p_pin text) returns boolean
language sql security definer set search_path = public as $$
  select exists (select 1 from ws_secret where pin = p_pin) $$;

create or replace function ws_set_state(p_pin text, p_data jsonb) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not ws_check_pin(p_pin) then raise exception 'wrong pin'; end if;
  update ws_state set data = p_data, updated_at = now() where id = 1;
end $$;

create or replace function ws_delete_item(p_pin text, p_id text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not ws_check_pin(p_pin) then raise exception 'wrong pin'; end if;
  delete from ws_items where id = p_id;
end $$;

create or replace function ws_export_signups(p_pin text) returns setof ws_signups
language plpgsql security definer set search_path = public as $$
begin
  if not ws_check_pin(p_pin) then raise exception 'wrong pin'; end if;
  return query select * from ws_signups order by created_at;
end $$;

create or replace function ws_reset(p_pin text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not ws_check_pin(p_pin) then raise exception 'wrong pin'; end if;
  delete from ws_items where true;
  delete from ws_people where true;
  delete from ws_signups where true;
  update ws_state set data = '{"stage":"lobby"}', updated_at = now() where id = 1;
end $$;

revoke all on function ws_check_pin(text), ws_set_state(text, jsonb), ws_delete_item(text, text),
  ws_export_signups(text), ws_reset(text) from public;
grant execute on function ws_check_pin(text), ws_set_state(text, jsonb), ws_delete_item(text, text),
  ws_export_signups(text), ws_reset(text) to anon;

-- Set the facilitator PIN. Change it before you run this.
delete from ws_secret where true;
insert into ws_secret (pin) values ('change-me-before-december');
