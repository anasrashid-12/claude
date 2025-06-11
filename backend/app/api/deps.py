"""API Dependencies Module"""

from fastapi import Depends, Request, HTTPException
from app.core.session import session_manager
from app.models.store import Store
from app.services.store import store_service
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def get_current_store(request: Request) -> Store:
    """Get current store from session."""
    try:
        # Get session
        session = await session_manager.get_current_session(request)
        
        # Get store
        store = await store_service.get_store(session['shop_domain'])
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        return store
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_webhook_session(
    request: Request,
    hmac_header: Optional[str] = None
) -> Dict:
    """Get session from webhook request."""
    try:
        return await session_manager.validate_webhook_session(request, hmac_header)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate webhook session: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 