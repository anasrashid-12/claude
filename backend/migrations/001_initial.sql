-- Create shops table
CREATE TABLE IF NOT EXISTS shops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_url TEXT NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    shop_name TEXT NOT NULL,
    email TEXT,
    plan_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    processing_enabled BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create image_jobs table
CREATE TABLE IF NOT EXISTS image_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    product_id TEXT,
    image_url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    processing_type TEXT[] NOT NULL,
    result_url TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_shops_url ON shops(shop_url);
CREATE INDEX IF NOT EXISTS idx_image_jobs_shop_id ON image_jobs(shop_id);
CREATE INDEX IF NOT EXISTS idx_image_jobs_status ON image_jobs(status);
CREATE INDEX IF NOT EXISTS idx_image_jobs_created_at ON image_jobs(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_shops_updated_at
    BEFORE UPDATE ON shops
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_image_jobs_updated_at
    BEFORE UPDATE ON image_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 