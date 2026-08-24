from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime
import random

app = FastAPI(title="MetaboSync AI Fitness API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Database Simulations
USER_DATABASE = {}       # {email: {name, phone, password, otp_code, is_verified}}
WORKOUT_DATABASE = []    # Stores workouts per user email

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SetItem(BaseModel):
    set_number: number = 1 # type: ignore
    weight_kg: float
    reps: int
    notes: Optional[str] = ""

class DetailedWorkoutCreate(BaseModel):
    email: EmailStr
    split_name: str
    exercise_name: str
    duration_minutes: int
    sets: List[SetItem]

@app.get("/")
def read_root():
    return {"message": "Welcome to MetaboSync Secure AI Fitness & Performance API"}

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/signup")
def register_user(data: SignupRequest):
    if data.email in USER_DATABASE:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    # Generate a 4-digit mock OTP (In production, integrate Twilio/SendGrid)
    mock_otp = str(random.randint(1000, 9999))
    
    USER_DATABASE[data.email] = {
        "full_name": data.full_name,
        "phone": data.phone,
        "password": None,
        "otp_code": mock_otp,
        "is_verified": False
    }
    
    return {
        "status": "success", 
        "message": f"OTP sent successfully to {data.email} and phone {data.phone}.",
        "debug_otp": mock_otp  # Shown for ease of testing in development
    }

@app.post("/api/auth/verify-otp")
def verify_otp_and_set_password(data: VerifyOTPRequest):
    user = USER_DATABASE.get(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if user["otp_code"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code entered.")
    
    user["password"] = data.password
    user["is_verified"] = True
    
    return {"status": "success", "message": "Account verified and password created successfully!"}

@app.post("/api/auth/login")
def login_user(data: LoginRequest):
    user = USER_DATABASE.get(data.email)
    if not user or not user["is_verified"]:
        raise HTTPException(status_code=400, detail="Account not found or not verified.")
    
    if user["password"] != data.password:
        raise HTTPException(status_code=400, detail="Incorrect password.")
        
    return {
        "status": "success",
        "message": "Login successful!",
        "user": {
            "full_name": user["full_name"],
            "email": data.email,
            "phone": user["phone"]
        }
    }

# --- WORKOUT & FITNESS ENDPOINTS ---

@app.post("/api/workouts/detailed")
def log_detailed_workout(workout: DetailedWorkoutCreate):
    session_data = {
        "email": workout.email,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "split_name": workout.split_name,
        "exercise_name": workout.exercise_name,
        "duration_minutes": workout.duration_minutes,
        "sets": [s.dict() for s in workout.sets]
    }
    WORKOUT_DATABASE.append(session_data)
    return {"status": "success", "message": f"Successfully logged {workout.exercise_name} session!"}

@app.get("/api/workouts/history/{email}/{exercise_name}")
def get_exercise_history(email: str, exercise_name: str):
    matching_sessions = [
        w for w in WORKOUT_DATABASE 
        if w["email"].lower() == email.lower() and w["exercise_name"].strip().lower() == exercise_name.strip().lower()
    ]
    
    max_weight = 0.0
    for session in matching_sessions:
        for s in session["sets"]:
            if s["weight_kg"] > max_weight:
                max_weight = s["weight_kg"]
                
    return {
        "exercise_name": exercise_name,
        "pr_weight": max_weight,
        "history": matching_sessions[::-1]
    }

@app.get("/api/analytics/{email}")
def get_analytics(email: str):
    user_workouts = [w for w in WORKOUT_DATABASE if w["email"].lower() == email.lower()]
    return {
        "total_workouts_logged": len(user_workouts),
        "streak_days": 5,
        "ai_recommendation": "Great consistency! Focus on progressive overload for your compound lifts this week."
    }

@app.post("/api/pose/analyze-squat")
def analyze_squat_form():
    return {
        "status": "success",
        "form_score": 92,
        "feedback": ["Good knee tracking", "Depth reached successfully", "Keep chest up slightly more on ascent"]
    }