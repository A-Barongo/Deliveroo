#!/usr/bin/env python3
"""
Seed script for Neon PostgreSQL database.
Usage: python seed_neon.py
"""

from faker import Faker
from server.config import create_app, db
from server.models import User, Parcel, ParcelHistory
from random import choice, uniform, randint
from datetime import datetime, timezone

fake = Faker()
app = create_app()

def seed_neon_db():
    """Seed the Neon database with test data."""
    
    with app.app_context():
        print("🌱 Starting Neon database seeding...")
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        ParcelHistory.query.delete()
        Parcel.query.delete()
        User.query.delete()
        db.session.commit()

        print("👥 Creating users...")
        users = []
        
        # Create your admin user
        admin_user = User(
            username="Brian Munene Mwirigi",
            email="brianinesh@gmail.com",
            phone_number="+254700000000",
            longitude_hash=str(fake.longitude()),
            latitude_hash=str(fake.latitude()),
            admin=True  # Make you admin
        )
        admin_user.password = "password123"
        users.append(admin_user)
        
        # Create some test users
        test_users = [
            {"username": "John Doe", "email": "john@example.com", "admin": False},
            {"username": "Jane Smith", "email": "jane@example.com", "admin": False},
            {"username": "Admin User", "email": "admin@deliveroo.com", "admin": True},
        ]
        
        for user_data in test_users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                phone_number=fake.phone_number()[:20],
                longitude_hash=str(fake.longitude()),
                latitude_hash=str(fake.latitude()),
                admin=user_data["admin"]
            )
            user.password = "password123"
            users.append(user)
        
        # Add some fake users
        for i in range(5):
            email = fake.email()
            if not email.endswith(".com"):
                email = email.split("@")[0] + "@example.com"

            user = User(
                username=fake.user_name(),
                email=email,
                phone_number=fake.phone_number()[:20],
                longitude_hash=str(fake.longitude()),
                latitude_hash=str(fake.latitude()),
                admin=False
            )
            user.password = "password123"
            users.append(user)

        db.session.add_all(users)
        db.session.commit()
        print(f"✅ Created {len(users)} users")

        print("📦 Creating parcels...")
        users = User.query.all()
        parcels = []
        
        # Create some test parcels
        test_parcels = [
            {
                "description": "Electronics package",
                "pickup": "Nairobi CBD",
                "destination": "Thika Town",
                "weight": 2.5,
                "status": "pending"
            },
            {
                "description": "Food delivery",
                "pickup": "Westlands",
                "destination": "Kilimani",
                "weight": 1.2,
                "status": "in_transit"
            },
            {
                "description": "Documents",
                "pickup": "Mombasa",
                "destination": "Nairobi",
                "weight": 0.5,
                "status": "delivered"
            }
        ]
        
        for parcel_data in test_parcels:
            sender = choice(users)
            parcel = Parcel(
                description=parcel_data["description"],
                weight=parcel_data["weight"],
                status=parcel_data["status"],
                sender_name=fake.name(),
                sender_phone_number=fake.phone_number()[:32],
                pickup_location_text=parcel_data["pickup"],
                destination_location_text=parcel_data["destination"],
                pick_up_longitude=float(fake.longitude()),
                pick_up_latitude=float(fake.latitude()),
                destination_longitude=float(fake.longitude()),
                destination_latitude=float(fake.latitude()),
                current_location_longitude=float(fake.longitude()),
                current_location_latitude=float(fake.latitude()),
                current_location=fake.city(),
                distance=round(uniform(1.0, 100.0), 2),
                cost=round(uniform(100.0, 1000.0), 2),
                recipient_name=fake.name(),
                recipient_phone_number=fake.phone_number()[:32],
                courier_id=None,
                user_id=sender.id
            )
            parcels.append(parcel)
        
        # Add some random parcels
        for _ in range(10):
            sender = choice(users)
            parcel = Parcel(
                description=fake.text(max_nb_chars=50),
                weight=round(uniform(1.0, 10.0), 2),
                status=choice(["pending", "in_transit", "delivered"]),
                sender_name=fake.name(),
                sender_phone_number=fake.phone_number()[:32],
                pickup_location_text=fake.address(),
                destination_location_text=fake.address(),
                pick_up_longitude=float(fake.longitude()),
                pick_up_latitude=float(fake.latitude()),
                destination_longitude=float(fake.longitude()),
                destination_latitude=float(fake.latitude()),
                current_location_longitude=float(fake.longitude()),
                current_location_latitude=float(fake.latitude()),
                current_location=fake.city(),
                distance=round(uniform(1.0, 100.0), 2),
                cost=round(uniform(100.0, 1000.0), 2),
                recipient_name=fake.name(),
                recipient_phone_number=fake.phone_number()[:32],
                courier_id=None,
                user_id=sender.id
            )
            parcels.append(parcel)

        db.session.bulk_save_objects(parcels)
        db.session.commit()
        print(f"✅ Created {len(parcels)} parcels")

        print("📝 Creating parcel history...")
        parcels = Parcel.query.all()
        histories = []
        
        for _ in range(20):
            parcel = choice(parcels)
            updater = choice(users)
            history = ParcelHistory(
                parcel_id=parcel.id,
                updated_by=updater.id,
                update_type=choice(["status", "location", "cost"]),
                old_value="pending",
                new_value=choice(["in_transit", "delivered", "cancelled"]),
                timestamp=datetime.now(timezone.utc)
            )
            histories.append(history)

        db.session.bulk_save_objects(histories)
        db.session.commit()
        print(f"✅ Created {len(histories)} history records")

        print("\n🎉 Neon database seeding complete!")
        print("\n📊 Summary:")
        print(f"  👥 Users: {User.query.count()}")
        print(f"  📦 Parcels: {Parcel.query.count()}")
        print(f"  📝 History: {ParcelHistory.query.count()}")
        print(f"  👑 Admins: {User.query.filter_by(admin=True).count()}")
        
        print("\n🔑 Login Credentials:")
        print("  Email: brianinesh@gmail.com")
        print("  Password: password123")
        print("  Status: ADMIN ✅")

if __name__ == '__main__':
    seed_neon_db() 