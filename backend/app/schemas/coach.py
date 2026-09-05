from pydantic import BaseModel

class CoachRequest(BaseModel):
    email: str
    query: str  # e.g., "How should I program my progressive overload for deadlifts this week?"