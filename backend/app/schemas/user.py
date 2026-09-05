from pydantic import BaseModel
from typing import List, Optional

class SignupRequest(BaseModel):
    full_name: str
    email: str
    phone: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str
    password: str

class LoginRequest(BaseModel):
    identifier: str
    password: str

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

class CoachRequest(BaseModel):
    email: str
    query: str