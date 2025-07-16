from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from .config import app, db, api
from .models import User, Parcel, ParcelHistory

from server.routes.auth_routes import Login
from server.routes.admin_routes import (
    AdminParcelList, UpdateParcelStatus, UpdateParcelLocation,
    ParcelHistoryList, ParcelHistoryDetail
)
from server.routes.profile import Signup, Logout, Profile

# Register routes
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Profile, '/profile')
api.add_resource(AdminParcelList, '/admin/parcels')
api.add_resource(UpdateParcelStatus, '/admin/parcels/<int:id>/status')
api.add_resource(UpdateParcelLocation, '/admin/parcels/<int:id>/location')
api.add_resource(ParcelHistoryList, '/admin/histories')
api.add_resource(ParcelHistoryDetail, '/admin/histories/<int:id>')

if __name__ == '__main__':
    app.run(port=5001, debug=True)

