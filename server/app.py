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

# Register routes
api.add_resource(AdminParcelList, '/admin/parcels')
api.add_resource(UpdateParcelStatus, '/admin/parcels/<int:id>/status')
api.add_resource(UpdateParcelLocation, '/admin/parcels/<int:id>/location')
api.add_resource(ParcelHistoryList, '/admin/histories')
api.add_resource(ParcelHistoryDetail, '/admin/histories/<int:id>')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
