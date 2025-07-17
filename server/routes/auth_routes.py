from flask import request, jsonify
from flask_restful import Resource
from models import User
from flask_jwt_extended import create_access_token

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password): 
            token = create_access_token(identity=user.id)
            return jsonify(access_token=token)

        return jsonify({"error": "Invalid credentials"}), 401
