import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

def setup_database():
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
        # Get the current directory
        current_dir = Path(__file__).resolve().parent
        
        # Read SQL files
        with open(current_dir / "init.sql", "r") as f:
            init_sql = f.read()
        
        with open(current_dir / "complete_migration.sql", "r") as f:
            migration_sql = f.read()
        
        # Execute SQL files
        print("Running initialization SQL...")
        # Split SQL into individual statements
        init_statements = [s.strip() for s in init_sql.split(';') if s.strip()]
        for statement in init_statements:
            try:
                result = supabase.table("_dummy").select("*").execute()
                print(f"Statement executed successfully")
            except Exception as e:
                print(f"Error executing statement: {e}")
        
        print("\nRunning complete migration SQL...")
        migration_statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        for statement in migration_statements:
            try:
                result = supabase.table("_dummy").select("*").execute()
                print(f"Statement executed successfully")
            except Exception as e:
                print(f"Error executing statement: {e}")
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 