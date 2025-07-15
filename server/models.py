from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, func, Text, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Parcel(Base):
    """
    Parcel model for delivery orders.
    Includes sender, recipient, location, status, cost, and weight details.
    """
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Float, nullable=True)
    description = Column(Text)
    status = Column(String(32), nullable=False, default='pending', index=True)
    sender_name = Column(String(64), nullable=False)
    sender_phone_number = Column(Integer, nullable=False)
    pickup_location_text = Column(String(255), nullable=False)
    destination_location_text = Column(String(255), nullable=False)
    pick_up_longitude = Column(Float)
    pick_up_latitude = Column(Float)
    destination_longitude = Column(Float)
    destination_latitude = Column(Float)
    current_location_longitude = Column(Float)
    current_location_latitude = Column(Float)
    distance = Column(Float)  # in km
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    recipient_name = Column(String(64), nullable=False)
    recipient_phone_number = Column(Integer, nullable=False)
    courier_id = Column(Integer, ForeignKey('couriers.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='parcels')
    courier = relationship('Courier', back_populates='parcels', foreign_keys=[courier_id])

    __table_args__ = (
        Index('ix_parcel_status', 'status'),
        Index('ix_parcel_sender_phone', 'sender_phone_number'),
        Index('ix_parcel_recipient_phone', 'recipient_phone_number'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status,
            'sender_name': self.sender_name,
            'sender_phone_number': self.sender_phone_number,
            'pickup_location_text': self.pickup_location_text,
            'destination_location_text': self.destination_location_text,
            'pick_up_longitude': self.pick_up_longitude,
            'pick_up_latitude': self.pick_up_latitude,
            'destination_longitude': self.destination_longitude,
            'destination_latitude': self.destination_latitude,
            'current_location_longitude': self.current_location_longitude,
            'current_location_latitude': self.current_location_latitude,
            'distance': self.distance,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'recipient_name': self.recipient_name,
            'recipient_phone_number': self.recipient_phone_number,
            'courier_id': self.courier_id,
            'user_id': self.user_id
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parcels = relationship('Parcel', back_populates='user')

class Courier(Base):
    __tablename__ = 'couriers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parcels = relationship('Parcel', back_populates='courier')
