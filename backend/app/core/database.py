from typing import Optional
from supabase import create_client, Client
from functools import lru_cache
from app.core.config import settings
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(settings.SUPABASE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@lru_cache()
def get_supabase_client() -> Optional[Client]:
    """Get a cached Supabase client instance"""
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase URL or key not configured")
            return None
        return create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

# Initialize Supabase client
db = get_supabase_client()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database connection"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

class Database:
    """Database utility class for common operations"""
    
    @staticmethod
    async def execute_query(table: str, query_fn, *args, **kwargs) -> Optional[dict]:
        """Execute a query using the provided query function"""
        try:
            result = query_fn(db.table(table), *args, **kwargs).execute()
            return result.data if result else None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    @staticmethod
    async def get_by_id(table: str, id: str) -> Optional[dict]:
        """Get a record by ID"""
        try:
            result = db.table(table).select('*').eq('id', id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get record by ID: {e}")
            raise

    @staticmethod
    async def create(table: str, data: dict) -> Optional[dict]:
        """Create a new record"""
        try:
            result = db.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create record: {e}")
            raise

    @staticmethod
    async def update(table: str, id: str, data: dict) -> Optional[dict]:
        """Update a record by ID"""
        try:
            result = db.table(table).update(data).eq('id', id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update record: {e}")
            raise

    @staticmethod
    async def delete(table: str, id: str) -> bool:
        """Delete a record by ID"""
        try:
            result = db.table(table).delete().eq('id', id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to delete record: {e}")
            raise 