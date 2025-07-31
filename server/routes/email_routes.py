"""Email routes for Deliveroo app."""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flasgger import swag_from
from server.models import User, Parcel
from server.services.sendgrid_service import SendGridService

# Initialize SendGrid service
sendgrid_service = SendGridService()

class EmailPreferences(Resource):
    """Handle email preferences for users."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Get email preferences',
        'description': 'Get email preferences for a specific user.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'User ID'
            }
        ],
        'responses': {
            200: {
                'description': 'Email preferences retrieved successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'parcel_created': {'type': 'boolean'},
                                'status_updates': {'type': 'boolean'},
                                'location_updates': {'type': 'boolean'},
                                'parcel_cancelled': {'type': 'boolean'},
                                'welcome_emails': {'type': 'boolean'}
                            }
                        }
                    }
                }
            },
            404: {'description': 'User not found'}
        }
    })
    @jwt_required()
    def get(self, user_id):
        """Get email preferences for a user."""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        
        # Return default preferences (all enabled)
        preferences = {
            "parcel_created": True,
            "status_updates": True,
            "location_updates": True,
            "parcel_cancelled": True,
            "welcome_emails": True
        }
        
        return preferences, 200

    @swag_from({
        'tags': ['Email'],
        'summary': 'Update email preferences',
        'description': 'Update email preferences for a specific user.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'User ID'
            }
        ],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'parcel_created': {'type': 'boolean'},
                            'status_updates': {'type': 'boolean'},
                            'location_updates': {'type': 'boolean'},
                            'parcel_cancelled': {'type': 'boolean'},
                            'welcome_emails': {'type': 'boolean'}
                        }
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email preferences updated successfully'},
            404: {'description': 'User not found'}
        }
    })
    @jwt_required()
    def put(self, user_id):
        """Update email preferences for a user."""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        
        data = request.get_json()
        
        # For now, just return success (in a real app, you'd save to database)
        return {"message": "Email preferences updated successfully"}, 200

class EmailParcelCreated(Resource):
    """Send email when parcel is created."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send parcel created email',
        'description': 'Send email notification when a parcel is created.',
        'security': [{'BearerAuth': []}],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'parcel_id': {'type': 'integer'},
                            'user_email': {'type': 'string'}
                        },
                        'required': ['parcel_id', 'user_email']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'},
            404: {'description': 'Parcel not found'}
        }
    })
    @jwt_required()
    def post(self):
        data = request.get_json()
        parcel_id = data.get('parcel_id')
        user_email = data.get('user_email')
        
        if not parcel_id or not user_email:
            return {"error": "Missing parcel_id or user_email"}, 400
        
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        
        try:
            # Get user details for email
            user = User.query.get(current_user_id)
            username = user.username if user else "User"
            
            # Send email using SendGrid
            success = sendgrid_service.send_parcel_created_email(user_email, parcel.to_dict(), username)
            
            if success:
                return {"message": "Parcel created email sent successfully"}, 200
            else:
                return {"error": "Failed to send email via SendGrid"}, 500
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailStatusUpdate(Resource):
    """Send email when parcel status is updated."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send status update email',
        'description': 'Send email notification when parcel status is updated.',
        'security': [{'BearerAuth': []}],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'parcel_id': {'type': 'integer'},
                            'user_email': {'type': 'string'},
                            'old_status': {'type': 'string'},
                            'new_status': {'type': 'string'}
                        },
                        'required': ['parcel_id', 'user_email', 'old_status', 'new_status']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'},
            404: {'description': 'Parcel not found'}
        }
    })
    @jwt_required()
    def post(self):
        data = request.get_json()
        parcel_id = data.get('parcel_id')
        user_email = data.get('user_email')
        old_status = data.get('old_status')
        new_status = data.get('new_status')
        
        if not all([parcel_id, user_email, old_status, new_status]):
            return {"error": "Missing required fields"}, 400
        
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        
        try:
            # Send email using SendGrid
            success = sendgrid_service.send_status_update_email(user_email, parcel.to_dict(), old_status, new_status)
            
            if success:
                return {"message": "Status update email sent successfully"}, 200
            else:
                return {"error": "Failed to send email via SendGrid"}, 500
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailLocationUpdate(Resource):
    """Send email when parcel location is updated."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send location update email',
        'description': 'Send email notification when parcel location is updated.',
        'security': [{'BearerAuth': []}],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'parcel_id': {'type': 'integer'},
                            'user_email': {'type': 'string'},
                            'new_location': {'type': 'string'}
                        },
                        'required': ['parcel_id', 'user_email', 'new_location']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'},
            404: {'description': 'Parcel not found'}
        }
    })
    @jwt_required()
    def post(self):
        data = request.get_json()
        parcel_id = data.get('parcel_id')
        user_email = data.get('user_email')
        new_location = data.get('new_location')
        
        if not all([parcel_id, user_email, new_location]):
            return {"error": "Missing required fields"}, 400
        
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        
        try:
            send_location_update_email(user_email, parcel.to_dict(), new_location)
            return {"message": "Location update email sent successfully"}, 200
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailParcelCancelled(Resource):
    """Send email when parcel is cancelled."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send parcel cancelled email',
        'description': 'Send email notification when a parcel is cancelled.',
        'security': [{'BearerAuth': []}],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'parcel_id': {'type': 'integer'},
                            'user_email': {'type': 'string'}
                        },
                        'required': ['parcel_id', 'user_email']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'},
            404: {'description': 'Parcel not found'}
        }
    })
    @jwt_required()
    def post(self):
        data = request.get_json()
        parcel_id = data.get('parcel_id')
        user_email = data.get('user_email')
        
        if not parcel_id or not user_email:
            return {"error": "Missing parcel_id or user_email"}, 400
        
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        
        try:
            send_parcel_cancelled_email(user_email, parcel.to_dict())
            return {"message": "Parcel cancelled email sent successfully"}, 200
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailWelcome(Resource):
    """Send welcome email to new users."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send welcome email',
        'description': 'Send welcome email to new users.',
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'user_email': {'type': 'string'},
                            'username': {'type': 'string'}
                        },
                        'required': ['user_email', 'username']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'}
        }
    })
    def post(self):
        data = request.get_json()
        user_email = data.get('user_email')
        username = data.get('username')
        
        if not user_email or not username:
            return {"error": "Missing user_email or username"}, 400
        
        try:
            send_welcome_email(user_email, username)
            return {"message": "Welcome email sent successfully"}, 200
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailPasswordReset(Resource):
    """Send password reset email."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send password reset email',
        'description': 'Send password reset email to user.',
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'user_email': {'type': 'string'},
                            'reset_token': {'type': 'string'}
                        },
                        'required': ['user_email', 'reset_token']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Email sent successfully'},
            400: {'description': 'Missing required fields'}
        }
    })
    def post(self):
        data = request.get_json()
        user_email = data.get('user_email')
        reset_token = data.get('reset_token')
        
        if not user_email or not reset_token:
            return {"error": "Missing user_email or reset_token"}, 400
        
        try:
            send_password_reset_email(user_email, reset_token)
            return {"message": "Password reset email sent successfully"}, 200
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500

class EmailTest(Resource):
    """Send test email."""
    
    @swag_from({
        'tags': ['Email'],
        'summary': 'Send test email',
        'description': 'Send test email to verify email configuration.',
        'security': [{'BearerAuth': []}],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'user_email': {'type': 'string'}
                        },
                        'required': ['user_email']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Test email sent successfully'},
            400: {'description': 'Missing user_email'},
            429: {'description': 'Rate limit exceeded'}
        }
    })
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_email = data.get('user_email')
        
        if not user_email:
            return {"error": "Missing user_email"}, 400
        
        try:
            # Send test email using SendGrid
            success = sendgrid_service.send_test_email(user_email)
            
            if success:
                return {"message": "Test email sent successfully"}, 200
            else:
                return {"error": "Failed to send test email via SendGrid"}, 500
        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}, 500 