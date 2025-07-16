from flask import request, jsonify
from flask_restful import Resource
from server.config import db
from server.models import Parcel, User, ParcelHistory
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def admin_required(func):
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.admin:
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs, current_user=user)
    wrapper.__name__ = func.__name__
    return wrapper


# 1. GET /admin/parcels
class AdminParcelList(Resource):
    @admin_required
    def get(self, current_user):
        parcels = Parcel.query.all()
        return jsonify([p.to_dict() for p in parcels])

# 2. PATCH /admin/parcels/<id>/status
class UpdateParcelStatus(Resource):
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
        db.session.add(parcel)

        # Create history entry
        history = ParcelHistory(
            parcel_id=parcel.id,
            updated_by=current_user.id,
            update_type="status",
            old_value=old_status,
            new_value=new_status
        )
        db.session.add(history)
        db.session.commit()

        return {"message": "Parcel status updated", "parcel": parcel.to_dict()}, 200

# 3. PATCH /admin/parcels/<id>/location
class UpdateParcelLocation(Resource):
    @admin_required
    def patch(self, id, current_user):
        parcel = Parcel.query.get(id)
        if not parcel:
            return {"error": "Parcel not found"}, 404

        data = request.get_json()
        new_location = data.get("present_location")
        if not new_location:
            return {"error": "present_location is required"}, 400

        old_location = parcel.present_location
        parcel.present_location = new_location
        db.session.add(parcel)

        # Create history entry
        history = ParcelHistory(
            parcel_id=parcel.id,
            updated_by=current_user.id,
            update_type="location",
            old_value=old_location,
            new_value=new_location
        )
        db.session.add(history)
        db.session.commit()

        return {"message": "Parcel location updated", "parcel": parcel.to_dict()}, 200

# GET all history entries
class ParcelHistoryList(Resource):
    @admin_required
    def get(self, current_user):
        histories = ParcelHistory.query.all()
        return jsonify([h.to_dict() for h in histories])

# Optional: GET single history entry
class ParcelHistoryDetail(Resource):
    @admin_required
    def get(self, id, current_user):
        history = ParcelHistory.query.get(id)
        if not history:
            return {"error": "History not found"}, 404
        return jsonify(history.to_dict())
