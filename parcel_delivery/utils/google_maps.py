import requests

class GoogleMapsService:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={'address': address, 'key': self.api_key, 'region': 'us', 'language': 'en' }
        )
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return {'lat': location['lat'], 'lng': location['lng']}
        return None

    def get_route_metrics(self, origin, destination):
        response = requests.get(
            'https://maps.googleapis.com/maps/api/distancematrix/json',
            params={
                'origins': f"{origin['lat']},{origin['lng']}",
                'destinations': f"{destination['lat']},{destination['lng']}",
                'key': self.api_key,
                'units': 'metric'
            }
        )
        data = response.json()
        if data['status'] == 'OK':
            element = data['rows'][0]['elements'][0]
            return {
                'distance_meters': element['distance']['value'],
                'duration_seconds': element['duration']['value']
            }
        return None