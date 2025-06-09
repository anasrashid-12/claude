from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session
from supabase import create_client, Client
from functools import lru_cache

from app.core.config import settings

# Sync engine for Celery tasks
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

def get_db() -> Session:
    """Sync database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncSession:
    """Async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@lru_cache()
def get_supabase_client() -> Client:
    """Get a cached Supabase client instance."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    ) 