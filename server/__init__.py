# this file makes the flask app and sets up everything
# it connects to the database and adds routes

from flask import Flask, g, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .routes.parcels import parcels_bp
import os

# get database url from env right now it is sqlite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///deliveroo.db')

def create_app():
    # this makes the flask app
    app = Flask(__name__)
    engine = create_engine(DATABASE_URL) # connect to database
    Base.metadata.create_all(engine) # make tables if not there
    SessionLocal = sessionmaker(bind=engine) # make session for database

    @app.before_request
    def before_request():
        # this runs before every request
        g.db_session = SessionLocal() # make a new database session
        request.environ['db_session'] = g.db_session # save session

    @app.teardown_request
    def teardown_request(exception=None):
        # this runs after every request
        db = g.pop('db_session', None) # get the session
        if db is not None:
            db.close() # close the session

    app.register_blueprint(parcels_bp) # add parcel routes
    return app # give back the app
