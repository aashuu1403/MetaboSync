from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from backend.app.core.exceptions import UserNotFoundError, DataValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.nutrition import DailyMacroLog
from backend.app.models.workout import Workout
from backend.app.schemas.dashboard import DailySummaryResponse

router = APIRouter()

@router.get("/summary", response_model=DailySummaryResponse)
def get_daily_summary(
    target_date: Optional[date] = Query(default_factory=date.today),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Nutrition Summary
    macro_logs = (
        db.query(DailyMacroLog)
        .filter(
            DailyMacroLog.user_id == current_user.id,
            func.DATE(DailyMacroLog.date) == target_date,
        )
        .all()
    )

    total_calories = sum([log.calories for log in macro_logs])
    total_protein_g = sum([log.protein_g for log in macro_logs])
    total_carbs_g = sum([log.carbs_g for log in macro_logs])
    total_fats_g = sum([log.fats_g for log in macro_logs])

    # Workout Summary
    workout_logs = (
        db.query(Workout)
        .filter(
            Workout.user_id == current_user.id,
            func.DATE(Workout.date) == target_date,
        )
        .all()
    )

    total_exercises_completed = db.query(func.count(distinct(Workout.exercise_name)))
    total_exercises_completed = total_exercises_completed.filter(
        Workout.user_id == current_user.id,
        func.DATE(Workout.date) == target_date
    ).scalar()

    total_sets_completed = sum([log.sets for log in workout_logs])

    if not current_user:
        raise UserNotFoundError()

    if not macro_logs and not workout_logs:
        raise DataValidationError(detail="No data found for the target date.")

    return DailySummaryResponse(
        date=target_date,
        total_calories=total_calories,
        total_protein_g=total_protein_g,
        total_carbs_g=total_carbs_g,
        total_fats_g=total_fats_g,
        total_exercises_completed=total_exercises_completed if total_exercises_completed is not None else 0,
        total_sets_completed=total_sets_completed,
    )
