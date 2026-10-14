-- =====================================================================
-- Gastô · banco de dados no Supabase
-- Como usar: Supabase → SQL Editor → New query → cole TUDO → Run.
-- Pode rodar de novo sem problema (não apaga dados).
-- O mesmo banco vai servir o app nativo (Expo) depois.
-- =====================================================================

create extension if not exists pgcrypto;

-- Família: o grupo que compartilha os gastos (ex.: Kaue + Kaoanna)
create table if not exists public.families (
  id          uuid primary key default gen_random_uuid(),
  name        text not null default 'Família',
  code        text not null unique default upper(substr(md5(random()::text || clock_timestamp()::text), 1, 6)),
  created_by  uuid not null default auth.uid() references auth.users(id),
  created_at  timestamptz not null default now()
);

-- Quem faz parte de cada família, e qual "pessoa" do app é cada login
create table if not exists public.members (
  family_id   uuid not null references public.families(id) on delete cascade,
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  person_id   text,
  email       text,
  created_at  timestamptz not null default now(),
  primary key (family_id, user_id)
);

-- Tudo do app: pessoas, cartões, categorias, gastos, lojas aprendidas e ajustes.
-- Uma linha por item; "deleted" marca o que foi apagado (para sincronizar entre os celulares).
create table if not exists public.items (
  family_id   uuid not null references public.families(id) on delete cascade,
  kind        text not null,              -- person | card | category | expense | rule | meta
  id          text not null,
  data        jsonb not null default '{}'::jsonb,
  deleted     boolean not null default false,
  updated_at  timestamptz not null default now(),
  updated_by  uuid default auth.uid(),
  primary key (family_id, kind, id)
);
create index if not exists items_family_updated on public.items (family_id, updated_at);

create or replace function public.touch_item() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  new.updated_by := auth.uid();
  return new;
end $$;
drop trigger if exists items_touch on public.items;
create trigger items_touch before insert or update on public.items
  for each row execute function public.touch_item();

-- Regras de acesso: cada um só vê os dados da própria família
create or replace function public.is_member(f uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from members where family_id = f and user_id = auth.uid())
$$;

-- Acesso pela API (funciona com "Expor automaticamente novas tabelas" ligado ou desligado)
grant usage on schema public to authenticated;
grant select, insert, update, delete on public.families, public.members, public.items to authenticated;
revoke all on public.families, public.members, public.items from anon;

alter table public.families enable row level security;
alter table public.members  enable row level security;
alter table public.items    enable row level security;

drop policy if exists fam_select on public.families;
create policy fam_select on public.families for select using (public.is_member(id));
drop policy if exists fam_update on public.families;
create policy fam_update on public.families for update using (public.is_member(id));

drop policy if exists mem_select on public.members;
create policy mem_select on public.members for select using (public.is_member(family_id));
drop policy if exists mem_update_own on public.members;
create policy mem_update_own on public.members for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists mem_delete_own on public.members;
create policy mem_delete_own on public.members for delete using (user_id = auth.uid());

drop policy if exists items_all on public.items;
create policy items_all on public.items for all
  using (public.is_member(family_id)) with check (public.is_member(family_id));

-- Criar família (quem começa) e entrar com o código (os outros)
create or replace function public.create_family(p_name text, p_person text) returns public.families
language plpgsql security definer set search_path = public as $$
declare f families;
begin
  if auth.uid() is null then raise exception 'not logged in'; end if;
  insert into families (name, created_by) values (coalesce(nullif(trim(p_name), ''), 'Família'), auth.uid()) returning * into f;
  insert into members (family_id, user_id, person_id, email)
    values (f.id, auth.uid(), p_person, (select email from auth.users where id = auth.uid()));
  return f;
end $$;

create or replace function public.join_family(p_code text) returns public.families
language plpgsql security definer set search_path = public as $$
declare f families;
begin
  if auth.uid() is null then raise exception 'not logged in'; end if;
  select * into f from families where code = upper(trim(p_code));
  if f.id is null then raise exception 'codigo invalido'; end if;
  insert into members (family_id, user_id, email)
    values (f.id, auth.uid(), (select email from auth.users where id = auth.uid()))
    on conflict (family_id, user_id) do nothing;
  return f;
end $$;

revoke all on function public.create_family(text, text) from public, anon;
revoke all on function public.join_family(text) from public, anon;
grant execute on function public.create_family(text, text) to authenticated;
grant execute on function public.join_family(text) to authenticated;

-- Tempo real: o que um lança aparece no celular do outro
do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'items') then
    alter publication supabase_realtime add table public.items;
  end if;
end $$;
