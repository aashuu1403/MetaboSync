from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import datetime
import random
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

from .core.database import engine, get_db, Base
from .schemas.user import SignupRequest, VerifyOTPRequest, LoginRequest, CoachRequest
from .schemas.workout import DetailedWorkoutCreate
from .core.security import hash_password, verify_password
from .models import user, workout

import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# --- AI COACH CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    coach_model = genai.GenerativeModel('gemini-3.6-flash')
else:
    coach_model = None
    print("WARNING: GEMINI_API_KEY not found in .env file.")

# Creates tables on startup if they don't already exist (SQLite file:
# metabosync.db, created next to this file). Safe to call every run.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MetaboSync AI Fitness API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GMAIL SMTP CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "aashna.lalka14@gmail.com"          # Your Gmail address
SENDER_PASSWORD = "YOUR_16_CHARACTER_APP_PASSWORD"  # Your Google App Password


def send_real_email_otp(recipient_email: str, otp_code: str) -> bool:
    """Dispatches a real verification OTP email via Gmail SMTP"""
    if SENDER_PASSWORD == "YOUR_16_CHARACTER_APP_PASSWORD" or not SENDER_PASSWORD:
        print(f"\n[DEV FALLBACK] Gmail App Password not set. Code for {recipient_email}: {otp_code}\n")
        return False

    msg = EmailMessage()
    msg.set_content(
        f"Hello from MetaboSync,\n\nYour account verification code is: {otp_code}\n\n"
        f"Enter this code on the verification screen to complete your profile setup "
        f"and link your phone number.\n\nBest regards,\nMetaboSync Security Team"
    )
    msg["Subject"] = "Your MetaboSync Verification Code"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Email Error: {e}")
        return False


@app.get("/")
def read_root():
    return {"message": "Welcome to MetaboSync Secure Gmail Auth & Fitness API"}


@app.post("/api/auth/signup")
def register_user(data: SignupRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(user.User)
        .filter((user.User.email == data.email) | (user.User.phone == data.phone))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this email or phone number already exists.",
        )

    real_otp = str(random.randint(100000, 999999))

    new_user = user.User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        hashed_password="",
        otp_code=real_otp,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()

    email_sent = send_real_email_otp(data.email, real_otp)

    return {
        "status": "success",
        "message": (
            f"Verification code successfully sent to {data.email}!"
            if email_sent
            else "Registered, but SMTP needs an App Password. Check backend terminal for code."
        ),
        "dev_fallback_otp": real_otp if not email_sent else None,
    }


@app.post("/api/auth/verify-otp")
def verify_otp_and_set_password(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User profile not found.")

    if db_user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP verification code entered.")

    db_user.hashed_password = hash_password(data.password)
    db_user.is_verified = True
    db.commit()

    return {"status": "success", "message": "Account verified, password secured, and profile successfully linked!"}


@app.post("/api/auth/login")
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    identifier = data.identifier.strip()

    if "@" in identifier:
        db_user = db.query(user.User).filter(user.User.email == identifier).first()
    else:
        db_user = db.query(user.User).filter(user.User.phone == identifier).first()

    if not db_user or not db_user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="No verified account found matching this email or phone number.",
        )

    if not db_user.hashed_password or not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password.")

    return {
        "status": "success",
        "message": "Login successful!",
        "user": {
            "full_name": db_user.full_name,
            "email": db_user.email,
            "phone": db_user.phone,
        },
    }


