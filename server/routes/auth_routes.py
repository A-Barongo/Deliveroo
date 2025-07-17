"""Authentication routes for Deliveroo API."""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from server.models import User

class Login(Resource):
    """Login resource for user authentication."""
    def post(self):
        """Authenticate user and return JWT token if valid."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password): 
            token = create_access_token(identity=user.id)
            return jsonify(access_token=token)

        return jsonify({"error": "Invalid credentials"}), 401
