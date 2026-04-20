from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import hashlib
from datetime import datetime, timedelta
import json
import os

from app.models import User, UserProfile, WorkoutPlan, DietPlan, Subscription, GenderEnum, ActivityLevelEnum, GoalEnum, MembershipTypeEnum, SubscriptionDurationEnum, SubscriptionStatusEnum
from app.models import TimeSlot, SlotBooking, BookingStatusEnum
from app.database import get_db, create_tables
from app.models import User, UserProfile, WorkoutPlan, DietPlan, Subscription, GenderEnum, ActivityLevelEnum, GoalEnum, MembershipTypeEnum, SubscriptionDurationEnum, SubscriptionStatusEnum
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
    membership_type: Optional[str] = None  # New field

class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None
    goal: Optional[GoalEnum] = None
    membership_type: Optional[MembershipTypeEnum] = None  # New field

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
    membership_type: Optional[MembershipTypeEnum] = None
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

class SubscriptionCreate(BaseModel):
    membership_type: str  # yoga or gym
    duration: str  # 3_months, 6_months, annual

class SubscriptionResponse(BaseModel):
    id: int
    membership_type: MembershipTypeEnum
    duration: SubscriptionDurationEnum
    status: SubscriptionStatusEnum
    price: float
    start_date: datetime
    end_date: datetime
    
    class Config:
        from_attributes = True

# Subscription pricing
SUBSCRIPTION_PRICES = {
    "yoga": {
        "3_months": 2999.00,
        "6_months": 5499.00,
        "annual": 9999.00
    },
    "gym": {
        "3_months": 3999.00,
        "6_months": 7499.00,
        "annual": 13999.00
    }
}

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
                <p>Backend is working at <a href="/docs">http://localhost:6447/docs</a></p>
                <p>Frontend file not found. Please check the frontend directory.</p>
                <p>Tried path: {frontend_path}</p>
                <p>Error: {str(e)}</p>
                <p><a href="/api">View API Info</a></p>
            </body>
        </html>
        """)
@app.get("/slot-booking-dashboard.html", response_class=HTMLResponse)
async def serve_slot_booking_dashboard():
    # Use absolute path for the slot booking dashboard
    frontend_path = r"C:\Users\SanthoshNR\Desktop\fitness-ai-app\frontend\slot-booking-dashboard.html"
    
    # Fallback: try relative path from backend directory
    if not os.path.exists(frontend_path):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        frontend_path = os.path.join(project_root, "frontend", "slot-booking-dashboard.html")
    
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Slot Booking Dashboard Not Found</h1>
                <p>Tried path: {frontend_path}</p>
                <p>Error: {str(e)}</p>
                <p><a href="/">Back to Main Dashboard</a></p>
            </body>
        </html>
        """)

