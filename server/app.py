from routes.profile import Signup,Login,Logout,Profile
from config import app, db, api
    
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Profile, '/profile')

if __name__ == '__main__':
    app.run(port=5001, debug=True)