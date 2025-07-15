from flask import request,make_response,jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User,Parcel,ParcelHistory
from flask_jwt_extended import create_access_token,jwt_required, get_jwt,get_jwt_identity
from config import blacklist

class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data['username'],
                email=data['email'],
                admin=data.get('admin', False)
            )
            user.password = data['password']  

            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)

            return {
                "user": user.to_dict(),
                "access_token": access_token
            }, 201

        except Exception as e:
            db.session.rollback()
            print(str(e))
            return {'error': 'Signup failed'}, 422


class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'error': 'Missing credentials'}, 400

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            access_token = create_access_token(identity=user.id)
            return {
                "user": user.to_dict(),
                "access_token": access_token
            }, 200

        return {'error': 'Unauthorized'}, 401
    
class Profile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return user.to_dict(), 200
        return {'error': 'User not found'}, 404
class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  
        blacklist.add(jti)
        return {"message": "Successfully logged out"}, 200
    
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Profile, '/profile')

if __name__ == '__main__':
    app.run(port=5001, debug=True)