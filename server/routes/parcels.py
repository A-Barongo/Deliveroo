# this file has all the code for parcels api
# we use blueprint to keep things together

from flask import Blueprint, request, jsonify, g
from server.models import Parcel
from server.schemas import ParcelSchema
from server.helpers import calculate_parcel_cost
from sqlalchemy.exc import SQLAlchemyError

# make a blueprint for parcels
parcels_bp = Blueprint('parcels', __name__)

# make schemas for turning parcel to json
parcel_schema = ParcelSchema()
parcels_schema = ParcelSchema(many=True)

# make a new parcel
@parcels_bp.route('/parcels', methods=['POST'])
def create_parcel():
    # this makes a new parcel from json data
    data = request.get_json() # get data from user
    errors = parcel_schema.validate(data) # check if data is ok
    if errors:
        return {"error": errors}, 400 # if not ok tell user
    try:
        parcel = Parcel(**data) # make parcel
        parcel.cost = calculate_parcel_cost(parcel.weight) # set cost
        g.db_session.add(parcel) # add to database
        g.db_session.commit() # save to database
        return parcel_schema.dump(parcel), 201 # send back the new parcel
    except SQLAlchemyError as e:
        g.db_session.rollback() # if error undo
        return {"error": str(e)}, 500 # tell user error

# get all parcels with pages
@parcels_bp.route('/parcels', methods=['GET'])
def list_parcels():
    # this gets all parcels but not too many at once
    page = int(request.args.get('page', 1)) # which page
    per_page = int(request.args.get('per_page', 10)) # how many per page
    query = g.db_session.query(Parcel)
    total = query.count() # how many parcels in total
    parcels = query.offset((page - 1) * per_page).limit(per_page).all() # get some parcels
    return {
        "parcels": parcels_schema.dump(parcels),
        "page": page,
        "per_page": per_page,
        "total": total
    }, 200 # send back parcels

# get one parcel by id
@parcels_bp.route('/parcels/<int:parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    # this gets one parcel if it exists
    parcel = g.db_session.query(Parcel).get(parcel_id)
    if not parcel:
        return {"error": "parcel not found"}, 404 # if not found tell user
    return parcel_schema.dump(parcel), 200 # send back parcel

# cancel a parcel
@parcels_bp.route('/parcels/<int:parcel_id>/cancel', methods=['PATCH'])
def cancel_parcel(parcel_id):
    # this cancels a parcel if it is pending
    parcel = g.db_session.query(Parcel).get(parcel_id)
    if not parcel:
        return {"error": "parcel not found"}, 404 # if not found tell user
    if parcel.status != 'pending':
        return {"error": "only pending parcels can be cancelled"}, 400 # only pending can cancel
    parcel.status = 'cancelled' # set status to cancelled
    g.db_session.commit() # save
    return parcel_schema.dump(parcel), 200 # send back parcel

# change where parcel goes
@parcels_bp.route('/parcels/<int:parcel_id>/destination', methods=['PATCH'])
def edit_destination(parcel_id):
    # this changes the destination if parcel is pending
    parcel = g.db_session.query(Parcel).get(parcel_id)
    if not parcel:
        return {"error": "parcel not found"}, 404 # if not found tell user
    if parcel.status != 'pending':
        return {"error": "only pending parcels can be edited"}, 400 # only pending can edit
    data = request.get_json() # get new data
    for field in ["destination_location_text", "destination_longitude", "destination_latitude"]:
        if field in data:
            setattr(parcel, field, data[field]) # change the field
    g.db_session.commit() # save
    return parcel_schema.dump(parcel), 200 # send back parcel

# change status of parcel
@parcels_bp.route('/parcels/<int:parcel_id>/status', methods=['PATCH'])
def change_status(parcel_id):
    # this changes the status like to delivered
    parcel = g.db_session.query(Parcel).get(parcel_id)
    if not parcel:
        return {"error": "parcel not found"}, 404 # if not found tell user
    data = request.get_json() # get new status
    new_status = data.get('status')
    if not new_status:
        return {"error": "missing status field"}, 400 # need status
    parcel.status = new_status # set new status
    g.db_session.commit() # save
    return parcel_schema.dump(parcel), 200 # send back parcel 