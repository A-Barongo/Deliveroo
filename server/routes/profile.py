"""Profile routes for Deliveroo app."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from server.models import User
from server.config import blacklist, db
from sqlalchemy.exc import IntegrityError


class Signup(Resource):
    """Resource for user signup."""

    def post(self):
        """
        Register a new user.
        ---
        tags:
          - Auth
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                  - username
                  - email
                  - phone_number
                  - password
                properties:
                  username:
                    type: string
                    example: johndoe
                  email:
                    type: string
                    example: johndoe@example.com
                  phone_number:
                    type: string
                    example: "+1234567890"
                  password:
                    type: string
                    example: secret123
                  admin:
                    type: boolean
                    example: false
        responses:
          201:
            description: User created
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    user:
                      type: object
                    access_token:
                      type: string
          422:
            description: Signup failed (validation or conflict)
        """
        data = request.get_json()

        try:
            if User.query.filter(
                (User.username == data['username']) | (User.email == data['email'])
            ).first():
                return {"error": "Username or email already exists"}, 422

            user = User(
                username=data['username'],
                email=data['email'],
                phone_number=data['phone_number'],
                admin=data.get('admin', False)
            )
            user.password = data['password']

            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            return {
                "user": user.to_dict(),
                "access_token": access_token
            }, 201

        except (KeyError, ValueError, IntegrityError):
            db.session.rollback()
            return {'error': 'Signup failed. Please check your input.'}, 422


class Profile(Resource):
    """Resource for user profile."""

    @jwt_required()
    def get(self):
        """
        Get the current user's profile.
        ---
        tags:
          - Profile
        security:
          - BearerAuth: []
        responses:
          200:
            description: Profile retrieved successfully
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    id:
                      type: integer
                    username:
                      type: string
                    email:
                      type: string
                    phone_number:
                      type: string
                    admin:
                      type: boolean
          404:
            description: User not found
        """
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return user.to_dict(), 200
        return {'error': 'User not found'}, 404


class Logout(Resource):
    """Resource for user logout."""

    @jwt_required()
    def post(self):
        """
        Logout the current user (JWT is blacklisted).
        ---
        tags:
          - Auth
        security:
          - BearerAuth: []
        responses:
          200:
            description: Logged out successfully
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Successfully logged out
        """
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        return {"message": "Successfully logged out"}, 200

