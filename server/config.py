import os
from datetime import timedelta
from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flasgger import Swagger
from flask_mail import Mail  

load_dotenv()

# 1. Extensions (not bound to app yet)
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

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
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    # For CORS preflight/headers
    app.config['CORS_HEADERS'] = 'Content-Type,Authorization'

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Import models *after* db is initialized to avoid circular import
    from server import models  # noqa: F401

    # ---- CORS configuration ----
    origins_env = os.getenv("CORS_ORIGINS")
    if origins_env:
        allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    else:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "https://deliveroo-server.onrender.com",
            "https://your-frontend-domain.com"
        ]

    # CORS configuration for development and production
    CORS(app, 
         supports_credentials=True,
         origins="*",  # Allow all origins temporarily for debugging
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type", "Authorization"]
    )

    # Add CORS preflight handler
    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses."""
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Add OPTIONS route handler for preflight requests
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        """Handle OPTIONS requests for CORS preflight."""
        response = app.make_default_options_response()
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

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
    from server.routes.profile import Signup, Register, Logout, Profile, Home
    from server.routes.auth_routes import Login
    from server.routes.admin_routes import (
        AdminParcelList, UpdateParcelStatus, UpdateParcelLocation,
        ParcelHistoryList, ParcelHistoryDetail, AdminParcelDetail
    )
    from server.routes.parcels import ParcelList, ParcelResource, ParcelCancel, ParcelDestination, ParcelStatus
    from server.routes.email_routes import (
        EmailParcelCreated, EmailStatusUpdate, EmailLocationUpdate,
        EmailParcelCancelled, EmailWelcome, EmailPasswordReset, EmailTest,
        EmailPreferences
    )

    api.add_resource(Home, '/')
    api.add_resource(Signup, '/signup')
    api.add_resource(Register, '/register')  # Frontend compatibility
    api.add_resource(Login, '/login')
    api.add_resource(Logout, '/logout')
    api.add_resource(Profile, '/profile')
    api.add_resource(AdminParcelList, '/admin/parcels')
    api.add_resource(AdminParcelDetail, '/admin/parcels/<int:parcel_id>')
    api.add_resource(UpdateParcelStatus, '/admin/parcels/<int:id>/status')
    api.add_resource(UpdateParcelLocation, '/admin/parcels/<int:id>/location')
    api.add_resource(ParcelHistoryList, '/admin/histories')
    api.add_resource(ParcelHistoryDetail, '/admin/histories/<int:id>')
    api.add_resource(ParcelList, '/parcels')
    api.add_resource(ParcelResource, '/parcels/<int:parcel_id>')
    api.add_resource(ParcelCancel, '/parcels/<int:parcel_id>/cancel')
    api.add_resource(ParcelDestination, '/parcels/<int:parcel_id>/destination')
    api.add_resource(ParcelStatus, '/parcels/<int:parcel_id>/status')

    # Email routes
    api.add_resource(EmailParcelCreated, '/email/parcel-created')
    api.add_resource(EmailStatusUpdate, '/email/status-update')
    api.add_resource(EmailLocationUpdate, '/email/location-update')
    api.add_resource(EmailParcelCancelled, '/email/parcel-cancelled')
    api.add_resource(EmailWelcome, '/email/welcome')
    api.add_resource(EmailPasswordReset, '/email/password-reset')
    api.add_resource(EmailTest, '/email/test')
    api.add_resource(EmailPreferences, '/email/preferences/<int:user_id>')
    
    print("After registering API resources")

    return app
