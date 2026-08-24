from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.schema import WorkoutLog, WorkoutSet, NutritionLog, Base
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- FORCES FASTAPI TO BUILD THE NEW TABLES ---
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
# ----------------------------------------------

app = FastAPI(title="MetaboSync Analytics API")

# --- ADD THIS BLOCK TO ALLOW FRONTEND CONNECTION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------------------

# --- PYDANTIC MODELS FOR N8N AND DETAILED LOGGING ---
class IncomingWorkout(BaseModel):
    total_reps: int
    average_form_score: float

class WorkoutSetItem(BaseModel):
    set_number: int
    weight_kg: float
    reps: int
    notes: Optional[str] = None

class DetailedWorkoutCreate(BaseModel):
    split_name: str         # e.g., "Back & Biceps", "Legs"
    exercise_name: str      # e.g., "Conventional Deadlift"
    duration_minutes: Optional[int] = None
    sets: List[WorkoutSetItem]
# ---------------------------------------------------

@app.get("/")
def root():
    return {"status": "MetaboSync AI Backend is live!"}

# --- ENDPOINT TO RECEIVE DATA FROM N8N ---
@app.post("/api/workouts")
def save_workout(data: IncomingWorkout, db: Session = Depends(get_db)):
    new_workout = WorkoutLog(
        date=date.today(),
        exercise_type="Squat",
        total_reps=data.total_reps,
        form_accuracy=data.average_form_score
    )
    db.add(new_workout)
    db.commit()
    
    return {"status": "success", "message": "Workout successfully logged in database!"}
# ----------------------------------------------

# --- NEW: ENDPOINT FOR DETAILED USER WORKOUT LOGGING ---
@app.post("/api/workouts/detailed")
def save_detailed_workout(data: DetailedWorkoutCreate, db: Session = Depends(get_db)):
    calculated_total_reps = sum(s.reps for s in data.sets)
    
    new_workout = WorkoutLog(
        date=date.today(),
        split_name=data.split_name,
        exercise_name=data.exercise_name,
        total_reps=calculated_total_reps,
        duration_minutes=data.duration_minutes,
        form_accuracy=95.0  # Default baseline score for manual logs
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    for set_item in data.sets:
        new_set = WorkoutSet(
            workout_id=new_workout.id,
            set_number=set_item.set_number,
            weight_kg=set_item.weight_kg,
            reps=set_item.reps,
            notes=set_item.notes
        )
        db.add(new_set)
    
    db.commit()
    
    return {
        "status": "success", 
        "message": f"Successfully logged {data.exercise_name} with {len(data.sets)} sets!"
    }
# -------------------------------------------------------

@app.get("/api/analytics")
def get_analytics_data(db: Session = Depends(get_db)):
    workouts = db.query(WorkoutLog).order_by(WorkoutLog.date).all()
    nutrition = db.query(NutritionLog).order_by(NutritionLog.date).all()

    # Safely convert to DataFrames and drop state column if it exists
    df_workouts = pd.DataFrame([w.__dict__ for w in workouts])
    if not df_workouts.empty and '_sa_instance_state' in df_workouts.columns:
        df_workouts = df_workouts.drop(columns=['_sa_instance_state'])

    df_nutrition = pd.DataFrame([n.__dict__ for n in nutrition])
    if not df_nutrition.empty and '_sa_instance_state' in df_nutrition.columns:
        df_nutrition = df_nutrition.drop(columns=['_sa_instance_state'])

    insights = []
    recommendations = []

    if not df_workouts.empty and not df_nutrition.empty:
        df_merged = pd.merge(df_workouts, df_nutrition, on='date', how='inner')
        poor_performance = df_merged[df_merged['form_accuracy'] < 90.0]
        
        if not poor_performance.empty:
            avg_protein_low_days = poor_performance['protein_grams'].mean()
            if avg_protein_low_days < 60:
                insights.append("Detected a correlation between form degradation and sub-60g protein intake.")
                recommendations.append("Increase protein intake on heavy lifting days. Suggested sources: Whey protein isolate, lentils, or paneer. (Strictly no eggs).")

    return {
        "raw_data": {
            "workouts": df_workouts.to_dict(orient="records") if not df_workouts.empty else [],
            "nutrition": df_nutrition.to_dict(orient="records") if not df_nutrition.empty else []
        },
        "analytics": {
            "insights": insights,
            "dietary_recommendations": recommendations
        }
    }

@app.get("/api/workouts/history/{exercise_name}")
def get_exercise_history(exercise_name: str, db: Session = Depends(get_db)):
    # Find all past workout logs for this specific exercise, ordered by date descending
    past_workouts = db.query(WorkoutLog).filter(
        WorkoutLog.exercise_name == exercise_name
    ).order_by(WorkoutLog.date.desc()).all()

    if not past_workouts:
        return {"history": [], "pr_weight": 0}

    history_data = []
    all_weights = []

    for workout in past_workouts:
        sets_data = []
        for s in workout.sets:
            sets_data.append({
                "set_number": s.set_number,
                "weight_kg": s.weight_kg,
                "reps": s.reps,
                "notes": s.notes
            })
            all_weights.append(s.weight_kg)
        
        history_data.append({
            "date": str(workout.date),
            "split_name": workout.split_name,
            "sets": sets_data
        })

    # Calculate Personal Record (Max weight lifted for this exercise)
    pr_weight = max(all_weights) if all_weights else 0.0

    return {
        "history": history_data,
        "pr_weight": pr_weight
    }