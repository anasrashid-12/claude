from typing import Optional
from supabase import create_client, Client
from app.core.config import settings
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create a Supabase client instance using the singleton pattern.
        """
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Successfully initialized Supabase client")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        return cls._instance

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager for getting a Supabase client connection.
        """
        client = cls.get_client()
        try:
            yield client
        except Exception as e:
            logger.error(f"Error during Supabase operation: {str(e)}")
            raise
        finally:
            # Connection cleanup if needed
            pass

# Initialize the client
supabase = SupabaseClient() 