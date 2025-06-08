-- Create buckets if they don't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('original-images', 'original-images', false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('processed-images', 'processed-images', false)
ON CONFLICT (id) DO NOTHING;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Authenticated users can upload original images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can view original images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload processed images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can view processed images" ON storage.objects;

-- Create storage policies
CREATE POLICY "Authenticated users can upload original images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'original-images' AND
        auth.role() = 'authenticated'
    );

CREATE POLICY "Authenticated users can view original images"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'original-images' AND
        auth.role() = 'authenticated'
    );

CREATE POLICY "Authenticated users can upload processed images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'processed-images' AND
        auth.role() = 'authenticated'
    );

CREATE POLICY "Authenticated users can view processed images"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'processed-images' AND
        auth.role() = 'authenticated'
    ); 