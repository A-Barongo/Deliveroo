import pytest
from flask import Flask
from . import create_app
from .models import Base, Parcel, User
from .helpers import calculate_parcel_cost
from .schemas import ParcelSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Add a test user
    user = User(id=1)
    session.add(user)
    session.commit()
    yield session
    session.close()

@pytest.fixture
def client(app, db_session, monkeypatch):
    def fake_get_current_user_id():
        return 1
    monkeypatch.setattr('server.routes.get_current_user_id', fake_get_current_user_id)
    with app.app_context():
        with app.test_client() as client:
            yield client

def valid_parcel_data():
    return {
        'description': 'Test parcel',
        'sender_name': 'Alice',
        'sender_phone_number': 1234567890,
        'pickup_location_text': 'Origin',
        'destination_location_text': 'Destination',
        'pick_up_longitude': 36.8219,
        'pick_up_latitude': -1.2921,
        'destination_longitude': 36.8219,
        'destination_latitude': -1.2921,
        'recipient_name': 'Bob',
        'recipient_phone_number': 9876543210
    }

def test_calculate_parcel_cost():
    assert calculate_parcel_cost(2) == 300
    assert calculate_parcel_cost(0.5) == 75

def test_create_parcel_valid(client, db_session, monkeypatch):
    data = valid_parcel_data()
    data['weight'] = 2.5
    response = client.post('/parcels', json=data)
    assert response.status_code == 201
    resp = response.get_json()
    assert resp['description'] == data['description']
    assert resp['sender_name'] == data['sender_name']
    assert resp['recipient_name'] == data['recipient_name']
    assert resp['status'] == 'pending'
    assert 'id' in resp
    assert resp['weight'] == 2.5

def test_create_parcel_invalid(client, db_session):
    data = valid_parcel_data()
    del data['sender_name']
    response = client.post('/parcels', json=data)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_cancel_parcel(client, db_session, monkeypatch):
    # Create a parcel
    parcel = Parcel(
        description='Cancel me', status='pending', sender_name='A', sender_phone_number=1,
        pickup_location_text='O', destination_location_text='D', pick_up_longitude=1.0, pick_up_latitude=1.0,
        destination_longitude=1.0, destination_latitude=1.0, recipient_name='B', recipient_phone_number=2,
        cost=150, user_id=1
    )
    db_session.add(parcel)
    db_session.commit()
    response = client.patch(f'/parcels/{parcel.id}/cancel')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'cancelled'
    # Use API to set status to delivered
    response = client.patch(f'/parcels/{parcel.id}/status', json={'status': 'delivered'})
    assert response.status_code == 200
    response = client.patch(f'/parcels/{parcel.id}/cancel')
    assert response.status_code == 400

def test_edit_destination(client, db_session, monkeypatch):
    # Create a parcel using the API
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    assert response.status_code == 201
    parcel_id = response.get_json()['id']
    # Edit destination
    response = client.patch(f'/parcels/{parcel_id}/destination', json={'destination_location_text': 'NewDest'})
    assert response.status_code == 200
    assert response.get_json()['destination_location_text'] == 'NewDest'
    # Use API to set status to delivered
    response = client.patch(f'/parcels/{parcel_id}/status', json={'status': 'delivered'})
    assert response.status_code == 200
    response = client.patch(f'/parcels/{parcel_id}/destination', json={'destination_location_text': 'Other'})
    assert response.status_code == 400
