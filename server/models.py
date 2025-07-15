from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Parcel(Base):
    __tablename__ = 'parcels'
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    weight = Column(Float)
    status = Column(String(32), default='pending')
    sender_name = Column(String(64))
    sender_phone_number = Column(String(32))
    pickup_location_text = Column(String(255))
    destination_location_text = Column(String(255))
    pick_up_longitude = Column(Float)
    pick_up_latitude = Column(Float)
    destination_longitude = Column(Float)
    destination_latitude = Column(Float)
    current_location_longitude = Column(Float)
    current_location_latitude = Column(Float)
    distance = Column(Float)
    cost = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    recipient_name = Column(String(64))
    recipient_phone_number = Column(String(32))
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='parcels')
    courier = relationship('Courier', back_populates='parcels')
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    parcels = relationship('Parcel', back_populates='user')
class Courier(Base):
    __tablename__ = 'couriers'
    id = Column(Integer, primary_key=True)
    parcels = relationship('Parcel', back_populates='courier')
