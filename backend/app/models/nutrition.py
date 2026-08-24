from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class DailyMacroLog(Base):
    __tablename__ = "daily_macro_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_name = Column(String, index=True)
    calories = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fats_g = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", backref="daily_macro_logs")
