# this file has all the code for parcels api
# we use blueprint to keep things together

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from models import Parcel
from config import db

class ParcelList(Resource):
    def get(self):
        # get all parcels with pagination
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
        # create a new parcel
        data = request.get_json()
        try:
            parcel = Parcel(**data)
            # cost calculation logic here if needed
            db.session.add(parcel)
            db.session.commit()
            return parcel.to_dict(), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class ParcelResource(Resource):
    def get(self, parcel_id):
        # get one parcel by id
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        return parcel.to_dict(), 200

class ParcelCancel(Resource):
    def patch(self, parcel_id):
        # cancel a parcel
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        if parcel.status != 'pending':
            return {"error": "only pending parcels can be cancelled"}, 400
        parcel.status = 'cancelled'
        db.session.commit()
        return parcel.to_dict(), 200

class ParcelDestination(Resource):
    def patch(self, parcel_id):
        # edit destination
        parcel = db.session.query(Parcel).get(parcel_id)
        if not parcel:
            return {"error": "parcel not found"}, 404
        if parcel.status != 'pending':
            return {"error": "only pending parcels can be edited"}, 400
        data = request.get_json()
        for field in ["destination_location_text", "destination_longitude", "destination_latitude"]:
            if field in data:
                setattr(parcel, field, data[field])
        db.session.commit()
        return parcel.to_dict(), 200

class ParcelStatus(Resource):
    def patch(self, parcel_id):
        # change status
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