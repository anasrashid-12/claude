-- Drop all existing objects
DO $$ DECLARE
    r RECORD;
BEGIN
    -- Drop triggers
    FOR r IN (SELECT DISTINCT trigger_name, event_object_table 
              FROM information_schema.triggers 
              WHERE trigger_schema = 'public') LOOP
        EXECUTE 'DROP TRIGGER IF EXISTS ' || quote_ident(r.trigger_name) || ' ON public.' || quote_ident(r.event_object_table) || ' CASCADE';
    END LOOP;

    -- Drop tables
    DROP TABLE IF EXISTS batch_job_items CASCADE;
    DROP TABLE IF EXISTS batch_jobs CASCADE;
    DROP TABLE IF EXISTS processing_tasks CASCADE;
    DROP TABLE IF EXISTS processing_history CASCADE;
    DROP TABLE IF EXISTS image_versions CASCADE;
    DROP TABLE IF EXISTS images CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS store_users CASCADE;
    DROP TABLE IF EXISTS store_settings CASCADE;
    DROP TABLE IF EXISTS stores CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS health_check CASCADE;

    -- Drop functions
    DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

    -- Drop types
    DROP TYPE IF EXISTS processing_status CASCADE;
    DROP TYPE IF EXISTS image_operation CASCADE;
    DROP TYPE IF EXISTS store_user_role CASCADE;
    DROP TYPE IF EXISTS user_role CASCADE;
END $$; 