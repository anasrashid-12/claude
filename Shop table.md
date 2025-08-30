create table if not exists shops (
  shop text primary key,
  access_token text not null,
  installed_at timestamp with time zone default timezone('utc'::text, now())
);

alter table shops enable row level security;

create policy "Allow shop to access and manage their own data"
on shops for all
using (shop = current_setting('request.jwt.claim.shop', true))
with check (shop = current_setting('request.jwt.claim.shop', true));

create table if not exists settings (
  shop text primary key references shops(shop) on delete cascade,
  background_removal boolean default true,
  optimize_images boolean default true,
  avatar_url text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

alter table settings enable row level security;

CREATE POLICY "Shop can read own settings"
  ON settings
  FOR SELECT
  USING (
    shop = auth.jwt()->>'shop'
  );
CREATE POLICY "Shop can insert own settings"
  ON settings
  FOR INSERT
  WITH CHECK (
    shop = auth.jwt()->>'shop'
  );
CREATE POLICY "Shop can update own settings"
  ON settings
  FOR UPDATE
  USING (
    shop = auth.jwt()->>'shop'
  );
CREATE POLICY "Shop can delete own settings"
  ON settings
  FOR DELETE
  USING (
    shop = auth.jwt()->>'shop'
  );

create policy "Allow shop to upload to their avatar folder"
on storage.objects for insert
with check (
  bucket_id = 'avatars'
  AND auth.role() = 'authenticated'
  AND split_part(name, '/', 1) = auth.jwt() ->> 'shop'
);
create policy "Allow shop to read their own avatars"
on storage.objects for select
using (
  bucket_id = 'avatars'
  AND auth.role() = 'authenticated'
  AND split_part(name, '/', 1) = auth.jwt() ->> 'shop'
);

create table if not exists images (
  id uuid primary key default gen_random_uuid(),
  shop text not null references shops(shop) on delete cascade,
  original_path text not null,
  processed_path text,
  operation text check (operation in ('remove-bg', 'upscale', 'downscale')) not null,
  status text default 'pending' check (status in ('pending', 'processing', 'processed', 'completed', 'failed', 'queued')),
  error_message text,
  filename text not null,
  task_id text,
  created_at timestamp with time zone default timezone('utc', now()),
  updated_at timestamp with time zone default timezone('utc', now())
);
ALTER TABLE images ADD COLUMN IF NOT EXISTS poll_attempts integer DEFAULT 0;

alter table images enable row level security;

create policy "Shop can read their images"
on images for select
using (auth.jwt() ->> 'shop' = shop);

create policy "Shop can insert their images"
on images for insert
with check (auth.jwt() ->> 'shop' = shop);

ALTER POLICY "Shop can update their images"
ON "public"."images"
TO public
USING (
  (auth.jwt() ->> 'shop') = shop
)
WITH CHECK (
  (auth.jwt() ->> 'shop') = shop
);

create policy "Shop can delete their images"
on images for delete
using (auth.jwt() ->> 'shop' = shop);

create policy "Allow signed uploads" on storage.objects
  for insert
  with check (
    bucket_id = 'makeit3d-public'
    and auth.role() = 'authenticated'
  );

create policy "Allow signed downloads" on storage.objects
  for select
  using (
    bucket_id = 'makeit3d-public'
    and auth.role() = 'authenticated'
  );

CREATE TABLE shop_credits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_domain text NOT NULL REFERENCES shops(shop) ON DELETE CASCADE,
    credits integer NOT NULL DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Auto-update updated_at on change
CREATE OR REPLACE FUNCTION update_shop_credits_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_shop_credits
BEFORE UPDATE ON shop_credits
FOR EACH ROW
EXECUTE FUNCTION update_shop_credits_timestamp();

CREATE TABLE credit_transactions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    shop text not null references shops(shop) on delete cascade,
    change_amount integer NOT NULL, -- +ve add karega, -ve minus karega
    reason text NOT NULL, -- kis wajah se credit add/remove hue
    created_at timestamptz DEFAULT now()
);

ALTER TABLE shop_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Shop can view only own credits"
ON shop_credits
FOR SELECT
USING (shop_domain = auth.jwt() ->> 'shop');

CREATE POLICY "Only service role can update credits"
ON shop_credits
FOR UPDATE
USING (false);

CREATE POLICY "Shop can view only own transactions"
ON credit_transactions
FOR SELECT
USING (shop = auth.jwt() ->> 'shop');

CREATE POLICY "Only service role can insert transactions"
ON credit_transactions
FOR INSERT
WITH CHECK (auth.role() = 'service_role');

-- credit_transactions (idempotent on shop+external_id)
create table if not exists credit_transactions (
  id bigserial primary key,
  shop text not null references shops(shop) on delete cascade,
  change_amount int not null,
  reason text,
  external_id text,      -- Shopify GID of the purchase
  source text,           -- "callback" | "webhook"
  created_at timestamptz default now(),
  unique (shop, external_id)
);

-- credit_pending (track initiated purchases)
create table if not exists credit_pending (
  id bigserial primary key,
  shop_domain text NOT NULL REFERENCES shops(shop) ON DELETE CASCADE,
  plan_id text not null,
  purchase_id text,
  name text,
  status text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- shop_credits (store merchant credit balance)
create table if not exists shop_credits (
  id bigserial primary key,
  shop_domain text NOT NULL REFERENCES shops(shop) ON DELETE CASCADE,
  credits int default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
ALTER TABLE credit_transactions
ADD COLUMN external_id TEXT;
ALTER TABLE credit_transactions
ADD COLUMN source TEXT DEFAULT 'unknown';

ALTER TABLE images ADD COLUMN job_id UUID DEFAULT gen_random_uuid();
ALTER TABLE images ADD COLUMN credits_deducted BOOLEAN DEFAULT FALSE;

