from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime
import random
import smtplib
from email.message import EmailMessage

app = FastAPI(title="MetaboSync AI Fitness API", version="2.7")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_DATABASE = {}
WORKOUT_DATABASE = []

# --- CONFIG YOUR SMTP SENDER HERE ---
# To use real Gmail delivery, generate an App Password from your Google Account settings 
# and input your email & app password below:
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"          # Replace with your Gmail
SENDER_PASSWORD = "your_google_app_password"   # Replace with your 16-character Google App Password

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
    set_number: int
    weight_kg: float
    reps: int
    notes: Optional[str] = ""

class DetailedWorkoutCreate(BaseModel):
    email: EmailStr
    split_name: str
    exercise_name: str
    duration_minutes: int
    sets: List[SetItem]

def send_real_email_otp(recipient_email: str, otp_code: str):
    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nYour MetaboSync verification code is: {otp_code}\n\nEnter this code to complete your account setup.\n\nBest regards,\nMetaboSync Team")
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
    return {"message": "Welcome to MetaboSync Secure AI Fitness & Performance API"}

@app.post("/api/auth/signup")
def register_user(data: SignupRequest):
    if data.email in USER_DATABASE:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    # Generate 6-digit OTP code standard in production apps
    real_otp = str(random.randint(100000, 999999))
    
    USER_DATABASE[data.email] = {
        "full_name": data.full_name,
        "phone": data.phone,
        "password": None,
        "otp_code": real_otp,
        "is_verified": False
    }
    
    # Attempt to send real email
    email_sent = send_real_email_otp(data.email, real_otp)
    
    if not email_sent:
        # Fallback for dev mode if SMTP isn't configured yet
        return {
            "status": "success",
            "message": f"User registered, but SMTP failed. Dev OTP fallback: {real_otp}",
            "dev_otp": real_otp
        }
    
    return {
        "status": "success", 
        "message": f"Real verification code successfully sent to {data.email}!"
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