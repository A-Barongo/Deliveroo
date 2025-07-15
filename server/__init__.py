from flask import Flask, g, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .routes import parcels_bp
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///deliveroo.db')

def create_app():
    app = Flask(__name__)
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    @app.before_request
    def before_request():
        g.db_session = SessionLocal()
        request.environ['db_session'] = g.db_session

    @app.teardown_request
    def teardown_request(exception=None):
        db = g.pop('db_session', None)
        if db is not None:
            db.close()

    app.register_blueprint(parcels_bp)
    return app
