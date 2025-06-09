-- Add missing enum type for user roles if it doesn't exist
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- First, update existing roles to match the enum values
UPDATE store_users 
SET role = CASE 
    WHEN role = 'member' THEN 'member'
    WHEN role = 'admin' THEN 'admin'
    ELSE 'member'
END;

-- Create a temporary column with the new type
ALTER TABLE store_users 
ADD COLUMN role_enum user_role;

-- Copy data to the new column
UPDATE store_users 
SET role_enum = role::user_role;

-- Drop the old column
ALTER TABLE store_users 
DROP COLUMN role;

-- Set constraints on the new column
ALTER TABLE store_users 
ALTER COLUMN role_enum SET NOT NULL,
ALTER COLUMN role_enum SET DEFAULT 'member';

-- Rename the new column
ALTER TABLE store_users 
RENAME COLUMN role_enum TO role;

-- Add missing indexes for better performance
CREATE INDEX IF NOT EXISTS idx_store_users_user_id ON store_users(user_id);
CREATE INDEX IF NOT EXISTS idx_store_users_store_id ON store_users(store_id);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_store_id ON processing_tasks(store_id);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_status ON processing_tasks(status);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_celery_task_id ON processing_tasks(celery_task_id);

-- Add missing columns to stores table for better store management
ALTER TABLE stores
ADD COLUMN IF NOT EXISTS webhook_secret TEXT,
ADD COLUMN IF NOT EXISTS webhook_url TEXT,
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'trial',
ADD COLUMN IF NOT EXISTS subscription_ends_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS monthly_api_limit INTEGER DEFAULT 1000,
ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}'::jsonb;

-- Add missing columns to processing_tasks table
ALTER TABLE processing_tasks
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS processing_options JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Create batch_jobs table for handling bulk operations
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status processing_status DEFAULT 'pending',
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    error_details JSONB DEFAULT '{}'::jsonb,
    options JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create batch_job_items table for tracking individual items in a batch
CREATE TABLE IF NOT EXISTS batch_job_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,
    item_id UUID NOT NULL,
    status processing_status DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Add indexes for batch processing tables
CREATE INDEX IF NOT EXISTS idx_batch_jobs_store_id ON batch_jobs(store_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX IF NOT EXISTS idx_batch_job_items_batch_job_id ON batch_job_items(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_job_items_status ON batch_job_items(status);

-- Create trigger for batch_jobs updated_at
CREATE TRIGGER update_batch_jobs_updated_at
    BEFORE UPDATE ON batch_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for batch_job_items updated_at
CREATE TRIGGER update_batch_job_items_updated_at
    BEFORE UPDATE ON batch_job_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS on new tables
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_job_items ENABLE ROW LEVEL SECURITY;

-- Add RLS policies for batch_jobs
CREATE POLICY "Users can view their store's batch jobs"
    ON batch_jobs
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users su 
            WHERE su.store_id = batch_jobs.store_id 
            AND su.user_id = auth.uid()
        )
    );

CREATE POLICY "Store admins can manage batch jobs"
    ON batch_jobs
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM store_users su 
            WHERE su.store_id = batch_jobs.store_id 
            AND su.user_id = auth.uid()
            AND su.role IN ('admin', 'owner')
        )
    );

-- Add RLS policies for batch_job_items
CREATE POLICY "Users can view their store's batch job items"
    ON batch_job_items
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM batch_jobs bj
            JOIN store_users su ON su.store_id = bj.store_id
            WHERE bj.id = batch_job_items.batch_job_id
            AND su.user_id = auth.uid()
        )
    );

-- Add storage bucket for original images if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('original-images', 'original-images', false)
ON CONFLICT (id) DO NOTHING;

-- Add storage policy for original images
CREATE POLICY "Authenticated users can access original images"
    ON storage.objects
    FOR ALL
    USING (
        bucket_id = 'original-images'
        AND auth.role() = 'authenticated'
        AND EXISTS (
            SELECT 1 FROM store_users su
            WHERE su.user_id = auth.uid()
        )
    ); 