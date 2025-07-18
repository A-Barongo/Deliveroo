"""Parcel routes for Deliveroo app."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import Parcel
from server.config import db


class ParcelList(Resource):
    """List and create parcels."""

    def get(self):
        """
        Get a paginated list of parcels.
        ---
        tags:
          - Parcels
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
          - name: per_page
            in: query
            type: integer
            default: 10
        responses:
          200:
            description: List of parcels with pagination
        """
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        parcels = Parcel.query.offset((page - 1) * per_page).limit(per_page).all()
        total = Parcel.query.count()
        return {
            "parcels": [p.to_dict() for p in parcels],
            "page": page,
            "per_page": per_page,
            "total": total
        }, 200

    def post(self):
        """
        Create a new parcel.
        ---
        tags:
          - Parcels
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                  - user_id
                  - pickup_location_text
                  - destination_location_text
                properties:
                  user_id:
                    type: integer
                  pickup_location_text:
                    type: string
                  pickup_latitude:
                    type: number
                  pickup_longitude:
                    type: number
                  destination_location_text:
                    type: string
                  destination_latitude:
                    type: number
                  destination_longitude:
                    type: number
                  weight:
                    type: number
                  status:
                    type: string
        responses:
          201:
            description: Parcel created
          500:
            description: Server error
        """
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
    """Get parcel by ID."""

    def get(self, parcel_id):
        """
        Get parcel by ID.
        ---
        tags:
          - Parcels
        parameters:
          - name: parcel_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Parcel found
          404:
            description: Parcel not found
        """
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        return parcel.to_dict(), 200


class ParcelCancel(Resource):
    """Cancel a parcel."""

    @jwt_required()
    def patch(self, parcel_id):
        """
        Cancel parcel by owner if not delivered.
        ---
        tags:
          - Parcels
        security:
          - BearerAuth: []
        parameters:
          - name: parcel_id
            in: path
            required: true
            type: integer
        responses:
          200:
            description: Parcel cancelled
          400:
            description: Already delivered
          403:
            description: Not parcel owner
          404:
            description: Parcel not found
        """
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

    def patch(self, parcel_id):
        """
        Update parcel destination (if not delivered).
        ---
        tags:
          - Parcels
        parameters:
          - name: parcel_id
            in: path
            required: true
            type: integer
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  destination_location_text:
                    type: string
                  destination_latitude:
                    type: number
                  destination_longitude:
                    type: number
        responses:
          200:
            description: Parcel updated
          400:
            description: Already delivered
          404:
            description: Not found
        """
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404
        if parcel.status == 'delivered':
            return {"error": "Cannot update delivered parcel"}, 400

        data = request.get_json()
        for field in ["destination_location_text", "destination_latitude", "destination_longitude"]:
            if field in data:
                setattr(parcel, field, data[field])
        db.session.commit()
        return parcel.to_dict(), 200


class ParcelStatus(Resource):
    """Update parcel status (generic)."""

    def patch(self, parcel_id):
        """
        Update parcel status.
        ---
        tags:
          - Parcels
        parameters:
          - name: parcel_id
            in: path
            required: true
            type: integer
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                  - status
                properties:
                  status:
                    type: string
        responses:
          200:
            description: Parcel updated
          400:
            description: Missing status
          404:
            description: Not found
        """
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {"error": "Parcel not found"}, 404

        new_status = request.json.get("status")
        if not new_status:
            return {"error": "Missing status field"}, 400

        parcel.status = new_status
        db.session.commit()
        return parcel.to_dict(), 200
