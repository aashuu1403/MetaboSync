from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    split_name = Column(String, nullable=True)      # e.g., "Back & Biceps", "Leg Day"
    exercise_name = Column(String, nullable=True)    # e.g., "Conventional Deadlift"
    total_reps = Column(Integer)  
    form_accuracy = Column(Float)  
    duration_minutes = Column(Integer)
    joint_stress_score = Column(Float)
    
    # Relationship to hold multiple sets per workout log
    sets = relationship("WorkoutSet", back_populates="workout", cascade="all, delete-orphan")

class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workout_logs.id"), nullable=False)
    set_number = Column(Integer, nullable=False)     # Set 1, Set 2, etc.
    weight_kg = Column(Float, nullable=False)        # Weight used (e.g., 80.0, 100.0)
    reps = Column(Integer, nullable=False)           # Reps completed
    notes = Column(Text, nullable=True)              # e.g., "Warmup set", "Used a belt, felt heavy"

    workout = relationship("WorkoutLog", back_populates="sets")

class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_calories = Column(Integer)
    protein_grams = Column(Float)
    carbs_grams = Column(Float)
    fats_grams = Column(Float)
    dietary_preference = Column(String) # Example: "Vegetarian (No Eggs)"