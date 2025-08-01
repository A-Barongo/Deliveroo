"""Debug routes for checking database."""
from flask import jsonify, request
from flask_restful import Resource
from server.models import User
from server.config import db

class DebugUsers(Resource):
    """Debug endpoint to check users in database."""
    
    def get(self):
        """Get all users (for debugging)."""
        try:
            users = User.query.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'admin': user.admin
                })
            
            return {
                'total_users': len(user_list),
                'admin_users': len([u for u in user_list if u['admin']]),
                'users': user_list
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class MakeAdmin(Resource):
    """Debug endpoint to make a user admin."""
    
    def post(self):
        """Make a user admin by email."""
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return {'error': 'Email is required'}, 400
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return {'error': f'User with email {email} not found'}, 404
            
            if user.admin:
                return {'message': f'User {email} is already an admin'}, 200
            
            user.admin = True
            db.session.commit()
            
            return {
                'message': f'Successfully made {email} an admin',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'admin': user.admin
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class SeedDatabase(Resource):
    """Debug endpoint to seed the database."""
    
    def post(self):
        """Seed the database with test data."""
        try:
            from faker import Faker
            from random import choice, uniform
            from datetime import datetime, timezone
            
            fake = Faker()
            
            # Clear existing data
            ParcelHistory.query.delete()
            Parcel.query.delete()
            User.query.delete()
            db.session.commit()
            
            # Create users
            users = []
            
            # Create your admin user
            admin_user = User(
                username="Brian Munene Mwirigi",
                email="brianinesh@gmail.com",
                phone_number="+254700000000",
                longitude_hash=str(fake.longitude()),
                latitude_hash=str(fake.latitude()),
                admin=True
            )
            admin_user.password = "password123"
            users.append(admin_user)
            
            # Create test users
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
            
            # Add fake users
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
            
            # Create parcels
            users = User.query.all()
            parcels = []
            
            test_parcels = [
                {"description": "Electronics package", "pickup": "Nairobi CBD", "destination": "Thika Town", "weight": 2.5, "status": "pending"},
                {"description": "Food delivery", "pickup": "Westlands", "destination": "Kilimani", "weight": 1.2, "status": "in_transit"},
                {"description": "Documents", "pickup": "Mombasa", "destination": "Nairobi", "weight": 0.5, "status": "delivered"}
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
            
            # Add random parcels
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
            
            # Create history
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
            
            return {
                'message': 'Database seeded successfully!',
                'summary': {
                    'users': User.query.count(),
                    'parcels': Parcel.query.count(),
                    'history': ParcelHistory.query.count(),
                    'admins': User.query.filter_by(admin=True).count()
                },
                'login': {
                    'email': 'brianinesh@gmail.com',
                    'password': 'password123',
                    'status': 'ADMIN'
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500 