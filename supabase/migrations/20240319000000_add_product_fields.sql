-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    shopify_product_id TEXT NOT NULL,
    title TEXT NOT NULL,
    name VARCHAR(255),
    price DECIMAL(10,2),
    description TEXT,
    handle TEXT,
    vendor TEXT,
    product_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_processed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(store_id, shopify_product_id)
);

-- Create store_settings table
CREATE TABLE IF NOT EXISTS store_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    default_image_settings JSONB DEFAULT '{}'::jsonb,
    auto_process_new_images BOOLEAN DEFAULT false,
    notification_email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(store_id)
);

-- Create triggers
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_store_settings_updated_at
    BEFORE UPDATE ON store_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_shopify_id ON products(shopify_product_id);
CREATE INDEX IF NOT EXISTS idx_products_updated_at ON products(updated_at);

-- Enable Row Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_settings ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Store users can view their products"
    ON products
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = products.store_id 
            AND store_users.user_id = auth.uid()
        )
    );

CREATE POLICY "Store users can view their store settings"
    ON store_settings
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = store_settings.store_id 
            AND store_users.user_id = auth.uid()
        )
    );

CREATE POLICY "Store admins can update store settings"
    ON store_settings
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM store_users 
            WHERE store_users.store_id = store_settings.store_id 
            AND store_users.user_id = auth.uid()
            AND store_users.role IN ('owner', 'admin')
        )
    );