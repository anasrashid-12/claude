from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis, ConnectionPool
from supabase import create_client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
import zlib
import base64

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Shopify AI Image App")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis connection pool
redis_pool = ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10,
    decode_responses=True
)

# Initialize Redis with connection pool
redis_client = Redis(connection_pool=redis_pool)

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions for Redis compression
def compress_data(data: dict) -> str:
    json_str = json.dumps(data)
    compressed = zlib.compress(json_str.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def decompress_data(data: str) -> dict:
    try:
        compressed = base64.b64decode(data.encode('utf-8'))
        decompressed = zlib.decompress(compressed)
        return json.loads(decompressed.decode('utf-8'))
    except Exception as e:
        # If decompression fails, try parsing as regular JSON
        return json.loads(data)

# Dependency to get Redis client
async def get_redis():
    try:
        yield redis_client
    finally:
        # Connection is managed by the connection pool
        pass

# Pydantic models
class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    shopify_product_id: Optional[str] = None
    title: Optional[str] = None
    store_id: Optional[str] = None

# Routes
@app.get("/")
async def root():
    return {"message": "Shopify AI Image App API"}

@app.post("/products/")
async def create_product(
    product: Product,
    redis: Redis = Depends(get_redis)
):
    try:
        # Store in Supabase
        response = supabase.table("products").insert({
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "shopify_product_id": product.shopify_product_id,
            "title": product.title or product.name,  # Use name as title if not provided
            "store_id": product.store_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        
        product_data = response.data[0]
        
        # Cache in Redis with compression (expire after 1 hour)
        compressed_data = compress_data(product_data)
        redis.setex(
            f"product:{product_data['id']}", 
            3600,  # 1 hour in seconds
            compressed_data
        )
        
        return product_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    redis: Redis = Depends(get_redis)
):
    try:
        # Try to get from Redis first
        cached_product = redis.get(f"product:{product_id}")
        if cached_product:
            try:
                return decompress_data(cached_product)
            except Exception as e:
                # Log the error but continue to fetch from Supabase
                print(f"Redis decompression error: {str(e)}")
        
        # If not in Redis or decompression failed, get from Supabase
        response = supabase.table("products").select("*").eq("id", product_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = response.data[0]
        
        # Cache in Redis with compression
        compressed_data = compress_data(product_data)
        redis.setex(
            f"product:{product_id}", 
            3600,  # 1 hour in seconds
            compressed_data
        )
        
        return product_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check(redis: Redis = Depends(get_redis)):
    try:
        # Check Redis connection
        redis.ping()
        
        # Check Supabase connection
        supabase.table("products").select("count", count="exact").execute()
        
        return {
            "status": "healthy",
            "redis": "connected",
            "supabase": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service unhealthy: {str(e)}"
        )

