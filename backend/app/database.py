from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for easy setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitness_ai.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    from app.models import Base
    Base.metadata.create_all(bind=engine)


