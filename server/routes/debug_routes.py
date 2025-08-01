"""Debug routes for checking database."""
from flask import jsonify
from flask_restful import Resource
from server.models import User

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