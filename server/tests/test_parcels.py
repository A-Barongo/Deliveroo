"""Tests for parcel-related endpoints in Deliveroo app."""
import sys
import os
from uuid import uuid4
from server.config import db
from server.models import User, Parcel, ParcelHistory

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def unique_phone():
    """Generate a unique 10-digit phone number."""
    return f"{uuid4().int % 10**10:010d}"


def create_admin_user():
    phone = unique_phone()
    admin = User()
    admin.username = f"admin_{uuid4().hex[:6]}"
    admin.email = f"admin_{uuid4().hex[:6]}@deliveroo.com"
    admin.phone_number = phone
    admin.admin = True
    admin.password = 'adminpass'
    db.session.add(admin)
    db.session.commit()
    return admin


def create_normal_user():
    phone = unique_phone()
    user = User()
    user.username = f"user_{uuid4().hex[:6]}"
    user.email = f"user_{uuid4().hex[:6]}@deliveroo.com"
    user.phone_number = phone
    user.admin = False
    user.password = 'userpass'
    db.session.add(user)
    db.session.commit()
    return user


def create_parcel(owner):
    parcel = Parcel()
    parcel.user_id = owner.id
    parcel.status = 'pending'
    parcel.current_location = 'Nairobi'
    parcel.destination_location_text = 'Mombasa'
    parcel.weight = 2.5
    parcel.cost = 100.0
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


# ---------------------- TESTS ----------------------

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
    assert updated is not None
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
        json={"current_location": "Kisumu"}
    )

    assert response.status_code == 200
    updated = Parcel.query.get(parcel.id)
    assert updated is not None
    assert updated.current_location == "Kisumu"

    history = ParcelHistory.query.filter_by(parcel_id=parcel.id).first()
    assert history is not None
    assert history.update_type == "location"


def test_admin_can_view_parcel_history(client):
    admin = create_admin_user()
    user = create_normal_user()
    parcel = create_parcel(user)
    token = get_token(client, admin)

    # Create history
    client.patch(f'/admin/parcels/{parcel.id}/status',
                 headers={"Authorization": f"Bearer {token}"},
                 json={"status": "in-transit"})

    # Check history
    response = client.get('/admin/histories', headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert any(h["parcel_id"] == parcel.id for h in data)

