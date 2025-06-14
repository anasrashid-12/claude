from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth_router
from routes.upload import upload_router
from routes.shopify import shopify_router

app = FastAPI()

# CORS middleware only once
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(shopify_router)

@app.get("/")
def root():
    return {"message": "Maxflow AI Backend is running"}
