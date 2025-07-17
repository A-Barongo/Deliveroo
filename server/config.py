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

# 1. App init
app = Flask(__name__)

# 2. Config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:////home/prizrak917/MORINGA/phase-5/Deliveroo/server/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-jwt-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

# app.json.compact = False  # Removed due to linter error

# 3. Extensions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


db = SQLAlchemy(metadata=metadata)
db.init_app(app)
migrate = Migrate(app, db)


bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)
CORS(app, supports_credentials=True)

# 4. Token blacklist setup
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in blacklist
