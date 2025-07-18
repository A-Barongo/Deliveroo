"""Configuration and app factory for Deliveroo Flask app."""
import os
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flasgger import Swagger  # ✅ NEW

load_dotenv()

# 1. Extensions (not bound to app yet)
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

blacklist = set()

# Swagger config (optional, can be customized)
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Deliveroo API",
        "description": "API documentation for the Deliveroo courier system.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http", "https"],
}

# 2. App factory
def create_app(test_config=None):
    """Application factory for Flask app."""
    app = Flask(__name__)

    # Default config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # Initialize Swagger ✅
    Swagger(app, template=swagger_template)

    # Register Flask-Restful API
    api = Api(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if JWT token is revoked."""
        return jwt_payload['jti'] in blacklist

    print("Before registering API resources")
    # Register API resources
    from server.routes.profile import Signup, Logout, Profile
    from server.routes.auth_routes import Login
    from server.routes.admin_routes import (
        AdminParcelList, UpdateParcelStatus, UpdateParcelLocation,
        ParcelHistoryList, ParcelHistoryDetail
    )
    from server.routes.parcels import ParcelList, ParcelResource, ParcelCancel, ParcelDestination, ParcelStatus

    api.add_resource(Signup, '/signup')
    api.add_resource(Login, '/login')
    api.add_resource(Logout, '/logout')
    api.add_resource(Profile, '/profile')
    api.add_resource(AdminParcelList, '/admin/parcels')
    api.add_resource(UpdateParcelStatus, '/admin/parcels/<int:id>/status')
    api.add_resource(UpdateParcelLocation, '/admin/parcels/<int:id>/location')
    api.add_resource(ParcelHistoryList, '/admin/histories')
    api.add_resource(ParcelHistoryDetail, '/admin/histories/<int:id>')
    api.add_resource(ParcelList, '/parcels')
    api.add_resource(ParcelResource, '/parcels/<int:parcel_id>')
    api.add_resource(ParcelCancel, '/parcels/<int:parcel_id>/cancel')
    api.add_resource(ParcelDestination, '/parcels/<int:parcel_id>/destination')
    api.add_resource(ParcelStatus, '/parcels/<int:parcel_id>/status')
    print("After registering API resources")

    return app
