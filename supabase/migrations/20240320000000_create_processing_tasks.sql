-- Create store_users table for managing store access
CREATE TABLE IF NOT EXISTS store_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(store_id, user_id)
);

-- Create processing_tasks table
CREATE TABLE IF NOT EXISTS processing_tasks (
    id UUID PRIMARY KEY,
    store_id UUID REFERENCES stores(id),
    original_filename TEXT NOT NULL,
    process_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    result_url TEXT,
    celery_task_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add RLS policies
ALTER TABLE store_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_tasks ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to view their own store's tasks
CREATE POLICY "Users can view their store's tasks"
    ON processing_tasks
    FOR SELECT
    USING (auth.uid() IN (
        SELECT user_id FROM store_users WHERE store_id = processing_tasks.store_id
    ));

-- Allow authenticated users to create tasks for their stores
CREATE POLICY "Users can create tasks for their stores"
    ON processing_tasks
    FOR INSERT
    WITH CHECK (auth.uid() IN (
        SELECT user_id FROM store_users WHERE store_id = store_id
    ));

-- Allow users to view their store associations
CREATE POLICY "Users can view their store associations"
    ON store_users
    FOR SELECT
    USING (auth.uid() = user_id);

-- Allow users to manage their store associations
CREATE POLICY "Users can manage their store associations"
    ON store_users
    FOR ALL
    USING (auth.uid() = user_id);

-- Create storage bucket for processed images if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('images', 'images', true)
ON CONFLICT (id) DO NOTHING;

-- Add storage policies
DROP POLICY IF EXISTS "Public read access" ON storage.objects;
CREATE POLICY "Public read access"
    ON storage.objects
    FOR SELECT
    USING (bucket_id = 'images');

DROP POLICY IF EXISTS "Authenticated users can upload images" ON storage.objects;
CREATE POLICY "Authenticated users can upload images"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'images'
        AND auth.role() = 'authenticated'
    ); 