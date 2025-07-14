from flask import request, session,make_response,jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User,Parcel,ParcelHistory

if __name__ == '__main__':
    app.run(port=5001, debug=True)