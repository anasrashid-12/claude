-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create stores table
CREATE TABLE IF NOT EXISTS stores (
    id BIGSERIAL PRIMARY KEY,
    shop_domain VARCHAR(255) NOT NULL UNIQUE,
    access_token VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    installed_at TIMESTAMP WITH TIME ZONE,
    uninstalled_at TIMESTAMP WITH TIME ZONE,
    shop_name VARCHAR(255),
    shop_email VARCHAR(255),
    shop_plan VARCHAR(100),
    shop_owner VARCHAR(255),
    shop_country VARCHAR(2),
    shop_currency VARCHAR(3),
    shop_timezone VARCHAR(100),
    myshopify_domain VARCHAR(255) NOT NULL,
    primary_locale VARCHAR(10) DEFAULT 'en',
    plan_name VARCHAR(100),
    plan_display_name VARCHAR(100),
    api_version VARCHAR(20) DEFAULT '2024-01'
);

-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id BIGSERIAL PRIMARY KEY,
    store_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    product_id VARCHAR(255) NOT NULL,
    image_id VARCHAR(255) NOT NULL,
    original_url TEXT NOT NULL,
    processed_url TEXT,
    position INTEGER,
    alt_text TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    processing_types TEXT[] NOT NULL,
    processing_options JSONB,
    error_message TEXT,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    task_id VARCHAR(255),
    version INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(store_id, product_id, image_id, version)
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    store_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL,
    celery_task_id VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'pending',
    params JSONB,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    retries INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    eta TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_stores_shop_domain ON stores(shop_domain);
CREATE INDEX idx_images_store_id ON images(store_id);
CREATE INDEX idx_images_product_id ON images(product_id);
CREATE INDEX idx_images_status ON images(status);
CREATE INDEX idx_tasks_store_id ON tasks(store_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_celery_id ON tasks(celery_task_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_images_updated_at
    BEFORE UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 