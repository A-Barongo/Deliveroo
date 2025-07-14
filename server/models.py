from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.types import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from config import  bcrypt,db

class User(db.Model,SerializerMixin):
    pass
class Parcel(db.Model,SerializerMixin):
    pass
class ParcelHistory(db.Model,SerializerMixin):
    pass