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

-- Create batch_jobs table
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    status processing_status NOT NULL DEFAULT 'pending',
    total_images INTEGER NOT NULL DEFAULT 0,
    processed_images INTEGER NOT NULL DEFAULT 0,
    failed_images INTEGER NOT NULL DEFAULT 0,
    settings JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create batch_job_items table
CREATE TABLE IF NOT EXISTS batch_job_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_job_id UUID NOT NULL REFERENCES batch_jobs(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    status processing_status NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create processing_tasks table
CREATE TABLE IF NOT EXISTS processing_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    celery_task_id TEXT,
    task_type TEXT NOT NULL,
    status processing_status NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create triggers
CREATE TRIGGER update_batch_jobs_updated_at
    BEFORE UPDATE ON batch_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_job_items_updated_at
    BEFORE UPDATE ON batch_job_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_tasks_updated_at
    BEFORE UPDATE ON processing_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_batch_jobs_store_id ON batch_jobs(store_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX IF NOT EXISTS idx_batch_job_items_batch_job_id ON batch_job_items(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_job_items_image_id ON batch_job_items(image_id);
CREATE INDEX IF NOT EXISTS idx_batch_job_items_status ON batch_job_items(status);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_store_id ON processing_tasks(store_id);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_celery_id ON processing_tasks(celery_task_id);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_status ON processing_tasks(status);

-- Enable Row Level Security
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_job_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_tasks ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Store users can view their batch jobs"
    ON batch_jobs
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = batch_jobs.store_id 
            AND store_users.user_id = auth.uid()
        )
    );

CREATE POLICY "Store users can view their batch job items"
    ON batch_job_items
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = (
                SELECT store_id FROM batch_jobs 
                WHERE batch_jobs.id = batch_job_items.batch_job_id
            )
            AND store_users.user_id = auth.uid()
        )
    );

CREATE POLICY "Store users can view their processing tasks"
    ON processing_tasks
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = processing_tasks.store_id 
            AND store_users.user_id = auth.uid()
        )
    );

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