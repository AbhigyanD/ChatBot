#!/usr/bin/env python3
"""
Database Initialization Script for TechPal
Creates all necessary database tables
"""

from app.database import create_tables
from app.config import settings

def main():
    print("🗄️ Initializing TechPal Database...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        create_tables()
        print("✅ Database tables created successfully!")
        print("📊 Tables created:")
        print("   - users")
        print("   - conversations") 
        print("   - messages")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 