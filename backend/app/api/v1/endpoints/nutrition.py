from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.nutrition import DailyMacroLog
from backend.app.schemas.nutrition import MacroCreate, MacroResponse

router = APIRouter()

@router.post("/", response_model=MacroResponse, status_code=status.HTTP_201_CREATED)
def create_macro_log(
    macro_in: MacroCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_macro = DailyMacroLog(**macro_in.model_dump(), user_id=current_user.id)
    db.add(db_macro)
    db.commit()
    db.refresh(db_macro)
    return db_macro

@router.get("/", response_model=List[MacroResponse])
def get_user_macros(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return current_user.daily_macro_logs
