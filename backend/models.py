from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    profile_picture = Column(String(500), nullable=True)  # URL to profile picture
    
    # Relationship to events
    events = relationship("Event", back_populates="owner")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    raw_text = Column(Text, nullable=True)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship to user
    owner = relationship("User", back_populates="events")