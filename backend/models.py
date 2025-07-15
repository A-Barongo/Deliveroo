from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Parcel(Base):
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    description = Column(String(255))
    status = Column(String(32), nullable=False, default='pending')
    sender_phone_number = Column(String(32), nullable=False)
    sender_name = Column(String(64), nullable=False)
    recipient_phone_number = Column(String(32), nullable=False)
    recipient_name = Column(String(64), nullable=False)
    pickup_location_text = Column(String(255), nullable=False)
    destination_location_text = Column(String(255), nullable=False)
    pick_up_longitude = Column(Float, nullable=True)
    pick_up_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)
    destination_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)
    location_latitude = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)  # in minutes or seconds
    distance = Column(Float, nullable=True)  # in km or meters
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='parcels')

    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight,
            'description': self.description,
            'status': self.status,
            'sender_phone_number': self.sender_phone_number,
            'sender_name': self.sender_name,
            'recipient_phone_number': self.recipient_phone_number,
            'recipient_name': self.recipient_name,
            'pickup_location_text': self.pickup_location_text,
            'destination_location_text': self.destination_location_text,
            'pick_up_longitude': self.pick_up_longitude,
            'pick_up_latitude': self.pick_up_latitude,
            'destination_longitude': self.destination_longitude,
            'destination_latitude': self.destination_latitude,
            'location_longitude': self.location_longitude,
            'location_latitude': self.location_latitude,
            'duration': self.duration,
            'distance': self.distance,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    parcels = relationship('Parcel', back_populates='user') 