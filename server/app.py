from routes.parcels import ParcelList, ParcelResource, ParcelCancel, ParcelDestination, ParcelStatus
from config import app, db, api

api.add_resource(ParcelList, '/parcels')
api.add_resource(ParcelResource, '/parcels/<int:parcel_id>')
api.add_resource(ParcelCancel, '/parcels/<int:parcel_id>/cancel')
api.add_resource(ParcelDestination, '/parcels/<int:parcel_id>/destination')
api.add_resource(ParcelStatus, '/parcels/<int:parcel_id>/status')

if __name__ == '__main__':
    app.run(port=5000, debug=True) 