from fastapi import APIRouter, HTTPException, Depends
from app.services.store import store_service
from app.models.store import Store, StoreUpdate
from app.core.exceptions import NotFoundError, ValidationError
from typing import List
from app.api.deps import get_current_store

router = APIRouter()

@router.get("/me", response_model=Store)
async def get_current_store(store: Store = Depends(get_current_store)):
    """
    Get current store information
    """
    return store

@router.get("/{store_id}", response_model=Store)
async def get_store(store_id: int):
    """
    Get store by ID
    """
    try:
        return await store_service.get(store_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/domain/{shop_domain}", response_model=Store)
async def get_store_by_domain(shop_domain: str):
    """
    Get store by domain
    """
    try:
        store = await store_service.get_by_domain(shop_domain)
        if not store:
            raise NotFoundError(f"Store {shop_domain} not found")
        return store
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/me", response_model=Store)
async def update_current_store(
    data: StoreUpdate,
    store: Store = Depends(get_current_store)
):
    """
    Update current store settings
    """
    try:
        return await store_service.update(store.id, data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[Store])
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None
):
    """
    List all stores with optional filtering
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    
    return await store_service.list(
        filters=filters,
        skip=skip,
        limit=limit
    ) 