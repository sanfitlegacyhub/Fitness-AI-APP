from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import hashlib
from datetime import datetime
import json
import os

from app.database import get_db, create_tables
from app.models import User, UserProfile, WorkoutPlan, DietPlan, GenderEnum, ActivityLevelEnum, GoalEnum
from app.calculator import FitnessCalculator
from app.workout_generator import WorkoutGenerator
from app.diet_generator import DietGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Fitness AI API",
    description="AI-powered fitness and nutrition planning API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple password hashing using hashlib (for demo purposes)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserProfileCreate(BaseModel):
    age: int
    gender: str  # Accept string, will convert to enum
    height: float
    weight: float
    activity_level: str  # Accept string, will convert to enum
    goal: str  # Accept string, will convert to enum

class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: int
    age: int
    gender: GenderEnum
    height: float
    weight: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    bmi: Optional[float] = None
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    target_calories: Optional[float] = None
    
    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    target_calories: float
    macros: dict

class WorkoutPlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration_weeks: Optional[int]
    difficulty_level: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DietPlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    daily_calories: float
    protein_grams: float
    carbs_grams: float
    fats_grams: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Startup event
@app.on_event("startup")
def startup_event():
    create_tables()

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    # Use absolute path for the new dashboard
    frontend_path = r"C:\Users\SanthoshNR\Desktop\fitness-ai-app\frontend\dashboard.html"
    
    # Fallback: try relative path from backend directory
    if not os.path.exists(frontend_path):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        frontend_path = os.path.join(project_root, "frontend", "dashboard.html")
    
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🎉 Fitness AI API is Running!</h1>
                <p>Backend is working at <a href="/docs">http://localhost:8486/docs</a></p>
                <p>Frontend file not found. Please check the frontend directory.</p>
                <p>Tried path: {frontend_path}</p>
                <p>Error: {str(e)}</p>
                <p><a href="/api">View API Info</a></p>
            </body>
        </html>
        """)

@app.get("/api")
def api_info():
    return {
        "message": "Welcome to Fitness AI API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "profile": "/profile",
            "metrics": "/metrics",
            "workout": "/workout",
            "diet": "/diet"
        }
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# User endpoints
class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "message": "Login successful"
    }

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Profile endpoints - Alternative route for frontend compatibility
@app.post("/users/{user_id}/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_user_profile(user_id: int, profile: UserProfileCreate, db: Session = Depends(get_db)):
    """Create or update user profile and calculate metrics"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    # Convert string values to enums
    try:
        gender_enum = GenderEnum(profile.gender)
        activity_enum = ActivityLevelEnum(profile.activity_level)
        goal_enum = GoalEnum(profile.goal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    
    # Calculate metrics
    metrics = FitnessCalculator.calculate_all_metrics(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=gender_enum,
        activity_level=activity_enum,
        goal=goal_enum
    )
    
    if existing_profile:
        # Update existing profile
        existing_profile.age = profile.age
        existing_profile.gender = gender_enum.value
        existing_profile.height = profile.height
        existing_profile.weight = profile.weight
        existing_profile.activity_level = activity_enum.value
        existing_profile.goal = goal_enum.value
        existing_profile.bmi = metrics["bmi"]
        existing_profile.bmr = metrics["bmr"]
        existing_profile.tdee = metrics["tdee"]
        existing_profile.target_calories = metrics["target_calories"]
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new profile
        db_profile = UserProfile(
            user_id=user_id,
            age=profile.age,
            gender=gender_enum.value,
            height=profile.height,
            weight=profile.weight,
            activity_level=activity_enum.value,
            goal=goal_enum.value,
            bmi=metrics["bmi"],
            bmr=metrics["bmr"],
            tdee=metrics["tdee"],
            target_calories=metrics["target_calories"]
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

# Profile endpoints
@app.post("/profile/{user_id}", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(user_id: int, profile: UserProfileCreate, db: Session = Depends(get_db)):
    """Create user profile and calculate metrics"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    # Calculate metrics
    metrics = FitnessCalculator.calculate_all_metrics(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    
    # Create profile
    db_profile = UserProfile(
        user_id=user_id,
        age=profile.age,
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        activity_level=profile.activity_level,
        goal=profile.goal,
        bmi=metrics["bmi"],
        bmr=metrics["bmr"],
        tdee=metrics["tdee"],
        target_calories=metrics["target_calories"]
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@app.get("/profile/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/profile/{user_id}", response_model=ProfileResponse)
def update_profile(user_id: int, profile_update: UserProfileUpdate, db: Session = Depends(get_db)):
    """Update user profile and recalculate metrics"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Recalculate metrics
    metrics = FitnessCalculator.calculate_all_metrics(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    
    profile.bmi = metrics["bmi"]
    profile.bmr = metrics["bmr"]
    profile.tdee = metrics["tdee"]
    profile.target_calories = metrics["target_calories"]
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    return profile

# Metrics endpoint
@app.get("/metrics/{user_id}", response_model=MetricsResponse)
def get_metrics(user_id: int, db: Session = Depends(get_db)):
    """Get calculated fitness metrics"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    metrics = FitnessCalculator.calculate_all_metrics(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    
    return metrics

# Alternative workout endpoint for frontend compatibility
@app.post("/users/{user_id}/workout", status_code=status.HTTP_201_CREATED)
def generate_user_workout(user_id: int, duration_weeks: int = 8, db: Session = Depends(get_db)):
    """Generate AI workout plan for user"""
    return generate_workout(user_id, duration_weeks, db)

# Workout plan endpoints
@app.post("/workout/{user_id}", status_code=status.HTTP_201_CREATED)
def generate_workout(user_id: int, duration_weeks: int = 8, db: Session = Depends(get_db)):
    """Generate AI workout plan"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Generate workout plan
    workout_data = WorkoutGenerator.generate_workout_plan(
        goal=profile.goal,
        activity_level=profile.activity_level,
        duration_weeks=duration_weeks
    )
    
    # Save to database
    db_workout = WorkoutPlan(
        user_id=user_id,
        title=workout_data["title"],
        description=f"Personalized {workout_data['difficulty']} level workout plan",
        duration_weeks=duration_weeks,
        difficulty_level=workout_data["difficulty"],
        plan_data=json.dumps(workout_data)
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    # Flatten exercises for frontend
    exercises = []
    for day, day_data in workout_data.get("weekly_schedule", {}).items():
        for exercise in day_data.get("exercises", []):
            if "name" in exercise and exercise["name"] not in ["Rest", "Active Recovery"]:
                exercises.append({
                    "name": exercise.get("name", ""),
                    "category": day,
                    "description": f"Part of your {day} routine",
                    "sets": exercise.get("sets", 3),
                    "reps": exercise.get("reps", "10-12"),
                    "rest": exercise.get("rest", "60-90 seconds")
                })
    
    return {
        "id": db_workout.id,
        "exercises": exercises,
        "title": workout_data["title"],
        "difficulty": workout_data["difficulty"]
    }

@app.get("/workout/{user_id}/latest")
def get_latest_workout(user_id: int, db: Session = Depends(get_db)):
    """Get latest workout plan"""
    workout = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id
    ).order_by(WorkoutPlan.created_at.desc()).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="No workout plan found")
    
    return {
        "id": workout.id,
        "title": workout.title,
        "created_at": workout.created_at,
        "plan": json.loads(workout.plan_data)
    }

@app.get("/workout/{user_id}/all", response_model=List[WorkoutPlanResponse])
def get_all_workouts(user_id: int, db: Session = Depends(get_db)):
    """Get all workout plans for user"""
    workouts = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id
    ).order_by(WorkoutPlan.created_at.desc()).all()
    
    return workouts

# Alternative diet endpoint for frontend compatibility
@app.post("/users/{user_id}/diet", status_code=status.HTTP_201_CREATED)
def generate_user_diet(user_id: int, db: Session = Depends(get_db)):
    """Generate AI diet plan for user"""
    return generate_diet(user_id, db)

# Diet plan endpoints
@app.post("/diet/{user_id}", status_code=status.HTTP_201_CREATED)
def generate_diet(user_id: int, db: Session = Depends(get_db)):
    """Generate AI diet plan"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Calculate macros
    macros = FitnessCalculator.calculate_macros(profile.target_calories, profile.goal)
    
    # Generate diet plan
    diet_data = DietGenerator.generate_diet_plan(
        target_calories=profile.target_calories,
        protein_grams=macros["protein"],
        carbs_grams=macros["carbs"],
        fats_grams=macros["fats"],
        goal=profile.goal
    )
    
    # Save to database
    db_diet = DietPlan(
        user_id=user_id,
        title=diet_data["title"],
        description=f"Personalized diet plan for {profile.goal.value.replace('_', ' ')}",
        daily_calories=profile.target_calories,
        protein_grams=macros["protein"],
        carbs_grams=macros["carbs"],
        fats_grams=macros["fats"],
        plan_data=json.dumps(diet_data)
    )
    db.add(db_diet)
    db.commit()
    db.refresh(db_diet)
    
    # Format for frontend: convert meal_plan dict to meals array
    meals = []
    for meal_type, meal_data in diet_data.get("meal_plan", {}).items():
        meals.append({
            "meal_type": meal_type.title(),
            "options": [
                {
                    "name": option["name"],
                    "description": f"A nutritious {meal_type} option",
                    "calories": option["calories"],
                    "protein": option["protein"],
                    "carbs": option["carbs"],
                    "fats": option["fats"]
                }
                for option in meal_data.get("meal_options", [])
            ]
        })
    
    return {
        "id": db_diet.id,
        "meals": meals,
        "title": diet_data["title"],
        "daily_calories": diet_data["daily_calories"]
    }

@app.get("/diet/{user_id}/latest")
def get_latest_diet(user_id: int, db: Session = Depends(get_db)):
    """Get latest diet plan"""
    diet = db.query(DietPlan).filter(
        DietPlan.user_id == user_id
    ).order_by(DietPlan.created_at.desc()).first()
    
    if not diet:
        raise HTTPException(status_code=404, detail="No diet plan found")
    
    return {
        "id": diet.id,
        "title": diet.title,
        "created_at": diet.created_at,
        "plan": json.loads(diet.plan_data)
    }

@app.get("/diet/{user_id}/all", response_model=List[DietPlanResponse])
def get_all_diets(user_id: int, db: Session = Depends(get_db)):
    """Get all diet plans for user"""
    diets = db.query(DietPlan).filter(
        DietPlan.user_id == user_id
    ).order_by(DietPlan.created_at.desc()).all()
    
    return diets

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8486)

