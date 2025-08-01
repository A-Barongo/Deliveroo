#!/usr/bin/env python3
"""
Script to check database and list all users.
Usage: python check_db.py
"""

from server.config import create_app, db
from server.models import User

def check_database():
    """Check database and list all users."""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking database...")
        print("=" * 50)
        
        # Count users
        total_users = User.query.count()
        admin_users = User.query.filter_by(admin=True).count()
        
        print(f"📊 Database Statistics:")
        print(f"  Total users: {total_users}")
        print(f"  Admin users: {admin_users}")
        print(f"  Regular users: {total_users - admin_users}")
        print()
        
        # List all users
        users = User.query.all()
        print("👥 All Users:")
        print("-" * 50)
        for user in users:
            admin_status = "✅ ADMIN" if user.admin else "👤 USER"
            print(f"  {admin_status} | {user.email} | {user.username}")
        
        print()
        print("💡 To make a user admin, run:")
        print("   sqlite3 instance/deliveroo.db")
        print("   UPDATE users SET admin = 1 WHERE email = 'your-email@example.com';")

if __name__ == '__main__':
    check_database() 