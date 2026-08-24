from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_name = Column(String, index=True)
    sets_data = Column(JSON) 

    owner = relationship("User", back_populates="workouts")