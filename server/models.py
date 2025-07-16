# this file has the database tables for the app
# we use sqlalchemy to make tables

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base

# make base for models
Base = declarative_base()

# this is the parcel table
class Parcel(Base):
    __tablename__ = 'parcels' # table name is parcels
    id = Column(Integer, primary_key=True) # id for parcel
    description = Column(String(255)) # what is in the parcel
    weight = Column(Float) # how heavy
    status = Column(String(32), default='pending') # status like pending or delivered
    sender_name = Column(String(64)) # who sends
    sender_phone_number = Column(String(32)) # sender phone
    pickup_location_text = Column(String(255)) # where to pick up
    destination_location_text = Column(String(255)) # where to deliver
    pick_up_longitude = Column(Float) # pickup longitude
    pick_up_latitude = Column(Float) # pickup latitude
    destination_longitude = Column(Float) # destination longitude
    destination_latitude = Column(Float) # destination latitude
    current_location_longitude = Column(Float) # where is parcel now longitude
    current_location_latitude = Column(Float) # where is parcel now latitude
    distance = Column(Float) # how far
    cost = Column(Float) # how much to deliver
    created_at = Column(DateTime, server_default=func.now()) # when made
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # when changed
    recipient_name = Column(String(64)) # who gets parcel
    recipient_phone_number = Column(String(32)) # recipient phone
    courier_id = Column(Integer, ForeignKey('couriers.id')) # who delivers
    user_id = Column(Integer, ForeignKey('users.id')) # who owns parcel

    user = relationship('User', back_populates='parcels') # link to user
    courier = relationship('Courier', back_populates='parcels') # link to courier

# this is the user table
class User(Base):
    __tablename__ = 'users' # table name is users
    id = Column(Integer, primary_key=True) # id for user
    parcels = relationship('Parcel', back_populates='user') # user has parcels

# this is the courier table
class Courier(Base):
    __tablename__ = 'couriers' # table name is couriers
    id = Column(Integer, primary_key=True) # id for courier
    parcels = relationship('Parcel', back_populates='courier') # courier has parcels