@app.get("/admin-panel.html", response_class=HTMLResponse)
async def serve_admin_panel():
    # Serve the admin panel page for booking management
    frontend_path = r"C:\Users\SanthoshNR\Desktop\fitness-ai-app\frontend\admin-panel.html"
    
    # Fallback: try relative path from backend directory
    if not os.path.exists(frontend_path):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        frontend_path = os.path.join(project_root, "frontend", "admin-panel.html")
    
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Admin Panel Not Found</h1>
                <p>Tried path: {frontend_path}</p>
                <p>Error: {str(e)}</p>
                <p><a href="/">Back to Main Dashboard</a></p>
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
        membership_enum = MembershipTypeEnum(profile.membership_type) if profile.membership_type else None
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
        existing_profile.membership_type = membership_enum.value if membership_enum else None
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
            membership_type=membership_enum.value if membership_enum else None,
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
    
    # Generate workout plan with membership type
    workout_data = WorkoutGenerator.generate_workout_plan(
        goal=profile.goal,
        activity_level=profile.activity_level,
        duration_weeks=duration_weeks,
        membership_type=profile.membership_type
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

# Subscription endpoints
@app.post("/subscription/{user_id}", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(user_id: int, subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create or update user subscription"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate membership type and duration
    try:
        membership_enum = MembershipTypeEnum(subscription.membership_type)
        duration_enum = SubscriptionDurationEnum(subscription.duration)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid membership type or duration")
    
    # Get price
    price = SUBSCRIPTION_PRICES.get(subscription.membership_type, {}).get(subscription.duration)
    if not price:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    # Calculate end date
    start_date = datetime.utcnow()
    if duration_enum == SubscriptionDurationEnum.THREE_MONTHS:
        end_date = start_date + timedelta(days=90)
    elif duration_enum == SubscriptionDurationEnum.SIX_MONTHS:
        end_date = start_date + timedelta(days=180)
    else:  # annual
        end_date = start_date + timedelta(days=365)
    
    # Check if subscription exists
    existing_subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if existing_subscription:
        # Update existing subscription
        existing_subscription.membership_type = membership_enum
        existing_subscription.duration = duration_enum
        existing_subscription.status = SubscriptionStatusEnum.ACTIVE
        existing_subscription.price = price
        existing_subscription.start_date = start_date
        existing_subscription.end_date = end_date
        existing_subscription.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_subscription)
        
        # Update user profile membership type
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile.membership_type = membership_enum
            db.commit()
        
        return existing_subscription
    else:
        # Create new subscription
        db_subscription = Subscription(
            user_id=user_id,
            membership_type=membership_enum,
            duration=duration_enum,
            status=SubscriptionStatusEnum.ACTIVE,
            price=price,
            start_date=start_date,
            end_date=end_date
        )
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        # Update user profile membership type
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile.membership_type = membership_enum
            db.commit()
        
        return db_subscription

@app.get("/subscription/{user_id}", response_model=SubscriptionResponse)
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    """Get user subscription"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    # Check if subscription is expired
    if subscription.end_date < datetime.utcnow() and subscription.status == SubscriptionStatusEnum.ACTIVE:
        subscription.status = SubscriptionStatusEnum.EXPIRED
        db.commit()
        db.refresh(subscription)
    
    return subscription

@app.get("/subscription-plans")
def get_subscription_plans():
    """Get all available subscription plans with pricing"""
    return {
        "plans": [
            {
                "membership_type": "yoga",
                "name": "Yoga Membership",
                "description": "Access to yoga classes and personalized yoga workout plans",
                "icon": "🧘",
                "durations": [
                    {
                        "duration": "3_months",
                        "name": "3 Months",
                        "price": SUBSCRIPTION_PRICES["yoga"]["3_months"],
                        "savings": 0,
                        "per_month": round(SUBSCRIPTION_PRICES["yoga"]["3_months"] / 3, 2)
                    },
                    {
                        "duration": "6_months",
                        "name": "6 Months",
                        "price": SUBSCRIPTION_PRICES["yoga"]["6_months"],
                        "savings": round((SUBSCRIPTION_PRICES["yoga"]["3_months"] * 2) - SUBSCRIPTION_PRICES["yoga"]["6_months"], 2),
                        "per_month": round(SUBSCRIPTION_PRICES["yoga"]["6_months"] / 6, 2)
                    },
                    {
                        "duration": "annual",
                        "name": "Annual (Best Value)",
                        "price": SUBSCRIPTION_PRICES["yoga"]["annual"],
                        "savings": round((SUBSCRIPTION_PRICES["yoga"]["3_months"] * 4) - SUBSCRIPTION_PRICES["yoga"]["annual"], 2),
                        "per_month": round(SUBSCRIPTION_PRICES["yoga"]["annual"] / 12, 2)
                    }
                ]
            },
            {
                "membership_type": "gym",
                "name": "Gym Membership",
                "description": "Full gym access with personalized strength training plans",
                "icon": "🏋️",
                "durations": [
                    {
                        "duration": "3_months",
                        "name": "3 Months",
                        "price": SUBSCRIPTION_PRICES["gym"]["3_months"],
                        "savings": 0,
                        "per_month": round(SUBSCRIPTION_PRICES["gym"]["3_months"] / 3, 2)
                    },
                    {
                        "duration": "6_months",
                        "name": "6 Months",
                        "price": SUBSCRIPTION_PRICES["gym"]["6_months"],
                        "savings": round((SUBSCRIPTION_PRICES["gym"]["3_months"] * 2) - SUBSCRIPTION_PRICES["gym"]["6_months"], 2),
                        "per_month": round(SUBSCRIPTION_PRICES["gym"]["6_months"] / 6, 2)
                    },
                    {
                        "duration": "annual",
                        "name": "Annual (Best Value)",
                        "price": SUBSCRIPTION_PRICES["gym"]["annual"],
                        "savings": round((SUBSCRIPTION_PRICES["gym"]["3_months"] * 4) - SUBSCRIPTION_PRICES["gym"]["annual"], 2),
                        "per_month": round(SUBSCRIPTION_PRICES["gym"]["annual"] / 12, 2)
                    }
                ]
            }
        ]
    }

@app.delete("/subscription/{user_id}")
def cancel_subscription(user_id: int, db: Session = Depends(get_db)):
    """Cancel user subscription"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    subscription.status = SubscriptionStatusEnum.CANCELLED
    subscription.updated_at = datetime.utcnow()
    db.commit()

# Pydantic models for slot booking
class TimeSlotCreate(BaseModel):
    membership_type: str
    date: str  # ISO format date
    time_slot: str  # "morning" or "evening"
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    capacity: int = 10

class TimeSlotResponse(BaseModel):
    id: int
    membership_type: MembershipTypeEnum
    date: datetime
    time_slot: str
    start_time: str
    end_time: str
    capacity: int
    booked_count: int
    is_available: bool
    
    class Config:
        from_attributes = True

class SlotBookingCreate(BaseModel):
    username: str
    email: EmailStr
    membership_type: str  # "yoga" or "gym"
    date_from: str  # ISO format date (YYYY-MM-DD)
    date_to: str  # ISO format date (YYYY-MM-DD)
    time_slot: str  # "morning" or "evening"

class SlotBookingResponse(BaseModel):
    id: int
    username: str
    email: str
    membership_type: MembershipTypeEnum
    date_from: datetime
    date_to: datetime
    time_slot: str
    status: BookingStatusEnum
    rejection_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookingApproval(BaseModel):
    booking_id: int
    approved: bool
    rejection_reason: Optional[str] = None

# Time Slot Management Endpoints (Admin)
@app.post("/admin/time-slots", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
def create_time_slot(slot: TimeSlotCreate, db: Session = Depends(get_db)):
    """Create a new time slot (Admin only)"""
    try:
        membership_enum = MembershipTypeEnum(slot.membership_type)
        slot_date = datetime.fromisoformat(slot.date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    # Validate time_slot value
    if slot.time_slot not in ["morning", "evening"]:
        raise HTTPException(status_code=400, detail="time_slot must be 'morning' or 'evening'")
    
    # Check if slot already exists
    existing_slot = db.query(TimeSlot).filter(
        TimeSlot.membership_type == membership_enum.value,
        TimeSlot.date == slot_date,
        TimeSlot.time_slot == slot.time_slot
    ).first()
    
    if existing_slot:
        raise HTTPException(status_code=400, detail="Time slot already exists")
    
    db_slot = TimeSlot(
        membership_type=membership_enum.value,
        date=slot_date,
        time_slot=slot.time_slot,
        start_time=slot.start_time,
        end_time=slot.end_time,
        capacity=slot.capacity,
        booked_count=0,
        is_available=1
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    
    return db_slot

@app.get("/time-slots", response_model=List[TimeSlotResponse])
def get_available_time_slots(
    membership_type: Optional[str] = None,
    date: Optional[str] = None,
    time_slot: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available time slots, optionally filtered by membership type, date, and time slot"""
    query = db.query(TimeSlot).filter(TimeSlot.is_available == 1)
    
    if membership_type:
        try:
            membership_enum = MembershipTypeEnum(membership_type)
            query = query.filter(TimeSlot.membership_type == membership_enum.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid membership type")
    
    if date:
        try:
            filter_date = datetime.fromisoformat(date)
            query = query.filter(TimeSlot.date >= filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    
    if time_slot:
        if time_slot not in ["morning", "evening"]:
            raise HTTPException(status_code=400, detail="time_slot must be 'morning' or 'evening'")
        query = query.filter(TimeSlot.time_slot == time_slot)
    
    slots = query.order_by(TimeSlot.date, TimeSlot.time_slot).all()
    return slots

@app.get("/time-slots/{slot_id}", response_model=TimeSlotResponse)
def get_time_slot(slot_id: int, db: Session = Depends(get_db)):
    """Get a specific time slot"""
    slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return slot

# Slot Booking Endpoints (User)
@app.post("/bookings", response_model=SlotBookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking: SlotBookingCreate, db: Session = Depends(get_db)):
    """Create a new slot booking request"""
    # Validate membership type
    try:
        membership_enum = MembershipTypeEnum(booking.membership_type)
        date_from = datetime.fromisoformat(booking.date_from)
        date_to = datetime.fromisoformat(booking.date_to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    # Validate time_slot
    if booking.time_slot not in ["morning", "evening"]:
        raise HTTPException(status_code=400, detail="time_slot must be 'morning' or 'evening'")
    
    # Validate date range
    if date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")
    
    # Check if user exists by email
    user = db.query(User).filter(User.email == booking.email).first()
    user_id = user.id if user else None
    
    # Check for overlapping bookings
    existing_booking = db.query(SlotBooking).filter(
        SlotBooking.email == booking.email,
        SlotBooking.membership_type == membership_enum.value,
        SlotBooking.time_slot == booking.time_slot,
        SlotBooking.status.in_([BookingStatusEnum.PENDING.value, BookingStatusEnum.APPROVED.value]),
        # Check for date overlap
        SlotBooking.date_from <= date_to,
        SlotBooking.date_to >= date_from
    ).first()
    
    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail="You already have a booking that overlaps with this date range and time slot"
        )
    
    # Create booking
    db_booking = SlotBooking(
        user_id=user_id,
        username=booking.username,
        email=booking.email,
        membership_type=membership_enum.value,
        date_from=date_from,
        date_to=date_to,
        time_slot=booking.time_slot,
        status=BookingStatusEnum.PENDING.value
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

@app.get("/bookings/email/{email}", response_model=List[SlotBookingResponse])
def get_bookings_by_email(email: str, db: Session = Depends(get_db)):
    """Get all bookings for a user by email"""
    bookings = db.query(SlotBooking).filter(
        SlotBooking.email == email
    ).order_by(SlotBooking.created_at.desc()).all()
    
    return bookings

@app.get("/bookings/status/{booking_id}", response_model=SlotBookingResponse)
def get_booking_status(booking_id: int, db: Session = Depends(get_db)):
    """Get status of a specific booking"""
    booking = db.query(SlotBooking).filter(SlotBooking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, email: str, db: Session = Depends(get_db)):
    """Cancel a booking (user can cancel their own pending bookings)"""
    booking = db.query(SlotBooking).filter(
        SlotBooking.id == booking_id,
        SlotBooking.email == email
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or email mismatch")
    
    if booking.status != BookingStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Only pending bookings can be cancelled"
        )
    
    booking.status = BookingStatusEnum.CANCELLED.value
    booking.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Booking cancelled successfully"}

# Admin Endpoints for Booking Management
@app.get("/admin/bookings", response_model=List[SlotBookingResponse])
def get_all_bookings(
    status_filter: Optional[str] = None,
    membership_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all bookings (Admin only), optionally filtered by status and membership type"""
    query = db.query(SlotBooking)
    
    if status_filter:
        try:
            status_enum = BookingStatusEnum(status_filter)
            query = query.filter(SlotBooking.status == status_enum.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if membership_type:
        try:
            membership_enum = MembershipTypeEnum(membership_type)
            query = query.filter(SlotBooking.membership_type == membership_enum.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid membership type")
    
    bookings = query.order_by(SlotBooking.created_at.desc()).all()
    return bookings

@app.post("/admin/bookings/approve")
def approve_or_reject_booking(
    approval: BookingApproval,
    admin_id: int,
    db: Session = Depends(get_db)
):
    """Approve or reject a booking request (Admin only)"""
    # Check if admin exists (in production, verify admin role)
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Get booking
    booking = db.query(SlotBooking).filter(SlotBooking.id == approval.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Only pending bookings can be approved or rejected"
        )
    
    if approval.approved:
        booking.status = BookingStatusEnum.APPROVED.value
        booking.approved_by = admin_id
        booking.approved_at = datetime.utcnow()
        booking.rejection_reason = None
        
        message = "Booking approved successfully"
    else:
        if not approval.rejection_reason:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required when rejecting a booking"
            )
        
        booking.status = BookingStatusEnum.REJECTED.value
        booking.rejection_reason = approval.rejection_reason
        booking.approved_by = admin_id
        booking.approved_at = datetime.utcnow()
        
        message = "Booking rejected successfully"
    
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    
    return {
        "message": message,
        "booking": {
            "id": booking.id,
            "username": booking.username,
            "email": booking.email,
            "status": booking.status,
            "rejection_reason": booking.rejection_reason
        }
    }

@app.get("/admin/bookings/pending", response_model=List[SlotBookingResponse])
def get_pending_bookings(db: Session = Depends(get_db)):
    """Get all pending bookings (Admin only)"""
    bookings = db.query(SlotBooking).filter(
        SlotBooking.status == BookingStatusEnum.PENDING.value
    ).order_by(SlotBooking.created_at.asc()).all()
    
    return bookings

    
    return {"message": "Subscription cancelled successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)

