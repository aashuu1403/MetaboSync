from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.workout import Workout
from backend.app.schemas.workout import WorkoutCreate, WorkoutResponse
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("/", response_model=WorkoutResponse)
def log_workout(
    workout_in: WorkoutCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_workout = Workout(
        exercise_name=workout_in.exercise_name,
        sets_data=[set_item.model_dump() for set_item in workout_in.sets_data],
        user_id=current_user.id
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/", response_model=List[WorkoutResponse])
def get_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()
    return workouts