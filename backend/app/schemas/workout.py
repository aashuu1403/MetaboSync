from pydantic import BaseModel
from typing import List

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