"""Pytest fixtures for Deliveroo app tests."""
import pytest
from server.config import create_app, db

@pytest.fixture(scope='module')
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()  
        db.session.remove()
        db.drop_all()
