import pytest
from flask import Flask
from . import create_app
from .models import Base, Parcel, User
from .helpers import calculate_parcel_cost
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
    # Patch the get_current_user_id function in routes
    monkeypatch.setattr('backend.routes.get_current_user_id', fake_get_current_user_id)
    with app.app_context():
        with app.test_client() as client:
            yield client

def test_calculate_parcel_cost():
    assert calculate_parcel_cost(2) == 300
    assert calculate_parcel_cost(0.5) == 75

def test_create_parcel(client, db_session, monkeypatch):
    monkeypatch.setattr('backend.routes.request', type('obj', (object,), {'environ': {'db_session': db_session}, 'get_json': lambda: {'weight': 2, 'destination': 'Nairobi'}}))
    response = client.post('/parcels', json={'weight': 2, 'destination': 'Nairobi'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['weight'] == 2
    assert data['cost'] == 300
    assert data['destination'] == 'Nairobi'
    assert data['status'] == 'pending'

def test_cancel_parcel(client, db_session, monkeypatch):
    # Create a parcel
    parcel = Parcel(user_id=1, weight=1, cost=150, status='pending', destination='Mombasa')
    db_session.add(parcel)
    db_session.commit()
    # Cancel it
    monkeypatch.setattr('backend.routes.request', type('obj', (object,), {'environ': {'db_session': db_session}, 'get_json': lambda: {}}))
    response = client.patch(f'/parcels/{parcel.id}/cancel')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'cancelled'
    # Try cancelling delivered parcel
    parcel.status = 'delivered'
    db_session.commit()
    response = client.patch(f'/parcels/{parcel.id}/cancel')
    assert response.status_code == 400

def test_edit_destination(client, db_session, monkeypatch):
    # Create a parcel
    parcel = Parcel(user_id=1, weight=1, cost=150, status='pending', destination='Kisumu')
    db_session.add(parcel)
    db_session.commit()
    # Edit destination
    monkeypatch.setattr('backend.routes.request', type('obj', (object,), {'environ': {'db_session': db_session}, 'get_json': lambda: {'destination': 'Eldoret'}}))
    response = client.patch(f'/parcels/{parcel.id}/destination', json={'destination': 'Eldoret'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['destination'] == 'Eldoret'
    # Try editing delivered parcel
    parcel.status = 'delivered'
    db_session.commit()
    response = client.patch(f'/parcels/{parcel.id}/destination', json={'destination': 'Nakuru'})
    assert response.status_code == 400 