from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from server.config import create_app, db, api
from server.models import User, Parcel, ParcelHistory
from server.routes.auth_routes import Login
from server.routes.admin_routes import (
    AdminParcelList, UpdateParcelStatus, UpdateParcelLocation,
    ParcelHistoryList, ParcelHistoryDetail
)
from server.routes.profile import Signup, Logout, Profile
from server.routes.parcels import ParcelList, ParcelResource, ParcelCancel, ParcelDestination, ParcelStatus

app = create_app()

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

# Parcel routes
api.add_resource(ParcelList, '/parcels')
api.add_resource(ParcelResource, '/parcels/<int:parcel_id>')
api.add_resource(ParcelCancel, '/parcels/<int:parcel_id>/cancel')
api.add_resource(ParcelDestination, '/parcels/<int:parcel_id>/destination')
api.add_resource(ParcelStatus, '/parcels/<int:parcel_id>/status')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
