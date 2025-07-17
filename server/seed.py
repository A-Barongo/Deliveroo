"""Seed script for Deliveroo app database."""
# pyright: reportCallIssue=false
from random import choice, uniform
from datetime import datetime
from faker import Faker
from server.config import create_app, db
from server.models import User, Parcel, ParcelHistory

app = create_app()

fake = Faker()

def seed_db():
    """Seed the database with initial data."""
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
                description=fake.text(max_nb_chars=50),
                weight=uniform(1.0, 10.0),
                status="pending",
                sender_name=fake.name(),
                sender_phone_number=fake.phone_number(),
                pickup_location_text=fake.address(),
                destination_location_text=fake.address(),
                pick_up_longitude=uniform(-180, 180),
                pick_up_latitude=uniform(-90, 90),
                destination_longitude=uniform(-180, 180),
                destination_latitude=uniform(-90, 90),
                current_location_longitude=uniform(-180, 180),
                current_location_latitude=uniform(-90, 90),
                distance=uniform(1.0, 100.0),
                cost=uniform(10.0, 100.0),
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
    seed_db()
