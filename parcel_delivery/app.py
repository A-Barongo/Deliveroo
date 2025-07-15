from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)
mail = Mail(app)

from utils.google_maps import GoogleMapsService
from utils.email_service import EmailService
from utils.cost_calculator import CostCalculator

maps = GoogleMapsService(app.config['GOOGLE_MAPS_API_KEY'])
email = EmailService(mail)
cost = CostCalculator()

class Parcel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    pickup = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float)
    duration = db.Column(db.Float)
    price = db.Column(db.Float)
    status = db.Column(db.String(50), default='processing')
    recipient_email = db.Column(db.String(120), nullable=False)

@app.route('/api/parcels', methods=['POST'])
def create_parcel():
    data = request.get_json()
    
    pickup = maps.geocode(data['pickup'])
    destination = maps.geocode(data['destination'])
    
    if not pickup or not destination:
        return jsonify({'error': 'Address geocoding failed'}), 400

    route = maps.get_route_metrics(pickup, destination)
    if not route:
        return jsonify({'error': 'Route calculation failed'}), 400

    parcel = Parcel(
        weight=data['weight'],
        pickup=data['pickup'],
        destination=data['destination'],
        distance=route['distance_meters'],
        duration=route['duration_seconds'],
        price=cost.calculate(data['weight'], route['distance_meters']),
        recipient_email=data['email'],
        status='created'
    )
    
    db.session.add(parcel)
    db.session.commit()
    
    email.send_created(parcel)
    
    return jsonify({
        'id': parcel.id,
        'price': parcel.price,
        'distance': parcel.distance,
        'duration': parcel.duration
    }), 201

@app.route('/api/parcels/<int:parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    return jsonify({
        'id': parcel.id,
        'status': parcel.status,
        'price': parcel.price,
        'distance': parcel.distance,
        'duration': parcel.duration
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route('/')
def home():
    return "Parcel Delivery API is running"