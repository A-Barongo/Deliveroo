"""Profile and authentication routes for Deliveroo API."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from server.models import User
from server.config import blacklist, db
from sqlalchemy.exc import IntegrityError

class Signup(Resource):
    """Resource for user signup."""
    def post(self):
        """Register a new user."""
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                admin=data.get('admin', False),
                phone_number=data['phone_number']
            )
            user.password = data['password']
            db.session.add(user)
            db.session.commit()
            access_token = create_access_token(identity=user.id)
            return {
                "user": user.to_dict(),
                "access_token": access_token
            }, 201
        except (KeyError, ValueError, IntegrityError) as e:
            db.session.rollback()
            print(str(e))
            return {'error': 'Signup failed'}, 422

class Login(Resource):
    """Resource for user login."""
    def post(self):
        """Authenticate user and return JWT token if valid."""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return {'error': 'Missing credentials'}, 400
        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            access_token = create_access_token(identity=user.id)
            return {
                "user": user.to_dict(),
                "access_token": access_token
            }, 200
        return {'error': 'Unauthorized'}, 401

class Profile(Resource):
    """Resource for user profile."""
    @jwt_required()
    def get(self):
        """Get the current user's profile."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return user.to_dict(), 200
        return {'error': 'User not found'}, 404

class Logout(Resource):
    """Resource for user logout."""
    @jwt_required()
    def post(self):
        """Logout the current user by blacklisting their JWT."""
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        return {"message": "Successfully logged out"}, 200