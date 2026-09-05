from pydantic import BaseModel
from typing import List, Optional

class SetDetail(BaseModel):
    set_number: int
    reps: int
    weight_kg: float

class WorkoutCreate(BaseModel):
    exercise_name: str
    sets_data: List[SetDetail]

class WorkoutResponse(BaseModel):
    id: int
    exercise_name: str
    sets_data: List[SetDetail]
    
    class Config:
        from_attributes = True

class WorkoutSetCreate(BaseModel):
    set_number: int
    weight_kg: float
    reps: int
    notes: Optional[str] = ""

class DetailedWorkoutCreate(BaseModel):
    email: str
    split_name: str
    exercise_name: str
    duration_minutes: int
    sets: List[WorkoutSetCreate]