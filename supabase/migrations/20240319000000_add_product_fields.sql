-- Add new columns to products table
ALTER TABLE products
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS description TEXT;

-- Update existing columns to be nullable
ALTER TABLE products
ALTER COLUMN shopify_product_id DROP NOT NULL,
ALTER COLUMN title DROP NOT NULL; 