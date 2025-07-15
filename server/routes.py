from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from .models import Parcel
from .helpers import calculate_parcel_cost
from .schemas import ParcelSchema
from datetime import datetime

def get_current_user_id():
    return 1

parcels_bp = Blueprint('parcels', __name__)
parcel_schema = ParcelSchema()

@parcels_bp.route('/parcels', methods=['POST'])
def create_parcel():
    data = request.get_json()
    weight = data.get('weight', 1)
    cost = calculate_parcel_cost(weight)
    parcel = Parcel(
        description=data.get('description'),
        weight=weight,
        status='pending',
        sender_name=data.get('sender_name'),
        sender_phone_number=data.get('sender_phone_number'),
        pickup_location_text=data.get('pickup_location_text'),
        destination_location_text=data.get('destination_location_text'),
        pick_up_longitude=data.get('pick_up_longitude'),
        pick_up_latitude=data.get('pick_up_latitude'),
        destination_longitude=data.get('destination_longitude'),
        destination_latitude=data.get('destination_latitude'),
        current_location_longitude=data.get('current_location_longitude'),
        current_location_latitude=data.get('current_location_latitude'),
        distance=data.get('distance'),
        cost=cost,
        recipient_name=data.get('recipient_name'),
        recipient_phone_number=data.get('recipient_phone_number'),
        courier_id=data.get('courier_id'),
        user_id=get_current_user_id()
    )
    db: Session = request.environ['db_session']
    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    return parcel_schema.dump(parcel), 201
@parcels_bp.route('/parcels', methods=['GET'])
def list_parcels():
    db: Session = request.environ['db_session']
    user_id = get_current_user_id()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    query = db.query(Parcel).filter_by(user_id=user_id)
    total = query.count()
    parcels = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({
        'parcels': parcel_schema.dump(parcels, many=True),
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    }), 200

@parcels_bp.route('/parcels/<int:parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    return parcel_schema.dump(parcel), 200
@parcels_bp.route('/parcels/<int:parcel_id>/cancel', methods=['PATCH'])
def cancel_parcel(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    if parcel.status == 'delivered':
        return jsonify({'error': 'Cannot cancel delivered parcel'}), 400
    parcel.status = 'cancelled'
    parcel.updated_at = datetime.utcnow()
    db.commit()
    return parcel_schema.dump(parcel), 200

@parcels_bp.route('/parcels/<int:parcel_id>/destination', methods=['PATCH'])
def edit_parcel_destination(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    if parcel.status == 'delivered':
        return jsonify({'error': 'Cannot edit delivered parcel'}), 400
    data = request.get_json()
    new_destination = data.get('destination_location_text')
    if not new_destination:
        return jsonify({'error': 'destination_location_text required'}), 400
    parcel.destination_location_text = new_destination
    parcel.updated_at = datetime.utcnow()
    db.commit()
    return parcel_schema.dump(parcel), 200
@parcels_bp.route('/parcels/<int:parcel_id>/status', methods=['PATCH'])
def update_parcel_status(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'status required'}), 400
    parcel.status = new_status
    parcel.updated_at = datetime.utcnow()
    db.commit()
    return parcel_schema.dump(parcel), 200
