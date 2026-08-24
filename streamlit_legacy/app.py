import streamlit as st
import pandas as pd
from utils.api_client import register_user, login_user, log_workout, get_workouts
from utils.pose_analyzer import analyze_pose
from PIL import Image
import numpy as np
import altair as alt

st.set_page_config(page_title="MetaboSync Pro", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for MetaboSync Pro Theme
st.markdown("""
<style>
    @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap\');

    :root {
        --primary-color: #4A90E2; /* Deep Blue */
        --secondary-color: #5C6F8D; /* Slate Gray */
        --background-color: #F0F2F6; /* Clean White/Light Gray */
        --card-background: #FFFFFF;
        --text-color: #2F3C4C;
        --header-font: \'Montserrat\', sans-serif;
        --body-font: \'Roboto\', sans-serif;
    }

    body {
        font-family: var(--body-font);
        color: var(--text-color);
        background-color: var(--background-color);
    }

    /* Main container and sidebar styling */
    .stApp {
        background-color: var(--background-color);
    }

    .css-1d391kg, .css-1dp5vir {
        background-color: var(--card-background);
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .sidebar .sidebar-content {
        background-color: var(--secondary-color);
        color: white;
        padding: 20px;
    }
    .sidebar .sidebar-content .block-container {
        color: white; /* Ensure text in sidebar is white */
    }
    .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6 {
        color: white;
        font-family: var(--header-font);
    }
    .sidebar .stButton>button {
        color: var(--text-color);
        background-color: #F0F2F6;
        border: none;
        border-radius: 0.3rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    /* Headers and Titles */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--header-font);
        color: var(--primary-color);
        font-weight: 700;
    }
    .st-emotion-cache-10trblm.e1nzilvr1 {
        font-family: var(--header-font);
        color: var(--primary-color);
        font-weight: 700;
    }
    

    /* Cards */
    .st-emotion-cache-nahz7x.e1g8pov61 {
        background-color: var(--card-background);
        border-radius: 0.75rem;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .st-emotion-cache-nahz7x.e1g8pov61:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #3A7ACC; /* Darker shade of primary */
        color: white;
    }
    
    /* Metrics */
    .st-emotion-cache-jd4z4r.e1nzilvr5 {
        background-color: #E6F3FF; /* Light blue for metrics */
        border-left: 5px solid var(--primary-color);
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-family: var(--header-font);
    }
    .st-emotion-cache-jd4z4r.e1nzilvr5 label {
        color: var(--primary-color);
        font-weight: 600;
    }
    .st-emotion-cache-jd4z4r.e1nzilvr5 div[data-testid="stMetricValue"] {
        color: var(--text-color);
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Expander */
    .st-emotion-cache-nahz7x.e1g8pov61 .streamlit-expanderContent {
        background-color: #F8F9FA; /* Slightly different background for expander content */
        border-left: 3px solid #E0E0E0;
        padding-left: 1rem;
        margin-left: 0.5rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        color: var(--secondary-color);
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
        color: var(--primary-color);
    }

    /* Text Inputs */
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
        border: 1px solid #D0D4DB;
        padding: 0.6rem 1rem;
    }
    .stTextInput>label {
        font-weight: 600;
        color: var(--secondary-color);
    }

    /* File Uploader */
    .stFileUploader>div>button {
        background-color: var(--secondary-color);
        color: white;
        border-radius: 0.5rem;
    }

    /* Custom icons for headers */
    .icon-header {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--primary-color);
    }
    .icon-header h2 {
        margin: 0;
        color: var(--primary-color);
    }

    .card-container {
        background-color: var(--card-background);
        border-radius: 0.75rem;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    .user-profile-card {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 1rem;
        background-color: #E6F3FF;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--primary-color);
    }
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .user-info strong {
        color: var(--primary-color);
    }
    .logout-button-container {
        margin-top: 1rem;
        text-align: center;
    }
    .logout-button-container .stButton>button {
        width: 100%;
        background-color: #F44336; /* Red for logout */
    }
    .logout-button-container .stButton>button:hover {
        background-color: #D32F2F;
    }
</style>
""", unsafe_allow_html=True)

def custom_header(icon, text, level=2):
    st.markdown(f"""
    <div class="icon-header">
        <h{level}>{icon} {text}</h{level}>
    </div>
    """, unsafe_allow_html=True)

def main():
    if "token" not in st.session_state:
        st.session_state["token"] = None
    
    # --- Login/Registration Section --- 
    if st.session_state["token"] is None:
        st.markdown("<h1 style=\"text-align: center; color: var(--primary-color); font-family: var(--header-font);\">Welcome to MetaboSync Pro 🚀</h1>", unsafe_allow_html=True)
        st.markdown("<p style=\"text-align: center; color: var(--secondary-color); font-size: 1.1rem;\">Your ultimate fitness companion. Login or Register to get started!</p>", unsafe_allow_html=True)

        login_col, register_col = st.columns(2)

        with login_col:
            with st.container():
                st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
                custom_header("🔑", "Login", level=3)
                email = st.text_input("Email", key="login_email_pro")
                password = st.text_input("Password", type="password", key="login_password_pro")
                if st.button("Login to MetaboSync Pro", use_container_width=True):
                    res = login_user(email, password)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state["token"] = res.get("access_token")
                        st.success("Logged in successfully!")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                    
        with register_col:
            with st.container():
                st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
                custom_header("📝", "Register", level=3)
                reg_email = st.text_input("Email", key="reg_email_pro")
                reg_password = st.text_input("Password", type="password", key="reg_password_pro")
                if st.button("Join MetaboSync Pro", use_container_width=True):
                    res = register_user(reg_email, reg_password)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success("Registration successful! Please login.")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- Main App Section ---               
    else:
        st.sidebar.markdown("""
            <div style="text-align: center; padding-bottom: 20px;">
                <h1 style="color: white; font-family: var(--header-font);">MetaboSync Pro</h1>
                <p style="color: #A9B7C6; font-size: 0.9rem;">Your Premium Fitness Dashboard</p>
            </div>
            """, unsafe_allow_html=True)

        # User Info and Logout in Sidebar
        with st.sidebar:
            st.markdown("""
                <div class="user-profile-card">
                    <div class="user-avatar">👤</div>
                    <div class="user-info">
                        <strong>Welcome!</strong><br>
                        <small>Premium User</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            if st.button("Logout", key="sidebar_logout", use_container_width=True):
                st.session_state["token"] = None
                st.rerun()
            st.sidebar.markdown("--- ")
            st.sidebar.markdown("""
                <div style="padding-top: 20px; text-align: center; opacity: 0.8;">
                    <small>MetaboSync Pro v1.0</small><br>
                    <small>© 2023 All rights reserved.</small>
                </div>
                """, unsafe_allow_html=True)

        # Main Content Area
        st.markdown("<h1 class=\"icon-header\">✨ MetaboSync Pro Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style=\"color: var(--secondary-color); font-size: 1.1rem; margin-bottom: 2rem;\">Elevate your fitness journey with advanced analytics and personalized insights.</p>", unsafe_allow_html=True)

        # AI Form Analysis Section
        st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
        custom_header("🤖", "AI Form Analysis", level=2)
        st.markdown("<p style=\"color: var(--secondary-color);\">Upload an image of your exercise form for intelligent feedback and alignment checks.</p>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], help="Upload an image of your workout form here.")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            image_path = f"temp_{uploaded_file.name}"
            Image.fromarray(image_np).save(image_path)

            with st.spinner("Analyzing pose..."):
                processed_image, analysis_results = analyze_pose(image_path)
            
            if processed_image is not None and isinstance(analysis_results, dict):
                st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
                st.markdown("<h3 style=\"color: var(--primary-color);\">Analysis Results</h3>", unsafe_allow_html=True)
                
                col_img, col_metrics = st.columns([2, 1])
                with col_img:
                    st.image(processed_image, caption="Processed Image with Pose Detections", use_column_width=True, channels="BGR")
                
                with col_metrics:
                    st.markdown("<h4 style=\"color: var(--secondary-color);\">Key Metrics</h4>", unsafe_allow_html=True)
                    if "left_knee_angle" in analysis_results and analysis_results["left_knee_angle"] is not None:
                        st.metric(label="Left Knee Angle", value=f"{int(analysis_results["left_knee_angle"])}°")
                    else:
                        st.info("No knee angle detected or calculated.")

                    if "alignment_feedback" in analysis_results and analysis_results["alignment_feedback"]:
                        st.markdown(f"""
                            <div style="background-color: #FFF3E0; border-left: 5px solid #FFA726; padding: 10px; border-radius: 5px; margin-top: 15px;">
                                <h5 style="color: #FFA726;">💡 AI Feedback</h5>
                                <p style="color: var(--text-color);">{analysis_results["alignment_feedback"]}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(analysis_results) # Display error message from analyze_pose
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Log Workout Section
        st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
        custom_header("✍️", "Workout Entry Hub", level=2)
        st.markdown("<p style=\"color: var(--secondary-color);\">Log your workouts efficiently. Choose between a dynamic editor or quick-log common exercises.</p>", unsafe_allow_html=True)
        
        tab_new_workout, tab_quick_log = st.tabs(["Log New Workout (Dynamic Editor)", "Quick Log (Common Exercises)"])

        with tab_new_workout:
            exercise_name = st.text_input("Exercise Name (e.g., Bench Press)", key="new_exercise_name")
            st.write("Enter your sets below. You can add or remove rows dynamically!")
            
            default_sets = pd.DataFrame([{"set_number": 1, "reps": 10, "weight_kg": 20.0}])
            edited_df = st.data_editor(default_sets, num_rows="dynamic", use_container_width=True, hide_index=True)

            if st.button("🚀 Save Workout", use_container_width=True, key="save_new_workout"):
                if not exercise_name:
                    st.error("Please enter an exercise name.")
                else:
                    sets_data = edited_df.to_dict('records')
                    res = log_workout(exercise_name, sets_data)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"Logged {len(sets_data)} sets of {exercise_name} successfully!")
                        st.rerun()

        with tab_quick_log:
            st.info("Quick Log feature coming soon! Stay tuned for updates.")
            # Future implementation for quick logging common exercises

        st.markdown("</div>", unsafe_allow_html=True)

        # Progress Analytics Section
        st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
        custom_header("📈", "Performance Analytics", level=2)
        st.markdown("<p style=\"color: var(--secondary-color);\">Visualize your progress and gain insights into your training volume and frequency.</p>", unsafe_allow_html=True)

        history = get_workouts()
        
        if history and isinstance(history, list):
            analytics_data = []
            for workout in history:
                exercise = workout.get("exercise_name", "Unknown")
                sets = workout.get("sets_data", [])
                workout_date = pd.to_datetime(workout.get("timestamp")).date() # Assuming timestamp is available
                
                total_volume = sum([s.get("reps", 0) * s.get("weight_kg", 0.0) for s in sets])
                
                analytics_data.append({
                    "Date": workout_date,
                    "Exercise": exercise,
                    "Total Volume (kg)": total_volume,
                    "Frequency": 1 # For frequency count
                })
            
            if analytics_data:
                df_analytics = pd.DataFrame(analytics_data)
                df_analytics["Date"] = pd.to_datetime(df_analytics["Date"])

                col_volume, col_frequency = st.columns(2)

                with col_volume:
                    st.markdown("<h3 style=\"color: var(--primary-color);\">Volume Trend</h3>", unsafe_allow_html=True)
                    volume_trend_chart = alt.Chart(df_analytics).mark_line(point=True).encode(
                        x=alt.X("Date", axis=alt.Axis(format="%Y-%m-%d")),
                        y=alt.Y("Total Volume (kg)"),
                        tooltip=["Date", "Exercise", "Total Volume (kg)"]
                    ).properties(
                        title="Total Volume Over Time"
                    ).interactive()
                    st.altair_chart(volume_trend_chart, use_container_width=True)

                with col_frequency:
                    st.markdown("<h3 style=\"color: var(--primary-color);\">Exercise Frequency</h3>", unsafe_allow_html=True)
                    exercise_frequency = df_analytics.groupby("Exercise")["Frequency"].sum().reset_index()
                    pie_chart = alt.Chart(exercise_frequency).mark_arc().encode(
                        theta=alt.Theta(field="Frequency", type="quantitative"),
                        color=alt.Color(field="Exercise", type="nominal", title="Exercise"),
                        tooltip=["Exercise", "Frequency"]
                    ).properties(
                        title="Workout Frequency by Exercise"
                    )
                    st.altair_chart(pie_chart, use_container_width=True)

            else:
                st.info("Log some sets with weights to see your analytics!")
        else:
            st.info("Analytics will appear here once you log your first workout.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Workout History Section
        st.markdown("<div class=\"card-container\">", unsafe_allow_html=True)
        custom_header("📚", "Workout Logs", level=2)
        st.markdown("<p style=\"color: var(--secondary-color);\">Review your past workout sessions. Use the filter to find specific exercises.</p>", unsafe_allow_html=True)

        history = get_workouts()
        
        if history and isinstance(history, list):
            search_query = st.text_input("Filter workouts by exercise name", key="workout_filter", placeholder="e.g., Bench Press")
            
            filtered_history = [w for w in history if search_query.lower() in w.get("exercise_name", "").lower()]

            if filtered_history:
                # Sort history by date, newest first
                filtered_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                current_date = None
                for workout in filtered_history:
                    workout_timestamp = workout.get("timestamp")
                    workout_datetime = pd.to_datetime(workout_timestamp)
                    workout_date_str = workout_datetime.strftime("%Y-%m-%d")

                    if workout_date_str != current_date:
                        st.markdown(f"""
                        <h3 style="color: var(--primary-color); margin-top: 2rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 0.5rem;">
                            🗓️ {workout_date_str}
                        </h3>
                        """, unsafe_allow_html=True)
                        current_date = workout_date_str

                    exercise_name = workout.get('exercise_name', 'Unknown Exercise')
                    sets_data = workout.get('sets_data', [])
                    
                    with st.expander(f"🏋️‍♂️ {exercise_name} - {workout_datetime.strftime("%H:%M")}"):
                        if sets_data:
                            df = pd.DataFrame(sets_data)
                            df.rename(columns={
                                "set_number": "Set", 
                                "reps": "Reps", 
                                "weight_kg": "Weight (kg)"
                            }, inplace=True)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.write("No sets recorded.")
            else:
                st.info("No workouts match your filter criteria.")
        else:
            st.info("No workouts logged yet. Time to hit the iron!")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()