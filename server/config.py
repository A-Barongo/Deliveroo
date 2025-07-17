import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# 1. Extensions (not bound to app yet)
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
api = Api()

blacklist = set()

# 2. App factory
def create_app(test_config=None):
    app = Flask(__name__)

    # Default config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/prizrak917/MORINGA/phase-5/Deliveroo/server/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-jwt-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    CORS(app, supports_credentials=True)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklist

    return app
