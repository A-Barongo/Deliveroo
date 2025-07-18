import googlemaps
from datetime import datetime
from flask import current_app

class MapsService:
    def __init__(self):
        self.client = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    
    def geocode(self, address):
        try:
            result = self.client.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return location['lat'], location['lng']
            return None, None
        except Exception as e:
            current_app.logger.error(f"Geocoding failed: {str(e)}")
            return None, None

    def get_route_metrics(self, origin, destination):
        try:
            matrix = self.client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="driving",
                departure_time=datetime.now()
            )
            if matrix['rows'][0]['elements'][0]['status'] == 'OK':
                element = matrix['rows'][0]['elements'][0]
                return element['distance']['value'], element['duration']['value']
            return None, None
        except Exception as e:
            current_app.logger.error(f"Route metrics failed: {str(e)}")
            return None, None
    
    def calculate_delivery_cost(self, distance_meters, weight_category):
        weight_pricing = {
            'light': 5.00,
            'medium': 10.00,
            'heavy': 15.00,
            'fragile': 25.00
        }
        base_cost = weight_pricing.get(weight_category, 10.00)
        distance_km = distance_meters / 1000
        distance_cost = distance_km * 0.75
        return round(base_cost + distance_cost, 2)
