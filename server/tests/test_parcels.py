"""Tests for parcel-related endpoints in Deliveroo app."""
import sys
import os
from uuid import uuid4
from server.models import db, User, Parcel, ParcelHistory
from server.app import app



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def unique_phone():
    return f"{uuid4().int % 10**10:010d}"


def create_admin_user():
    phone = unique_phone()
    admin = User(
        username=f"admin_{uuid4().hex[:6]}",
        email=f"admin_{uuid4().hex[:6]}@deliveroo.com",
        phone_number=phone,
        admin=True
    )
    admin.password = 'adminpass123'  # Must be 8+ characters
    db.session.add(admin)
    db.session.commit()
    return admin


def create_normal_user():
    phone = unique_phone()
    user = User(
        username=f"user_{uuid4().hex[:6]}",
        email=f"user_{uuid4().hex[:6]}@deliveroo.com",
        phone_number=phone,
        admin=False
    )
    user.password = 'userpass123'
    db.session.add(user)
    db.session.commit()
    return user


def create_parcel(owner):
    parcel = Parcel(
        user_id=owner.id,
        description="Test parcel",
        weight=2.5,
        status="pending",
        sender_name="John Doe",
        sender_phone_number="0712345678",
        recipient_name="Jane Doe",
        recipient_phone_number="0798765432",
        pickup_location_text="Nairobi",
        destination_location_text="Mombasa",
        pick_up_latitude=-1.2921,
        pick_up_longitude=36.8219,
        destination_latitude=-4.0435,
        destination_longitude=39.6682,
        current_location="Nairobi",
        current_location_latitude=-1.2921,
        current_location_longitude=36.8219,
        cost=375.0
    )
    db.session.add(parcel)
    db.session.commit()
    return parcel


def get_token(client, user):
    response = client.post('/login', json={
        "username": user.username,
        "password": "adminpass123" if user.admin else "userpass123"
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
                            json={"status": "in-transit"})

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
                            json={"current_location": "Kisumu"})

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
