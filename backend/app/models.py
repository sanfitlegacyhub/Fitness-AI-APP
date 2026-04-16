from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ActivityLevelEnum(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

class GoalEnum(str, enum.Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"

class MembershipTypeEnum(str, enum.Enum):
    YOGA = "yoga"
    GYM = "gym"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    workouts = relationship("WorkoutPlan", back_populates="user")
    diet_plans = relationship("DietPlan", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Personal Info
    age = Column(Integer)
    gender = Column(Enum(GenderEnum))
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    
    # Fitness Info
    activity_level = Column(Enum(ActivityLevelEnum))
    goal = Column(Enum(GoalEnum))
    membership_type = Column(Enum(MembershipTypeEnum), nullable=True)  # New field
    
    # Calculated Metrics
    bmi = Column(Float)
    bmr = Column(Float)
    tdee = Column(Float)
    target_calories = Column(Float)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    description = Column(Text)
    duration_weeks = Column(Integer)
    difficulty_level = Column(String)
    plan_data = Column(Text)  # JSON string of workout details
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workouts")

class DietPlan(Base):
    __tablename__ = "diet_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, nullable=False)
    description = Column(Text)
    daily_calories = Column(Float)
    protein_grams = Column(Float)
    carbs_grams = Column(Float)
    fats_grams = Column(Float)
    plan_data = Column(Text)  # JSON string of meal details
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="diet_plans")

# Made with Bob
