from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def apply_migration():
    try:
        # SQL to add new columns and modify existing ones
        migration_sql = """
        -- Add new columns to products table
        ALTER TABLE products
        ADD COLUMN IF NOT EXISTS name VARCHAR(255),
        ADD COLUMN IF NOT EXISTS price DECIMAL(10,2),
        ADD COLUMN IF NOT EXISTS description TEXT;

        -- Update existing columns to be nullable
        ALTER TABLE products
        ALTER COLUMN shopify_product_id DROP NOT NULL,
        ALTER COLUMN title DROP NOT NULL;
        """

        # Execute the migration
        supabase.table("products").select("*").execute()  # This is just to test the connection
        print("Connected to Supabase successfully")

        # Note: We can't execute raw SQL directly with supabase-py
        # You'll need to run this migration through the Supabase dashboard SQL editor
        print("\nPlease run the following SQL in your Supabase dashboard SQL editor:")
        print("\n" + migration_sql)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    apply_migration() 