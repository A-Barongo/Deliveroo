from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from .models import Parcel
from .helpers import calculate_parcel_cost
from datetime import datetime

# Assume you have a way to get the current user (e.g., Flask-Login or JWT)
def get_current_user_id():
    # Placeholder: Replace with real authentication
    return 1

parcels_bp = Blueprint('parcels', __name__)

# POST /parcels
@parcels_bp.route('/parcels', methods=['POST'])
def create_parcel():
    data = request.get_json()
    weight = data.get('weight')
    destination = data.get('destination')
    if weight is None or destination is None:
        return jsonify({'error': 'weight and destination required'}), 400
    cost = calculate_parcel_cost(weight)
    parcel = Parcel(
        user_id=get_current_user_id(),
        weight=weight,
        cost=cost,
        status='pending',
        destination=destination
    )
    db: Session = request.environ['db_session']
    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    return jsonify(parcel.to_dict()), 201

# GET /parcels
@parcels_bp.route('/parcels', methods=['GET'])
def list_parcels():
    db: Session = request.environ['db_session']
    user_id = get_current_user_id()
    parcels = db.query(Parcel).filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in parcels]), 200

# GET /parcels/<id>
@parcels_bp.route('/parcels/<int:parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    return jsonify(parcel.to_dict()), 200

# PATCH /parcels/<id>/cancel
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
    return jsonify(parcel.to_dict()), 200

# PATCH /parcels/<id>/destination
@parcels_bp.route('/parcels/<int:parcel_id>/destination', methods=['PATCH'])
def edit_parcel_destination(parcel_id):
    db: Session = request.environ['db_session']
    parcel = db.query(Parcel).filter_by(id=parcel_id, user_id=get_current_user_id()).first()
    if not parcel:
        return jsonify({'error': 'Parcel not found'}), 404
    if parcel.status == 'delivered':
        return jsonify({'error': 'Cannot edit delivered parcel'}), 400
    data = request.get_json()
    new_destination = data.get('destination')
    if not new_destination:
        return jsonify({'error': 'destination required'}), 400
    parcel.destination = new_destination
    parcel.updated_at = datetime.utcnow()
    db.commit()
    return jsonify(parcel.to_dict()), 200 