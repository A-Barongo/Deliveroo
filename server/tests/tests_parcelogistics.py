"""Tests for parcel logistics functionality."""
import pytest
from server.models import Parcel, User

def valid_parcel_data():
    return {
        'description': 'Test parcel',
        'sender_name': 'Alice',
        'sender_phone_number': '1234567890',
        'pickup_location_text': 'Origin',
        'destination_location_text': 'Destination',
        'pick_up_longitude': 36.8219,
        'pick_up_latitude': -1.2921,
        'destination_longitude': 36.8219,
        'destination_latitude': -1.2921,
        'recipient_name': 'Bob',
        'recipient_phone_number': '9876543210',
        'weight': 1.5
    }

def test_create_parcel(client):
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    assert response.status_code == 201
    resp = response.get_json()
    assert resp['description'] == data['description']
    assert resp['weight'] == data['weight']
    assert resp['status'] == 'pending'
    assert 'id' in resp

def test_get_parcels(client):
    data = valid_parcel_data()
    client.post('/parcels', json=data)
    response = client.get('/parcels')
    assert response.status_code == 200
    parcels = response.get_json()['parcels']
    assert isinstance(parcels, list)
    assert parcels[0]['weight'] == data['weight']

def test_get_parcel_by_id(client):
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    parcel_id = response.get_json()['id']
    response = client.get(f'/parcels/{parcel_id}')
    assert response.status_code == 200
    parcel = response.get_json()
    assert parcel['weight'] == data['weight']

def test_cancel_parcel(client):
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    parcel_id = response.get_json()['id']
    response = client.patch(f'/parcels/{parcel_id}/cancel')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'cancelled'

def test_edit_destination(client):
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    parcel_id = response.get_json()['id']
    response = client.patch(f'/parcels/{parcel_id}/destination', json={'destination_location_text': 'NewDest'})
    assert response.status_code == 200
    assert response.get_json()['destination_location_text'] == 'NewDest'

def test_patch_status(client):
    data = valid_parcel_data()
    response = client.post('/parcels', json=data)
    parcel_id = response.get_json()['id']
    response = client.patch(f'/parcels/{parcel_id}/status', json={'status': 'delivered'})
    assert response.status_code == 200
    assert response.get_json()['status'] == 'delivered'

def test_pagination(client):
    # Create 15 parcels
    for i in range(15):
        data = valid_parcel_data()
        data['description'] = f'Parcel {i}'
        client.post('/parcels', json=data)
    response = client.get('/parcels?page=2&per_page=10')
    assert response.status_code == 200
    result = response.get_json()
    assert result['page'] == 2
    assert result['per_page'] == 10
    assert result['total'] >= 15
    assert isinstance(result['parcels'], list)