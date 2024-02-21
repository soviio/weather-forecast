import json
import requests
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

API_TOKEN = 'your_token'
WEATHER_API_KEY = '-'


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location, date):
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=metric&key={WEATHER_API_KEY}&contentType=json&date={date}'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def home_page():
    return '<p><h2>KMA HW1 (Komar Sofiia): python Saas.</h2></p>'


@app.route('/content/api/v1/integration/generate', methods=['POST'])
def weather_endpoint():
    data = request.json
    token = data.get('token')
    requester_name = data.get('requester_name')
    location = data.get('location')
    date = data.get('date')
   

    if token != API_TOKEN:
        raise InvalidUsage('Invalid token', status_code=403)

    weather_data = get_weather(location, date)
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    recommendation = ''
    if 'rain' in weather_data['days'][0]['conditions'].lower():
        recommendation = 'It is recommended to take an umbrella.'
    elif 'sun' in weather_data['days'][0]['conditions'].lower():
        recommendation = 'It is recommended to take sunglasses.'

    result = {
    'requester_name': requester_name,
    'timestamp': timestamp,
    'location': location,
    'date': date,
    'weather': {
        'windspeed': weather_data['days'][0]['windspeed'],
        'temp': weather_data['days'][0]['temp'],
        'humidity': weather_data['days'][0]['humidity'],
        'cloudcover': weather_data['days'][0]['cloudcover'],
        'feelslike': weather_data['days'][0]['feelslike'],
        'description': weather_data['days'][0]['description'],
        'sunrise': weather_data['days'][0]['sunrise'],
        'sunset': weather_data['days'][0]['sunset'],
        'visibility': weather_data['days'][0]['visibility'],
        'snow': weather_data['days'][0]['snow'],
        'conditions': weather_data['days'][0]['conditions'],
        'recommendation': recommendation
        }
    }

    return result
