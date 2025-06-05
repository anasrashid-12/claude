-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create storage buckets for image processing
DO $$
BEGIN
    -- Create buckets if they don't exist
    INSERT INTO storage.buckets (id, name, public)
    VALUES 
        ('original-images', 'original-images', false),
        ('processed-images', 'processed-images', true)
    ON CONFLICT (id) DO NOTHING;

    -- Set up security policies for original-images bucket
    CREATE POLICY "Authenticated users can upload original images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'original-images' AND
        auth.role() = 'authenticated'
    );

    CREATE POLICY "Authenticated users can read their original images"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'original-images' AND
        auth.role() = 'authenticated'
    );

    -- Set up security policies for processed-images bucket
    CREATE POLICY "Processed images are publicly readable"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (bucket_id = 'processed-images');

    CREATE POLICY "Only authenticated users can upload processed images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'processed-images' AND
        auth.role() = 'authenticated'
    );
END $$; 