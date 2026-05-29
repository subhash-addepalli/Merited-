from sqlalchemy import Column, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ProfileCache(Base):
    __tablename__ = "profile_cache"

    username = Column(String(100), primary_key=True, index=True)
    tech_focus = Column(String(200))
    consistency_score = Column(Float)
    project_complexity = Column(Float)
    top_project = Column(JSON)
    recommendation = Column(Text)
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
