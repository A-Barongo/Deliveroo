import pytest
from flask_jwt_extended import decode_token
from flask import json
from server.config import blacklist

# ---- Fixtures ---- #

@pytest.fixture
def valid_user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "phone_number": "0712345678"
    }

@pytest.fixture
def invalid_user_data():
    return {
        "username": "",
        "email": "invalid-email",
        "password": "",
        "phone_number": ""
    }
    
@pytest.fixture
def fresh_user_data():
    import random
    return {
        "username": f"user{random.randint(1000, 9999)}",
        "email": f"user{random.randint(1000, 9999)}@example.com",
        "password": "password123",
        "phone_number": f"07{random.randint(10000000, 99999999)}"
    }


# ---- Test Cases ---- #

def test_signup_with_valid_data(client, valid_user_data):
    res = client.post('/signup', json=valid_user_data)
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == valid_user_data["username"]

def test_signup_with_invalid_data(client, invalid_user_data):
    res = client.post('/signup', json=invalid_user_data)
    assert res.status_code == 422 or res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_login_with_correct_credentials(client, valid_user_data):
    # Signup
    client.post('/signup', json=valid_user_data)

    #login
    res = client.post('/login', json={
        "username": valid_user_data["username"],
        "password": valid_user_data["password"]
    })

    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data

def test_login_with_wrong_password(client, valid_user_data):
    client.post('/signup', json=valid_user_data)

    res = client.post('/login', json={
        "username": valid_user_data["username"],
        "password": "wrongpassword"
    })

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"

def test_protected_route_rejects_unauthenticated_user(client):
    res = client.get('/profile')  
    assert res.status_code == 401 

def test_protected_route_allows_authenticated_user(client, fresh_user_data):
    # Signup and get token
    res = client.post('/signup', json=fresh_user_data)
    token = res.get_json()["access_token"]

    # Access protected route with token
    res = client.get('/profile', headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    assert "username" in res.get_json()

def test_logout_blacklists_token(client, fresh_user_data):
    # Signup and get token
    res = client.post('/signup', json=fresh_user_data)
    token = res.get_json()["access_token"]
    jti = decode_token(token)["jti"]

    # Logout
    res = client.post('/logout', headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    assert jti in blacklist

    # Try accessing protected route again
    res = client.get('/profile', headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 401  
