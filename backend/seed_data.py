from datetime import date, timedelta
from app.core.database import SessionLocal
from app.models.schema import WorkoutLog, NutritionLog

def seed_database():
    db = SessionLocal()

    print("Injecting test data into MetaboSync...")

    # Let's create data for the last 3 days
    today = date.today()
    
    workouts = [
        WorkoutLog(date=today - timedelta(days=2), exercise_type="Squats", form_accuracy=94.5, duration_minutes=45, joint_stress_score=1.2),
        WorkoutLog(date=today - timedelta(days=1), exercise_type="Deadlifts", form_accuracy=88.0, duration_minutes=50, joint_stress_score=2.1), # Notice the drop in accuracy
        WorkoutLog(date=today, exercise_type="Squats", form_accuracy=91.2, duration_minutes=40, joint_stress_score=1.5),
    ]

    nutrition = [
        # High protein day
        NutritionLog(date=today - timedelta(days=2), total_calories=2100, protein_grams=110, carbs_grams=250, fats_grams=60, dietary_preference="Vegetarian (No Eggs)"),
        # Low protein day (correlates with the form accuracy drop on deadlifts!)
        NutritionLog(date=today - timedelta(days=1), total_calories=1800, protein_grams=45, carbs_grams=300, fats_grams=50, dietary_preference="Vegetarian (No Eggs)"),
        # Recovery day
        NutritionLog(date=today, total_calories=2000, protein_grams=95, carbs_grams=220, fats_grams=55, dietary_preference="Vegetarian (No Eggs)"),
    ]

    db.add_all(workouts)
    db.add_all(nutrition)
    db.commit()
    db.close()
    
    print("Test data successfully injected! Your analytics engine is ready to fire.")

if __name__ == "__main__":
    seed_database()