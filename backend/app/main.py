from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime

app = FastAPI(title="MetaboSync AI Fitness API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Database Simulation (or connect to SQLite/PostgreSQL)
WORKOUT_DATABASE = []

class SetItem(BaseModel):
    set_number: int
    weight_kg: float
    reps: int
    notes: Optional[str] = ""

class DetailedWorkoutCreate(BaseModel):
    split_name: str
    exercise_name: str
    duration_minutes: int
    sets: List[SetItem]

@get_route = app.get("/")
def read_root():
    return {"message": "Welcome to MetaboSync AI Fitness & Performance API"}

@app.post("/api/workouts/detailed")
def log_detailed_workout(workout: DetailedWorkoutCreate):
    session_data = {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "split_name": workout.split_name,
        "exercise_name": workout.exercise_name,
        "duration_minutes": workout.duration_minutes,
        "sets": [s.dict() for s in workout.sets]
    }
    WORKOUT_DATABASE.append(session_data)
    return {"status": "success", "message": f"Successfully logged {workout.exercise_name} session!"}

@app.get("/api/workouts/history/{exercise_name}")
def get_exercise_history(exercise_name: str):
    # Filter sessions matching the exercise name (case-insensitive)
    matching_sessions = [
        w for w in WORKOUT_DATABASE 
        if w["exercise_name"].strip().lower() == exercise_name.strip().lower()
    ]
    
    # Calculate PR (Maximum weight lifted across all sets and sessions for this exercise)
    max_weight = 0.0
    for session in matching_sessions:
        for s in session["sets"]:
            if s["weight_kg"] > max_weight:
                max_weight = s["weight_kg"]
                
    return {
        "exercise_name": exercise_name,
        "pr_weight": max_weight,
        "history": matching_sessions[::-1]  # Most recent first
    }

@app.get("/api/analytics")
def get_analytics():
    total_workouts = len(WORKOUT_DATABASE)
    return {
        "total_workouts_logged": total_workouts,
        "streak_days": 5,
        "ai_recommendation": "Great consistency! Focus on progressive overload for your compound lifts this week."
    }

# Computer Vision Squat Form Analysis Mock/Endpoint integration placeholder
@app.post("/api/pose/analyze-squat")
def analyze_squat_form():
    # Integrates with your MediaPipe pose analyzer module
    return {
        "status": "success",
        "form_score": 92,
        "feedback": ["Good knee tracking", "Depth reached successfully", "Keep chest up slightly more on ascent"]
    }