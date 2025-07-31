"""Admin routes for Deliveroo app."""

from datetime import datetime, timezone
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from server.config import db
from server.models import Parcel, User, ParcelHistory
from server.services.sendgrid_service import SendGridService

# Initialize SendGrid service
sendgrid_service = SendGridService()

# Utility to get current logged-in user
def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

# Admin role enforcement
def admin_required(func):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.admin:
            return {"error": "Admin access required"}, 403
        return func(*args, **kwargs, current_user=user)
    wrapper.__name__ = func.__name__
    return wrapper

class AdminParcelList(Resource):
    """Resource for listing all parcels (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'List all parcels',
        'description': 'Returns a list of all parcels. Admin access only.',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'List of all parcels',
                'content': {'application/json': {}}
            },
            403: {'description': 'Unauthorized (non-admin)'}
        }
    })
    @admin_required
    def get(self, current_user):
        parcels = Parcel.query.all()
        return jsonify([p.to_dict() for p in parcels])

class AdminParcelDetail(Resource):
    """Get a specific parcel by ID (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'Get parcel by ID',
        'description': 'Returns parcel details for a given ID. Admin access only.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'name': 'parcel_id',
                'in': 'path',
                'required': True,
                'schema': {'type': 'integer'}
            }
        ],
        'responses': {
            200: {
                'description': 'Parcel details',
                'content': {'application/json': {}}
            },
            404: {'description': 'Parcel not found'},
            403: {'description': 'Unauthorized'}
        }
    })
    @admin_required
    def get(self, current_user, parcel_id):
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {'message': 'Parcel not found'}, 404
        return jsonify(parcel.to_dict())

class UpdateParcelStatus(Resource):
    """Resource for updating parcel status (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'Update parcel status',
        'description': 'Allows admin to update the status of a parcel.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'in': 'path',
                'name': 'parcel_id',
                'required': True,
                'schema': {'type': 'integer'}
            }
        ],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string', 'example': 'in transit'}
                        },
                        'required': ['status']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Parcel status updated'},
            400: {'description': 'Status field is required'},
            403: {'description': 'Unauthorized (non-admin)'},
            404: {'description': 'Parcel not found'}
        }
    })
    @admin_required
    def patch(self, id, current_user):
        parcel = Parcel.query.get(id)
        if not parcel:
            return {"error": "Parcel not found"}, 404

        data = request.get_json()
        new_status = data.get("status")
        if not new_status:
            return {"error": "Status field is required"}, 400

        old_status = parcel.status
        parcel.status = new_status
        parcel.updated_at = datetime.now(timezone.utc)
        db.session.add(parcel)

        history = ParcelHistory(
            parcel_id=parcel.id,
            updated_by=current_user.id,
            update_type="status",
            old_value=old_status,
            new_value=new_status
        )
        db.session.add(history)
        db.session.commit()
        
        # Send status update email
        try:
            user = User.query.get(parcel.user_id)
            if user:
                sendgrid_service.send_status_update_email(user.email, parcel.to_dict(), old_status, new_status)
        except Exception as e:
            # Log the error but don't fail status update
            print(f"Failed to send status update email: {str(e)}")

        return {"message": "Parcel status updated", "parcel": parcel.to_dict()}, 200

class UpdateParcelLocation(Resource):
    """Resource for updating parcel location (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'Update parcel location',
        'description': 'Allows admin to update the current location of a parcel.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'in': 'path',
                'name': 'parcel_id',
                'required': True,
                'schema': {'type': 'integer'}
            }
        ],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'current_location': {'type': 'string', 'example': 'Nairobi Hub'}
                        },
                        'required': ['current_location']
                    }
                }
            }
        },
        'responses': {
            200: {'description': 'Parcel location updated'},
            400: {'description': 'current_location is required'},
            403: {'description': 'Unauthorized (non-admin)'},
            404: {'description': 'Parcel not found'}
        }
    })
    @admin_required
    def patch(self, id, current_user):
        parcel = Parcel.query.get(id)
        if not parcel:
            return {"error": "Parcel not found"}, 404

        data = request.get_json()
        new_location = data.get("current_location")
        if not new_location:
            return {"error": "current_location is required"}, 400

        old_location = parcel.current_location
        parcel.current_location = new_location
        parcel.updated_at = datetime.now(timezone.utc)
        db.session.add(parcel)

        history = ParcelHistory(
            parcel_id=parcel.id,
            updated_by=current_user.id,
            update_type="location",
            old_value=old_location,
            new_value=new_location
        )
        db.session.add(history)
        db.session.commit()
        
        # Send location update email
        try:
            user = User.query.get(parcel.user_id)
            if user:
                sendgrid_service.send_location_update_email(user.email, parcel.to_dict(), old_location, new_location)
        except Exception as e:
            # Log the error but don't fail location update
            print(f"Failed to send location update email: {str(e)}")

        return {"message": "Parcel location updated", "parcel": parcel.to_dict()}, 200

class ParcelHistoryList(Resource):
    """Resource for listing all parcel histories (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'List all parcel histories',
        'description': 'Returns a list of all parcel update history records.',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {'description': 'List of parcel history records'},
            403: {'description': 'Unauthorized (non-admin)'}
        }
    })
    @admin_required
    def get(self, current_user):
        histories = ParcelHistory.query.all()
        return jsonify([h.to_dict() for h in histories])

class ParcelHistoryDetail(Resource):
    """Resource for getting a specific parcel history (admin only)."""

    @swag_from({
        'tags': ['Admin'],
        'summary': 'Get parcel history detail',
        'description': 'Fetch a specific parcel history record by ID.',
        'security': [{'BearerAuth': []}],
        'parameters': [
            {
                'in': 'path',
                'name': 'history_id',
                'required': True,
                'schema': {'type': 'integer'}
            }
        ],
        'responses': {
            200: {'description': 'Parcel history record found'},
            403: {'description': 'Unauthorized (non-admin)'},
            404: {'description': 'History not found'}
        }
    })
    @admin_required
    def get(self, history_id, current_user):
        history = ParcelHistory.query.get(history_id)
        if not history:
            return {"error": "History not found"}, 404
        return jsonify(history.to_dict())

