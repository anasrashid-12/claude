-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');
    CREATE TYPE image_operation AS ENUM ('background_removal', 'resize', 'optimize', 'revert');
    CREATE TYPE store_user_role AS ENUM ('owner', 'admin', 'editor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create updated_at column function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create stores table
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_domain TEXT NOT NULL UNIQUE,
    access_token TEXT,
    shop_name TEXT,
    email TEXT,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    uninstalled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create store_users table
CREATE TABLE IF NOT EXISTS store_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role store_user_role NOT NULL DEFAULT 'editor',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(store_id, user_id)
);

-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    shopify_image_id TEXT NOT NULL,
    original_url TEXT NOT NULL,
    current_url TEXT NOT NULL,
    position INTEGER,
    width INTEGER,
    height INTEGER,
    format TEXT,
    status processing_status DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(store_id, shopify_image_id)
);

-- Create processing_history table
CREATE TABLE IF NOT EXISTS processing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    operation image_operation NOT NULL,
    status processing_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time INTEGER, -- in milliseconds
    error_message TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create image_versions table
CREATE TABLE IF NOT EXISTS image_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_id UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    url TEXT NOT NULL,
    operation image_operation NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(image_id, version_number)
);

-- Create triggers
CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_store_users_updated_at
    BEFORE UPDATE ON store_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_images_updated_at
    BEFORE UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_history_updated_at
    BEFORE UPDATE ON processing_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stores_shop_domain ON stores(shop_domain);
CREATE INDEX IF NOT EXISTS idx_store_users_store_id ON store_users(store_id);
CREATE INDEX IF NOT EXISTS idx_store_users_user_id ON store_users(user_id);
CREATE INDEX IF NOT EXISTS idx_images_store_id ON images(store_id);
CREATE INDEX IF NOT EXISTS idx_images_product_id ON images(product_id);
CREATE INDEX IF NOT EXISTS idx_images_status ON images(status);
CREATE INDEX IF NOT EXISTS idx_images_shopify_id ON images(shopify_image_id);
CREATE INDEX IF NOT EXISTS idx_processing_history_image_id ON processing_history(image_id);
CREATE INDEX IF NOT EXISTS idx_processing_history_status ON processing_history(status);
CREATE INDEX IF NOT EXISTS idx_image_versions_image_id ON image_versions(image_id);
CREATE INDEX IF NOT EXISTS idx_image_versions_version_number ON image_versions(version_number); 