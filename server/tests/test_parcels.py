import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import json
from server.models import db, User, Parcel, ParcelHistory
from server.app import app


def create_admin_user():
    admin = User(
        username='admin',
        email='admin@deliveroo.com',
        phone_number='1111111111',
        admin=True
    )
    admin.password = 'adminpass' 
    db.session.add(admin)
    db.session.commit()
    return admin


def create_normal_user():
    user = User(
        username='user1',
        email='user1@deliveroo.com',
        phone_number='2222222222',
        admin=False
    )
    user.password = 'userpass' 
    db.session.add(user)
    db.session.commit()
    return user


def create_parcel(owner):
    parcel = Parcel(
        user_id=owner.id,
        status='pending',
        present_location='Nairobi',
        destination='Mombasa',
        weight=2.5,
        cost=100.0
    )
    db.session.add(parcel)
    db.session.commit()
    return parcel

def get_token(client, user):
    response = client.post('/login', json={
        "username": user.username,
        "password": "adminpass" if user.admin else "userpass"
    })

    assert response.status_code == 200, f"Login failed: {response.get_data(as_text=True)}"
    return response.get_json()["access_token"]



def test_admin_can_view_all_parcels(client):
    admin = create_admin_user()
    token = get_token(client, admin)

    response = client.get('/admin/parcels', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200


def test_non_admin_cannot_access_admin_routes(client):
    user = create_normal_user()
    token = get_token(client, user)

    response = client.get('/admin/parcels', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 403


def test_admin_can_update_status_and_creates_history(client):
    admin = create_admin_user()
    user = create_normal_user()
    parcel = create_parcel(user)
    token = get_token(client, admin)

    response = client.patch(f'/admin/parcels/{parcel.id}/status',
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "in-transit"}
    )

    assert response.status_code == 200
    updated = Parcel.query.get(parcel.id)
    assert updated.status == "in-transit"

    history = ParcelHistory.query.filter_by(parcel_id=parcel.id).first()
    assert history is not None
    assert history.update_type == "status"


def test_admin_can_update_location_and_creates_history(client):
    admin = create_admin_user()
    user = create_normal_user()
    parcel = create_parcel(user)
    token = get_token(client, admin)

    response = client.patch(f'/admin/parcels/{parcel.id}/location',
        headers={"Authorization": f"Bearer {token}"},
        json={"present_location": "Kisumu"}
    )

    assert response.status_code == 200
    updated = Parcel.query.get(parcel.id)
    assert updated.present_location == "Kisumu"

    history = ParcelHistory.query.filter_by(parcel_id=parcel.id).first()
    assert history is not None
    assert history.update_type == "location"


def test_admin_can_view_parcel_history(client):
    admin = create_admin_user()
    user = create_normal_user()
    parcel = create_parcel(user)

    token = get_token(client, admin)

    # Admin updates status to create a history record
    client.patch(f'/admin/parcels/{parcel.id}/status',
                 headers={"Authorization": f"Bearer {token}"},
                 json={"status": "in-transit"})

    # Check history route
    response = client.get('/admin/histories', headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert any(h["parcel_id"] == parcel.id for h in data)
