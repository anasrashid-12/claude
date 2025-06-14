# backend/models.py
from sqlalchemy import Column, String, DateTime
from database import Base
import datetime

class ImageJob(Base):
    __tablename__ = "image_jobs"
    id = Column(String, primary_key=True)
    filename = Column(String)
    user_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)