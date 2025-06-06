import os
from dotenv import load_dotenv
from supabase import create_client
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_migrations():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables")
    
    # Initialize Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    # Get all migration files
    migration_files = sorted(glob.glob("migrations/*.sql"))
    
    if not migration_files:
        logger.warning("No migration files found")
        return
    
    # Apply each migration
    for migration_file in migration_files:
        try:
            logger.info(f"Applying migration: {migration_file}")
            
            # Read migration file
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute migration
            result = supabase.rpc('exec_sql', {'query': sql}).execute()
            
            logger.info(f"Successfully applied migration: {migration_file}")
            
        except Exception as e:
            logger.error(f"Error applying migration {migration_file}: {str(e)}")
            raise

if __name__ == "__main__":
    apply_migrations() 