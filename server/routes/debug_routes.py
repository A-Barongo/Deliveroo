"""Debug routes for checking database."""
from flask import jsonify, request
from flask_restful import Resource
from server.models import User
from server.config import db

class DebugUsers(Resource):
    """Debug endpoint to check users in database."""
    
    def get(self):
        """Get all users (for debugging)."""
        try:
            users = User.query.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'admin': user.admin
                })
            
            return {
                'total_users': len(user_list),
                'admin_users': len([u for u in user_list if u['admin']]),
                'users': user_list
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class MakeAdmin(Resource):
    """Debug endpoint to make a user admin."""
    
    def post(self):
        """Make a user admin by email."""
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return {'error': 'Email is required'}, 400
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return {'error': f'User with email {email} not found'}, 404
            
            if user.admin:
                return {'message': f'User {email} is already an admin'}, 200
            
            user.admin = True
            db.session.commit()
            
            return {
                'message': f'Successfully made {email} an admin',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'admin': user.admin
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500 