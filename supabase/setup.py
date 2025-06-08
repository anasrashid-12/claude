import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

def run_command(command):
    """Run a command and print its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        return False

def setup_supabase():
    """Set up Supabase project and run migrations."""
    # Check if Supabase CLI is installed
    if not run_command("supabase --version"):
        print("Supabase CLI not found. Please install it first:")
        print("npm install -g supabase")
        return False

    # Initialize Supabase project if not already initialized
    if not Path("supabase/config.toml").exists():
        print("Initializing Supabase project...")
        if not run_command("supabase init"):
            return False

    # Start Supabase locally
    print("Starting Supabase locally...")
    if not run_command("supabase start"):
        return False

    # Run the initialization SQL
    print("Running initialization SQL...")
    if not run_command("supabase db reset"):
        return False

    print("\nSupabase project setup completed successfully!")
    print("\nNext steps:")
    print("1. Create a .env file in the backend directory with your Supabase credentials")
    print("2. Create a .env.local file in the frontend directory with your Supabase credentials")
    print("3. Update your Supabase project settings in the dashboard")
    
    # Get local development credentials
    print("\nYour local development credentials:")
    run_command("supabase status")
    
    return True

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
        result = supabase.rpc("exec_sql", {"sql": init_sql}).execute()
        print(f"Initialization result: {result}")
        
        print("\nRunning complete migration SQL...")
        result = supabase.rpc("exec_sql", {"sql": migration_sql}).execute()
        print(f"Migration result: {result}")
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_supabase()
    setup_database() 