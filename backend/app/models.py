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

class SubscriptionDurationEnum(str, enum.Enum):
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    ANNUAL = "annual"

class SubscriptionStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class BookingStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

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
    subscription = relationship("Subscription", back_populates="user", uselist=False)

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

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Subscription Details
    membership_type = Column(Enum(MembershipTypeEnum), nullable=False)  # yoga or gym
    duration = Column(Enum(SubscriptionDurationEnum), nullable=False)  # 3, 6, or 12 months
    status = Column(Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.ACTIVE)
    
    # Pricing
    price = Column(Float, nullable=False)
    
    # Dates
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")

# Made with Bob


class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    membership_type = Column(Enum(MembershipTypeEnum), nullable=False)
    date = Column(DateTime, nullable=False)
    time_slot = Column(String, nullable=False)  # "morning" or "evening"
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)    # Format: "HH:MM"
    capacity = Column(Integer, default=10)
    booked_count = Column(Integer, default=0)
    is_available = Column(Integer, default=1)  # SQLite doesn't have boolean, use 1/0
    created_at = Column(DateTime, default=datetime.utcnow)

class SlotBooking(Base):
    __tablename__ = "slot_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for guest bookings
    
    # User details (for guest bookings or verification)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    # Booking details
    membership_type = Column(Enum(MembershipTypeEnum), nullable=False)
    date_from = Column(DateTime, nullable=False)  # Start date of booking period
    date_to = Column(DateTime, nullable=False)    # End date of booking period
    time_slot = Column(String, nullable=False)    # "morning" or "evening"
    
    # Status tracking
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.PENDING)
    rejection_reason = Column(Text, nullable=True)
    
    # Admin details
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[approved_by])
