import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000/api/v1"

def register_user(email, password):
    url = f"{BASE_URL}/register"
    response = requests.post(url, json={"email": email, "password": password})
    if not response.ok:
        return {"error": response.text}
    return response.json()

def login_user(email, password):
    url = f"{BASE_URL}/login"
    payload = {"username": email, "password": password}
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            try:
                error_detail = response.json().get("detail", "Login failed.")
            except:
                error_detail = response.text
            return {"error": error_detail}
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to backend. Is the FastAPI server running?"}

def get_auth_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}

def log_workout(exercise_name, sets_data):
    url = f"{BASE_URL}/workouts/"
    payload = {
        "exercise_name": exercise_name,
        "sets_data": sets_data
    }
    response = requests.post(url, json=payload, headers=get_auth_headers())
    if not response.ok:
        return {"error": response.text}
    return response.json()

def get_workouts():
    url = f"{BASE_URL}/workouts/"
    response = requests.get(url, headers=get_auth_headers())
    if response.ok:
        return response.json()
    return []