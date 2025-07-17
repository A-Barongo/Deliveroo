"""Parcel routes for Deliveroo app."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import Parcel
from server.config import db

class ParcelList(Resource):
    """Resource for listing and creating parcels."""
    def get(self):
        """Get a paginated list of parcels."""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = db.session.query(Parcel)
        total = query.count()
        parcels = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            "parcels": [p.to_dict() for p in parcels],
            "page": page,
            "per_page": per_page,
            "total": total
        }, 200

    def post(self):
        """Create a new parcel."""
        data = request.get_json()
        try:
            parcel = Parcel(**data)
            db.session.add(parcel)
            db.session.commit()
            return parcel.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class ParcelResource(Resource):
    """Resource for getting a single parcel."""
    def get(self, parcel_id):
        """Get a parcel by its ID."""
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        return parcel.to_dict(), 200

class ParcelCancel(Resource):
    """Resource for cancelling a parcel."""
    @jwt_required()
    def patch(self, parcel_id):
        """Cancel a parcel if the user is the owner and it's pending."""
        current_user_id = get_jwt_identity()
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        if parcel.user_id != current_user_id:
            return {"error": "You can only cancel parcels you created"}, 403

        if parcel.status== 'delivered':
            return {"error": "Parcel cannot be cancelled after delivery"}, 400

        parcel.status = 'cancelled'
        db.session.commit()
        return parcel.to_dict(), 200

class ParcelDestination(Resource):
    """Resource for updating parcel destination."""
    def patch(self, parcel_id):
        """Update the destination of a parcel."""
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        if parcel.status == 'delivered':
            return {"error": "Parcel destination cannot be changed after delivery"}, 400
        data = request.get_json()
        for field in ["destination_location_text", "destination_longitude", "destination_latitude"]:
            if field in data:
                setattr(parcel, field, data[field])
        db.session.commit()
        return parcel.to_dict(), 200

class ParcelStatus(Resource):
    """Resource for updating parcel status."""
    def patch(self, parcel_id):
        """Update the status of a parcel."""
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        data = request.get_json()
        new_status = data.get('status')
        if not new_status:
            return {"error": "missing status field"}, 400
        parcel.status = new_status
        db.session.commit()
        return parcel.to_dict(), 200 