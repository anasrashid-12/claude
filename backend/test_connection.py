from database import Database
import asyncio

async def test_supabase_connection():
    try:
        db = Database()
        # Try to query the stores table
        result = await db.client.from_('stores').select('*').limit(1).execute()
        print("✅ Successfully connected to Supabase!")
        print("✅ Database schema is properly set up!")
        
        # Test storage buckets
        storage_result = await db.client.storage.list_buckets()
        buckets = [bucket['name'] for bucket in storage_result]
        if 'original-images' in buckets and 'processed-images' in buckets:
            print("✅ Storage buckets are properly configured!")
        else:
            print("❌ Storage buckets are missing!")
            print("Expected: original-images, processed-images")
            print(f"Found: {', '.join(buckets)}")
            
    except Exception as e:
        print("❌ Error connecting to Supabase:")
        print(str(e))

if __name__ == "__main__":
    asyncio.run(test_supabase_connection()) 