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

    def set_password(self, password):
        """Set hashed password for user."""
        self._password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self._password, password)

    def to_dict(self):
        """Return a dictionary representation of the user."""
        result = {}
        for c in self.__mapper__.c:  # type: ignore
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
    current_location_longitude = db.Column(db.Float)
    current_location_latitude = db.Column(db.Float)
    distance = db.Column(db.Float)
    cost = db.Column(db.Float)
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
