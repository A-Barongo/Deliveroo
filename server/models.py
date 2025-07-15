from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.types import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from config import  bcrypt,db
from datetime import datetime, timezone

class User(db.Model,SerializerMixin):
    __tablename__='users'
    
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String, nullable=False,unique=True)
    email=db.Column(db.String,nullable=False,unique=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    longitude_hash = db.Column(db.Text)
    latitude_hash = db.Column(db.Text)
    _password=db.Column(db.String, nullable=False)
    admin=db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
  
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value and '.com' not in value:
            raise ValueError("Email must contain '@' and end with '.com'")
        return value
    
    @hybrid_property
    def password(self):
        raise Exception('Password hashes may not be viewed.')

    @password.setter
    def password(self, password):
        hashed= bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password = hashed.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password, password.encode('utf-8'))
        
        
#class Parcel(db.Model,SerializerMixin):
 #   pass
#class ParcelHistory(db.Model,SerializerMixin):
 #   pass