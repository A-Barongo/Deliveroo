"""Parcel routes for Deliveroo app."""
import traceback
from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import Parcel, User
from server.config import db


def _normalize_parcel_payload(raw: dict) -> dict:
    """
    Map common frontend keys to model column names and coerce types where safe.
    This makes the API tolerant to small naming differences.
    """
    data = dict(raw or {})

    # ---- Field aliases (frontend -> model) ----
    aliases = {
        # pickup lat/lng
        "pickup_longitude": "pick_up_longitude",
        "pickup_latitude": "pick_up_latitude",
        # sometimes camelCase from forms
        "pickupLocationText": "pickup_location_text",
        "destinationLocationText": "destination_location_text",
        "receiver_name": "recipient_name",
        "receiverPhone": "recipient_phone_number",
        "receiver_phone": "recipient_phone_number",
        "senderPhone": "sender_phone_number",
        "sender_phone": "sender_phone_number",
    }

    for k_src, k_dst in aliases.items():
        if k_src in data and k_dst not in data:
            data[k_dst] = data.pop(k_src)

    # ---- Type coercions (best effort) ----
    def _to_float(x):
        try:
            return float(x) if x is not None and x != "" else None
        except Exception:
            return None

    for key in [
        "weight",
        "pick_up_longitude",
        "pick_up_latitude",
        "destination_longitude",
        "destination_latitude",
        "current_location_longitude",
        "current_location_latitude",
        "distance",
        "cost",
    ]:
        if key in data:
            data[key] = _to_float(data[key])

    # Trim strings
    for key in [
        "pickup_location_text",
        "destination_location_text",
        "sender_name",
        "sender_phone_number",
        "recipient_name",
        "recipient_phone_number",
        "description",
        "current_location",
        "status",
    ]:
        if key in data and isinstance(data[key], str):
            data[key] = data[key].strip()

    return data


class ParcelList(Resource):
    """List and create parcels."""

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        if user and user.admin:
            query = Parcel.query
        else:
            query = Parcel.query.filter_by(user_id=user_id)

        parcels = query.offset((page - 1) * per_page).limit(per_page).all()
        total = query.count()

        return {
            "parcels": [p.to_dict() for p in parcels],
            "page": page,
            "per_page": per_page,
            "total": total
        }, 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        raw = request.get_json(silent=True) or {}

        # Basic required fields (text labels)
        required_fields = ['pickup_location_text', 'destination_location_text']
        # Normalize before validation to allow alias keys
        data = _normalize_parcel_payload(raw)

        for field in required_fields:
            if not data.get(field):
                return {"error": f"Missing required field: {field}"}, 400

        try:
            # Compute cost if not provided (weight * 150)
            if data.get("cost") is None:
                w = data.get("weight")
                if isinstance(w, (int, float)):
                    data["cost"] = w * 150

            parcel = Parcel(**data, user_id=current_user_id)
            db.session.add(parcel)
            db.session.commit()

            return parcel.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            # Log detailed error to help diagnose
            current_app.logger.error("Parcel creation failed: %s", e)
            current_app.logger.error("Incoming payload (raw): %s", raw)
            current_app.logger.error("Normalized payload: %s", data)
            current_app.logger.error("Traceback:\n%s", traceback.format_exc())
            return {"error": "Parcel creation failed", "detail": str(e)}, 500


class ParcelResource(Resource):
    """Get parcel by ID."""
    @jwt_required()
    def get(self, parcel_id):
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)

        if not parcel:
            return {"error": "Parcel not found"}, 404

        if parcel.user_id != current_user_id:
            return {"error": "Unauthorized access to this parcel"}, 403

        return parcel.to_dict(), 200


class ParcelCancel(Resource):
    """Cancel a parcel."""
    @jwt_required()
    def patch(self, parcel_id):
        user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        if parcel.user_id != user_id:
            return {"error": "Not authorized"}, 403
        if parcel.status == 'delivered':
            return {"error": "Cannot cancel delivered parcel"}, 400

        parcel.status = 'cancelled'
        db.session.commit()
        return parcel.to_dict(), 200


class ParcelDestination(Resource):
    """Update parcel destination."""
    @jwt_required()
    def patch(self, parcel_id):
        current_user_id = get_jwt_identity()
        parcel = Parcel.query.get(parcel_id)

        if not parcel:
            return {"error": "Parcel not found"}, 404
        if parcel.user_id != current_user_id:
            return {"error": "Not authorized to modify this parcel"}, 403
        if parcel.status == 'delivered':
            return {"error": "Cannot update delivered parcel"}, 400

        data = request.get_json(silent=True) or {}
        data = _normalize_parcel_payload(data)

        # Accept either 'destination_location_text' or a generic 'destination'
        new_dest = data.get("destination_location_text") or data.get("destination")
        if new_dest:
            parcel.destination_location_text = new_dest.strip()

        # Optional: lat/lng updates if provided
        if "destination_latitude" in data:
            parcel.destination_latitude = data["destination_latitude"]
        if "destination_longitude" in data:
            parcel.destination_longitude = data["destination_longitude"]

        db.session.commit()
        return parcel.to_dict(), 200


class ParcelStatus(Resource):
    """Update parcel status (admin only)."""
    @jwt_required()
    def patch(self, parcel_id):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.admin:
            return {"error": "Admin privileges required"}, 403

        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404

        new_status = (request.json or {}).get("status")
        if not new_status:
            return {"error": "Missing status field"}, 400

        parcel.status = new_status
        db.session.commit()
        return parcel.to_dict(), 200
