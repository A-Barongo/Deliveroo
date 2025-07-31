"""Tracking routes for real-time parcel tracking."""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from server.models import Parcel, User
from server.services.tracking_service import tracking_service
from datetime import datetime

class StartTracking(Resource):
    """Start real-time tracking for a parcel."""
    
    @swag_from({
        'tags': ['Tracking'],
        'summary': 'Start tracking a parcel',
        'description': 'Start real-time tracking simulation for a parcel.',
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
            200: {'description': 'Tracking started successfully'},
            404: {'description': 'Parcel not found'},
            403: {'description': 'Unauthorized'}
        }
    })
    @jwt_required()
    def post(self, parcel_id):
        """Start tracking a parcel."""
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)
        
        if not parcel:
            return {"error": "Parcel not found"}, 404
            
        if parcel.user_id != current_user_id:
            return {"error": "Unauthorized access"}, 403
            
        # Start tracking
        tracking_service.start_tracking(parcel_id)
        
        return {
            "message": "Tracking started successfully",
            "parcel_id": parcel_id,
            "status": "tracking_active"
        }, 200

class GetTrackingInfo(Resource):
    """Get current tracking information for a parcel."""
    
    @swag_from({
        'tags': ['Tracking'],
        'summary': 'Get tracking information',
        'description': 'Get real-time tracking information for a parcel.',
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
            200: {'description': 'Tracking information retrieved'},
            404: {'description': 'Parcel not found'},
            403: {'description': 'Unauthorized'}
        }
    })
    @jwt_required()
    def get(self, parcel_id):
        """Get tracking information for a parcel."""
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)
        
        if not parcel:
            return {"error": "Parcel not found"}, 404
            
        if parcel.user_id != current_user_id:
            return {"error": "Unauthorized access"}, 403
            
        # Get tracking information
        tracking_info = tracking_service.get_tracking_info(parcel_id)
        
        return {
            "tracking_info": tracking_info,
            "parcel": parcel.to_dict()
        }, 200

class StopTracking(Resource):
    """Stop tracking a parcel."""
    
    @swag_from({
        'tags': ['Tracking'],
        'summary': 'Stop tracking a parcel',
        'description': 'Stop real-time tracking for a parcel.',
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
            200: {'description': 'Tracking stopped successfully'},
            404: {'description': 'Parcel not found'},
            403: {'description': 'Unauthorized'}
        }
    })
    @jwt_required()
    def post(self, parcel_id):
        """Stop tracking a parcel."""
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)
        
        if not parcel:
            return {"error": "Parcel not found"}, 404
            
        if parcel.user_id != current_user_id:
            return {"error": "Unauthorized access"}, 403
            
        # Stop tracking
        tracking_service.stop_tracking(parcel_id)
        
        return {
            "message": "Tracking stopped successfully",
            "parcel_id": parcel_id,
            "status": "tracking_stopped"
        }, 200

class LiveTracking(Resource):
    """Get live tracking updates (for WebSocket-like experience)."""
    
    @swag_from({
        'tags': ['Tracking'],
        'summary': 'Get live tracking updates',
        'description': 'Get live tracking updates for real-time display.',
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
            200: {'description': 'Live tracking data'},
            404: {'description': 'Parcel not found'},
            403: {'description': 'Unauthorized'}
        }
    })
    @jwt_required()
    def get(self, parcel_id):
        """Get live tracking updates."""
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)
        
        if not parcel:
            return {"error": "Parcel not found"}, 404
            
        if parcel.user_id != current_user_id:
            return {"error": "Unauthorized access"}, 403
            
        # Get current tracking info
        tracking_info = tracking_service.get_tracking_info(parcel_id)
        
        # Add live tracking data
        live_data = {
            "parcel_id": parcel_id,
            "current_location": parcel.current_location,
            "status": parcel.status,
            "estimated_delivery": tracking_info.get('estimated_delivery'),
            "is_tracking": tracking_info.get('is_tracking', False),
            "last_updated": parcel.updated_at.isoformat() if parcel.updated_at else None,
            "timestamp": datetime.now().isoformat(),
            "tracking_active": parcel_id in tracking_service.tracking_threads
        }
        
        return {"live_tracking": live_data}, 200 