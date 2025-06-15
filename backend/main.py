# backend/main.py
import uvicorn
from app import create_app
from logging_config import logger
app = create_app()

if __name__ == "__main__":
    logger.info("Starting backend server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    logger.info("Backend server stopped")
