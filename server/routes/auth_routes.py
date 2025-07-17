"""Authentication routes for Deliveroo app."""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from server.models import User

class Login(Resource):
    """Login resource for user authentication."""
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
