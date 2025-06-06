from supabase import create_client, Client
from app.core.config import settings
from app.core.exceptions import DatabaseError
from contextlib import contextmanager
from typing import Generator

class Database:
    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self._client = create_client(
                settings.DATABASE_URL,
                settings.SUPABASE_KEY
            )
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database connection: {str(e)}")

    @property
    def client(self) -> Client:
        if not self._client:
            self._initialize()
        return self._client

    @contextmanager
    def transaction(self) -> Generator[Client, None, None]:
        """
        Context manager for database transactions.
        Usage:
            with db.transaction() as tx:
                tx.table("users").insert({"name": "John"}).execute()
        """
        try:
            yield self.client
            # Note: Supabase-py doesn't support explicit transaction management yet
            # This is a placeholder for future implementation
        except Exception as e:
            raise DatabaseError(f"Transaction failed: {str(e)}")

# Create a global instance
db = Database() 