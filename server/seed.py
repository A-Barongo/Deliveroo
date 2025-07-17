#!/usr/bin/env python3

from faker import Faker
from config import app, db
from models import User, Parcel, ParcelHistory
from random import choice, uniform, randint
from datetime import datetime
import random

fake = Faker()

def seed_data():
    with app.app_context():
        print("Clearing existing data...")
        ParcelHistory.query.delete()
        Parcel.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding users...")
        users = []
        for _ in range(10):
            email = fake.email()
            if not email.endswith(".com"):
                email = email.split("@")[0] + "@example.com"

            user = User(
                username=fake.user_name(),
                email=email,
                phone_number=fake.phone_number(),
                longitude_hash=str(fake.longitude()),  # Converted to string
                latitude_hash=str(fake.latitude())     # Converted to string
            )
            user.password = "password123"
            users.append(user)
            db.session.add(user)
        db.session.commit()

        print("Seeding parcels...")
        parcels = []
        for _ in range(20):
            sender = choice(users)
            parcel = Parcel(
                description=fake.sentence(),
                weight=round(uniform(0.5, 10.0), 2),
                status=choice(['pending', 'in_transit', 'delivered']),
                sender_name=sender.username,
                sender_phone_number=sender.phone_number,
                pickup_location_text=fake.address(),
                destination_location_text=fake.address(),
                pick_up_longitude=float(fake.longitude()),
                pick_up_latitude=float(fake.latitude()),
                destination_longitude=float(fake.longitude()),
                destination_latitude=float(fake.latitude()),
                current_location_longitude=float(fake.longitude()),
                current_location_latitude=float(fake.latitude()),
                distance=round(uniform(1.0, 100.0), 2),
                cost=round(uniform(100.0, 1000.0), 2),
                recipient_name=fake.name(),
                recipient_phone_number=fake.phone_number(),
                courier_id=None,
                user_id=sender.id
            )
            parcels.append(parcel)
            db.session.add(parcel)
        db.session.commit()

        print("Seeding parcel history...")
        for _ in range(30):
            parcel = choice(parcels)
            updater = choice(users)
            history = ParcelHistory(
                parcel_id=parcel.id,
                updated_by=updater.id,
                update_type=choice(["status", "location", "cost"]),
                old_value="pending",
                new_value=choice(["in_transit", "delivered", "cancelled"]),
                timestamp=datetime.now()
            )
            db.session.add(history)

        db.session.commit()
        print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
