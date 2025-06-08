import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

def run_migrations():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise Exception("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    
    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        # Get the absolute paths to migration files
        base_dir = Path(__file__).resolve().parent.parent.parent
        init_sql_path = base_dir / "supabase" / "init.sql"
        migration_sql_path = base_dir / "supabase" / "complete_migration.sql"
        
        # Read migration files
        with open(init_sql_path, "r") as f:
            init_sql = f.read()
        
        with open(migration_sql_path, "r") as f:
            migration_sql = f.read()
        
        # Execute migrations
        print("Running initialization SQL...")
        supabase.rpc("exec_sql", {"sql": init_sql}).execute()
        
        print("Running complete migration SQL...")
        supabase.rpc("exec_sql", {"sql": migration_sql}).execute()
        
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
        raise

if __name__ == "__main__":
    run_migrations() 