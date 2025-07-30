#!/usr/bin/env python3
"""Initialize the database with all tables."""

import os
from sqlalchemy import inspect
from server.config import create_app, db
from server.models import User, Parcel, ParcelHistory

def init_database():
    """Initialize the database with all tables."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")

if __name__ == "__main__":
    init_database() 