from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise Exception("Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
