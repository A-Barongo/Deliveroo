
from faker import Faker
from server.config import create_app, db
from server.models import User, Parcel, ParcelHistory
from random import choice, uniform
from datetime import datetime

fake = Faker()
app = create_app()

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
                longitude_hash=str(fake.longitude()),
                latitude_hash=str(fake.latitude())
            )
            user.password = "password123"
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        print("Seeding parcels...")
        # Refresh user list with IDs after commit
        users = User.query.all()
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
                recipient_phone_number=fake.phone_number(),
                courier_id=None,
                user_id=sender.id
            )
            parcels.append(parcel)
        db.session.bulk_save_objects(parcels)
        db.session.commit()

        print("Seeding parcel history...")
        parcels = Parcel.query.all()
        histories = []
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
            histories.append(history)
        db.session.bulk_save_objects(histories)
        db.session.commit()

        print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
