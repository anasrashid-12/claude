-- Drop existing tables if they exist
drop table if exists image_processing_history;
drop table if exists images;

-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create images table
create table public.images (
    id uuid default uuid_generate_v4() primary key,
    auth_user_id uuid references auth.users(id) not null,
    product_id text not null,
    shopify_id text,
    original_url text not null,
    processed_url text,
    status text not null default 'pending',
    processing_options jsonb default '{}',
    error_message text,
    is_active boolean default true,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create image processing history table
create table public.image_processing_history (
    id uuid default uuid_generate_v4() primary key,
    image_id uuid references public.images(id) on delete cascade,
    operation text not null,
    status text not null,
    error_message text,
    processing_time integer not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create updated_at function
create or replace function public.update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

-- Create trigger for updated_at
drop trigger if exists update_images_updated_at on public.images;
create trigger update_images_updated_at
    before update on public.images
    for each row
    execute function public.update_updated_at_column();

-- Enable Row Level Security
alter table public.images enable row level security;
alter table public.image_processing_history enable row level security;

-- Drop existing policies if they exist
drop policy if exists "Users can view their own images" on public.images;
drop policy if exists "Users can insert their own images" on public.images;
drop policy if exists "Users can update their own images" on public.images;
drop policy if exists "Users can delete their own images" on public.images;
drop policy if exists "Users can view history of their own images" on public.image_processing_history;
drop policy if exists "Users can insert history for their own images" on public.image_processing_history;

-- Create policies for images table
create policy "Users can view their own images"
    on public.images for select
    using (auth.uid() = auth_user_id);

create policy "Users can insert their own images"
    on public.images for insert
    with check (auth.uid() = auth_user_id);

create policy "Users can update their own images"
    on public.images for update
    using (auth.uid() = auth_user_id);

create policy "Users can delete their own images"
    on public.images for delete
    using (auth.uid() = auth_user_id);

-- Create policies for image_processing_history table
create policy "Users can view history of their own images"
    on public.image_processing_history for select
    using (
        exists (
            select 1 from public.images
            where images.id = image_processing_history.image_id
            and images.auth_user_id = auth.uid()
        )
    );

create policy "Users can insert history for their own images"
    on public.image_processing_history for insert
    with check (
        exists (
            select 1 from public.images
            where images.id = image_processing_history.image_id
            and images.auth_user_id = auth.uid()
        )
    );

-- Drop existing indexes if they exist
drop index if exists idx_images_auth_user_id;
drop index if exists idx_images_product_id;
drop index if exists idx_images_shopify_id;
drop index if exists idx_images_status;
drop index if exists idx_image_processing_history_image_id;

-- Create indexes
create index idx_images_auth_user_id on public.images(auth_user_id);
create index idx_images_product_id on public.images(product_id);
create index idx_images_shopify_id on public.images(shopify_id);
create index idx_images_status on public.images(status);
create index idx_image_processing_history_image_id on public.image_processing_history(image_id);

-- Create storage bucket for images
-- Note: This needs to be done through the Supabase dashboard or API
-- insert into storage.buckets (id, name)
-- values ('images', 'images')
-- on conflict do nothing; 