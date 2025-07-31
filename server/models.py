"""SQLAlchemy models for Deliveroo app."""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from server.config import db

class User(db.Model):
    """User model for Deliveroo app."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    longitude_hash = db.Column(db.Text)
    latitude_hash = db.Column(db.Text)
    _password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    @validates('email')
    def validate_email(self, key, value):
        """Validate that the email contains '@' and ends with '.com'."""
        if '@' not in value or not value.endswith('.com'):
            raise ValueError("Email must contain '@' and end with '.com'")
        return value

    @hybrid_property
    def password(self):
        """Prevent viewing the password hash."""
        raise Exception('Password hashes may not be viewed.')

    @password.setter
    def password(self, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        from server.config import bcrypt
        hashed = bcrypt.generate_password_hash(value.encode('utf-8'))
        self._password = hashed.decode('utf-8')

    def authenticate(self, password):
        from server.config import bcrypt
        return bcrypt.check_password_hash(self._password, password.encode('utf-8'))

    def to_dict(self):
        """Return a dictionary representation of the user."""
        result = {}
        for c in self.__mapper__.c:  
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                result[c.name] = value.isoformat()
            else:
                result[c.name] = value
        return result

class Parcel(db.Model):
    """Parcel model for Deliveroo app."""
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    weight = db.Column(db.Float)
    status = db.Column(db.String(32), default='pending')
    sender_name = db.Column(db.String(64))
    sender_phone_number = db.Column(db.String(32))
    pickup_location_text = db.Column(db.String(255))
    destination_location_text = db.Column(db.String(255))
    pick_up_longitude = db.Column(db.Float)
    pick_up_latitude = db.Column(db.Float)
    destination_longitude = db.Column(db.Float)
    destination_latitude = db.Column(db.Float)
    current_location = db.Column(db.String)
    current_location_longitude = db.Column(db.Float)
    current_location_latitude = db.Column(db.Float)
    distance = db.Column(db.Float)
    cost = db.Column(db.Float)
    estimated_delivery = db.Column(db.DateTime)
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    map_position = db.Column(db.Text)  # JSON string for lat/lng
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    recipient_name = db.Column(db.String(64))
    recipient_phone_number = db.Column(db.String(32))
    courier_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='parcels')

    def to_dict(self):
        """Return a dictionary representation of the parcel."""
        result = {}
        for c in self.__mapper__.c:  # type: ignore
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                result[c.name] = value.isoformat()
            else:
                result[c.name] = value
        return result

    def calculate_cost(self):
        """Calculate cost for the parcel."""
        if self.weight is not None:
            return self.weight * 150
        return 0

class ParcelHistory(db.Model):
    """Parcel history model for Deliveroo app."""
    __tablename__ = 'parcel_histories'

    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    update_type = db.Column(db.String, nullable=False)
    old_value = db.Column(db.String)
    new_value = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    user = db.relationship('User', backref='history_updates')
    parcel = db.relationship('Parcel', backref='history')

    def to_dict(self):
        """Return a dictionary representation of the parcel history."""
        return {
            "id": self.id,
            "parcel_id": self.parcel_id,
            "updated_by": self.updated_by,
            "update_type": self.update_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
