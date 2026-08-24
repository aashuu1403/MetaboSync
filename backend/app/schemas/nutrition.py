from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MacroBase(BaseModel):
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fats_g: float

class MacroCreate(MacroBase):
    pass

class MacroResponse(MacroBase):
    id: int
    user_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
