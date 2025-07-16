
from config import db
from datetime import datetime, timezone

class Parcel(db.Model):
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
    user_id = db.Column(db.Integer)

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                result[c.name] = value.isoformat()
            else:
                result[c.name] = value
        return result
