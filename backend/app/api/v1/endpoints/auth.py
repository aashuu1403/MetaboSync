from datetime import timedelta

from fastapi import APIRouter, Depends, status
from backend.app.core.exceptions import DataValidationError, InvalidCredentialsError, UserNotFoundError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, verify_password, get_password_hash
from backend.app.schemas.token import Token
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise DataValidationError(detail="The user with this username already exists in the system.")
    hashed_password = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise InvalidCredentialsError()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}