@app.post("/api/workouts/detailed")
def log_detailed_workout(workout_data: DetailedWorkoutCreate, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == workout_data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User profile not found.")

    db_workout = workout.Workout(
        user_id=db_user.id,
        split_name=workout_data.split_name,
        exercise_name=workout_data.exercise_name,
        duration_minutes=workout_data.duration_minutes,
        date=datetime.date.today(),
    )
    db.add(db_workout)
    db.flush()  # get db_workout.id before inserting sets

    for s in workout_data.sets:
        db.add(
            workout.WorkoutSet(
                workout_id=db_workout.id,
                set_number=s.set_number,
                weight_kg=s.weight_kg,
                reps=s.reps,
                notes=s.notes or "",
            )
        )

    db.commit()
    return {"status": "success", "message": f"Successfully logged {workout_data.exercise_name} session!"}


@app.get("/api/workouts/history/{email}/{exercise_name}")
def get_exercise_history(email: str, exercise_name: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(func.lower(user.User.email) == email.lower()).first()
    if not db_user:
        return {"exercise_name": exercise_name, "pr_weight": 0.0, "history": []}

    matching_workouts = (
        db.query(workout.Workout)
        .filter(
            workout.Workout.user_id == db_user.id,
            func.lower(workout.Workout.exercise_name) == exercise_name.strip().lower(),
        )
        .order_by(workout.Workout.date.desc(), workout.Workout.id.desc())
        .all()
    )

    max_weight = 0.0
    history = []
    for w in matching_workouts:
        sets = [
            {
                "set_number": s.set_number,
                "weight_kg": s.weight_kg,
                "reps": s.reps,
                "notes": s.notes,
            }
            for s in w.sets
        ]
        for s in sets:
            if s["weight_kg"] > max_weight:
                max_weight = s["weight_kg"]

        history.append(
            {
                "email": db_user.email,
                "date": w.date.strftime("%Y-%m-%d"),
                "split_name": w.split_name,
                "exercise_name": w.exercise_name,
                "duration_minutes": w.duration_minutes,
                "sets": sets,
            }
        )

    return {
        "exercise_name": exercise_name,
        "pr_weight": max_weight,
        "history": history,
    }


@app.get("/api/analytics/{email}")
def get_analytics(email: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(func.lower(user.User.email) == email.lower()).first()
    if not db_user:
        return {"total_workouts_logged": 0, "streak_days": 0, "ai_recommendation": "Log your first workout to get started!"}

    total = db.query(workout.Workout).filter(workout.Workout.user_id == db_user.id).count()

    return {
        "total_workouts_logged": total,
        "streak_days": 5,
        "ai_recommendation": "Great consistency! Focus on progressive overload for your compound lifts this week.",
    }


@app.post("/api/pose/analyze-squat")
def analyze_squat_form():
    return {
        "status": "success",
        "form_score": 92,
        "feedback": ["Good knee tracking", "Depth reached successfully", "Keep chest up slightly more on ascent"],
    }


@app.post("/api/coach/advice")
def get_ai_coach_advice(data: CoachRequest, db: Session = Depends(get_db)):
    # 1. Verify user exists
    db_user = db.query(user.User).filter(user.User.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User profile not found.")

    # 2. Retrieve all user workouts and sets (Retrieval step)
    user_workouts = db.query(workout.Workout).filter(workout.Workout.user_id == db_user.id).all()
    
    workout_summary = []
    max_weights = {}
    for w in user_workouts:
        exercise = w.exercise_name
        for s in w.sets:
            if exercise not in max_weights or s.weight_kg > max_weights[exercise]:
                max_weights[exercise] = s.weight_kg
        workout_summary.append(f"- Date: {w.date}, Split: {w.split_name}, Exercise: {w.exercise_name}")

    context_text = "\n".join(workout_summary) if workout_summary else "No workouts logged yet."
    pr_text = ", ".join([f"{ex}: {wt}kg" for ex, wt in max_weights.items()]) or "None"

    # 3. Construct the RAG prompt payload
    system_prompt = (
        "You are MetaboSync AI, an expert fitness and strength coach. "
        "Analyze the user's actual workout logs and personal records provided below "
        "to give tailored, actionable advice on progressive overload, recovery, and volume adjustments.\n\n"
        f"User Name: {db_user.full_name}\n"
        f"Personal Records (PRs): {pr_text}\n"
        f"Workout History Log:\n{context_text}"
    )

    # 4. Generate the AI Response
    if not coach_model:
        return {
            "status": "error",
            "message": "AI Coach is currently sleeping. Please add a valid GEMINI_API_KEY in main.py!"
        }

    try:
        # Combine the system context with the user's specific question
        full_prompt = f"{system_prompt}\n\nUser Question: {data.query}\n\nCoach Response:"
        
        response = coach_model.generate_content(full_prompt)
        ai_advice = response.text
        
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        raise HTTPException(status_code=500, detail="The AI Coach encountered an error generating your advice.")

    return {
        "status": "success",
        "user_query": data.query,
        "advice": ai_advice,
        "context_used": {
            "total_sessions_analyzed": len(user_workouts),
            "prs_found": max_weights
        }
    }