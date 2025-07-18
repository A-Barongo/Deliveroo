"""Authentication routes for Deliveroo app."""

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from server.models import User
from flasgger import swag_from

class Login(Resource):
    """Login resource for user authentication."""

    @swag_from({
        'tags': ['Auth'],
        'summary': 'User login',
        'description': 'Authenticate user and return a JWT token if credentials are valid.',
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string', 'example': 'johndoe'},
                            'password': {'type': 'string', 'example': 'secret123'}
                        },
                        'required': ['username', 'password']
                    }
                }
            }
        },
        'responses': {
            200: {
                'description': 'Login successful',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'user': {'type': 'object'},
                                'access_token': {'type': 'string', 'example': 'eyJ0eXAiOiJK...'}
                            }
                        }
                    }
                }
            },
            400: {'description': 'Missing credentials'},
            401: {'description': 'Unauthorized'}
        }
    })
    def post(self):
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

