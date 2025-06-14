# backend/schemas.py
from pydantic import BaseModel

class JobSchema(BaseModel):
    id: str
    filename: str
    user_id: str
    status: str