from datetime import date
from pydantic import BaseModel

class DailySummaryResponse(BaseModel):
    date: date
    total_calories: int
    total_protein_g: float
    total_carbs_g: float
    total_fats_g: float
    total_exercises_completed: int
    total_sets_completed: int
