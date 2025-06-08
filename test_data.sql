-- Insert test store
INSERT INTO stores (id, shop_domain, access_token, plan_type)
VALUES (
    'e629c1e7-3f2c-4c51-b3d3-26c06318f735',
    'test-store.myshopify.com',
    'shpat_test_token_123',
    'basic'
) ON CONFLICT (shop_domain) DO NOTHING;

-- Insert test store settings
INSERT INTO store_settings (store_id, default_image_settings, auto_process_new_images, notification_email)
VALUES (
    'e629c1e7-3f2c-4c51-b3d3-26c06318f735',
    '{"quality": 80, "format": "webp", "background_removal": true}'::jsonb,
    true,
    'test@example.com'
) ON CONFLICT (store_id) DO NOTHING;

-- Insert test products
INSERT INTO products (id, store_id, shopify_product_id, title, name, price, description)
VALUES 
    ('f7e3a42d-8c4b-4c1e-9a6f-3c1a3f7d8e9b', 'e629c1e7-3f2c-4c51-b3d3-26c06318f735', '123456789', 'Test Product 1', 'Cool T-Shirt', 29.99, 'A very cool t-shirt'),
    ('b2c3d4e5-f6g7-8h9i-j0k1-l2m3n4o5p6q7', 'e629c1e7-3f2c-4c51-b3d3-26c06318f735', '987654321', 'Test Product 2', 'Awesome Hoodie', 59.99, 'A very warm hoodie')
ON CONFLICT (store_id, shopify_product_id) DO NOTHING;

-- Insert test images
INSERT INTO images (id, product_id, shopify_image_id, original_url, current_url, position, width, height, format)
VALUES 
    (
        'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
        'f7e3a42d-8c4b-4c1e-9a6f-3c1a3f7d8e9b',
        'img_123',
        'https://example.com/original/tshirt.jpg',
        'https://example.com/current/tshirt.jpg',
        1,
        800,
        800,
        'jpg'
    ),
    (
        'b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7',
        'f7e3a42d-8c4b-4c1e-9a6f-3c1a3f7d8e9b',
        'img_124',
        'https://example.com/original/tshirt_back.jpg',
        'https://example.com/current/tshirt_back.jpg',
        2,
        800,
        800,
        'jpg'
    ),
    (
        'c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8',
        'b2c3d4e5-f6g7-8h9i-j0k1-l2m3n4o5p6q7',
        'img_789',
        'https://example.com/original/hoodie.jpg',
        'https://example.com/current/hoodie.jpg',
        1,
        1000,
        1000,
        'jpg'
    )
ON CONFLICT (product_id, shopify_image_id) DO NOTHING;

-- Insert test processing history
INSERT INTO processing_history (image_id, operation, status, settings, backup_url)
VALUES 
    (
        'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
        'background_removal',
        'completed',
        '{"quality": 90}'::jsonb,
        'https://example.com/backup/tshirt_v1.jpg'
    ),
    (
        'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
        'optimize',
        'pending',
        '{"format": "webp"}'::jsonb,
        null
    ),
    (
        'c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8',
        'resize',
        'processing',
        '{"width": 500, "height": 500}'::jsonb,
        'https://example.com/backup/hoodie_v1.jpg'
    );

-- Insert test image versions
INSERT INTO image_versions (image_id, version_number, storage_url)
VALUES 
    ('a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6', 1, 'https://example.com/versions/tshirt_v1.jpg'),
    ('a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6', 2, 'https://example.com/versions/tshirt_v2.jpg'),
    ('c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8', 1, 'https://example.com/versions/hoodie_v1.jpg');

-- Insert test processing tasks
INSERT INTO processing_tasks (id, store_id, original_filename, process_type, status, celery_task_id)
VALUES 
    (
        'e5f6g7h8-i9j0-k1l2-m3n4-o5p6q7r8s9t0',
        'e629c1e7-3f2c-4c51-b3d3-26c06318f735',
        'new_product.jpg',
        'background_removal',
        'pending',
        'celery_123'
    ),
    (
        'f6g7h8i9-j0k1-l2m3-n4o5-p6q7r8s9t0u1',
        'e629c1e7-3f2c-4c51-b3d3-26c06318f735',
        'another_product.jpg',
        'optimize',
        'processing',
        'celery_456'
    );

-- Insert test store user
INSERT INTO store_users (store_id, user_id, role)
VALUES (
    'e629c1e7-3f2c-4c51-b3d3-26c06318f735',
    auth.uid(),  -- This will use the current authenticated user's ID
    'admin'
); 