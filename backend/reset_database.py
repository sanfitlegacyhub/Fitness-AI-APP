"""
Reset Database Script
This script deletes the existing database and creates a fresh one.
Run this when you want to start with a clean database.
"""

import os
from app.database import create_tables

# Path to database file
DB_FILE = "fitness_ai.db"

def reset_database():
    """Delete existing database and create fresh tables"""
    
    # Check if database exists
    if os.path.exists(DB_FILE):
        print(f"🗑️  Deleting existing database: {DB_FILE}")
        os.remove(DB_FILE)
        print("✅ Database deleted successfully!")
    else:
        print("ℹ️  No existing database found.")
    
    # Create fresh tables
    print("🔨 Creating fresh database tables...")
    create_tables()
    print("✅ Fresh database created successfully!")
    print("\n🎉 Database reset complete! You can now start the server.")

if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE RESET UTILITY")
    print("=" * 50)
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    
    confirm = input("\nAre you sure you want to continue? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        reset_database()
    else:
        print("\n❌ Database reset cancelled.")

# Made with Bob
