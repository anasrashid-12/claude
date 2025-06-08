from supabase import create_client, Client
from app.core.config import settings
from app.core.exceptions import DatabaseError
from contextlib import contextmanager
from typing import Generator, AsyncGenerator
import httpx
from supabase.client import ClientOptions
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLAlchemy models base class
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

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
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public"
            )
            
            self._client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY,
                options=options
            )
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database connection: {str(e)}")

    @property
    def client(self) -> Client:
        if not self._client:
            self._initialize()
        return self._client

    def get_client(self) -> Client:
        return self.client

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