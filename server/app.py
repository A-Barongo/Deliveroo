from flask import request, session,make_response,jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from .config import app, db, api
from .models import User,Parcel,ParcelHistory

from server.routes.admin_routes import AdminParcelList, UpdateParcelStatus, UpdateParcelLocation

api.add_resource(AdminParcelList, '/admin/parcels')
api.add_resource(UpdateParcelStatus, '/admin/parcels/<int:id>/status')
api.add_resource(UpdateParcelLocation, '/admin/parcels/<int:id>/location')


if __name__ == '__main__':
    app.run(port=5001, debug=True)