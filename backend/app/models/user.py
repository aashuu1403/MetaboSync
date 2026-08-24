from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # This is the magic link that connects a User to their dynamic workout sets!
    workouts = relationship("Workout", back_populates="owner")