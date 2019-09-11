from src import app
from flask import make_response
import requests
import json
from requests.exceptions import HTTPError, ConnectionError, RequestException
from .classes.cache import Geocode

geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='

# This dict stores the geocode for cities already queried
geocode_cache = {}


@app.route("/geocode/<string:city>", methods=['GET'])
def get_geocode(city):
    city_key = city.lower()

    # If the city has been queried before the request must be served from the cache
    if city_key in geocode_cache:
        return make_response({
            "data": geocode_cache[city_key].get_result(),
            "status": 200,
            "from": "cache"  # This parameter is included just for testing the caching functionality
        }, 200)
    try:
        response = requests.get(geocode_url + city + '&key=' + app.config["API_KEY"])
        response.raise_for_status()
    except HTTPError as e1:
        return make_response({
            "error": "HTTP Error",
            "status": e1.response.status_code
        }, e1.response.status_code)
    except ConnectionError as e2:
        return make_response({
            "error": "Connection Error",
            "status": 503
        }, 503)
    except RequestException as e3:
        return make_response({
            "error": "Some error occurred",
            "status": 500
        }, 500)
    else:
        data = json.loads(response.text)

        # Handling requests for unknown city
        if data['status'] == "ZERO_RESULTS":
            return make_response({
                "message": "No such city present"
            }, 200)

        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']

        # In case of concurrent requests with same city, we need to update the cache only once
        if city_key not in geocode_cache:
            geocode_cache[city_key] = Geocode(latitude, longitude)
        return make_response({
            "data": geocode_cache[city_key].get_result(),
            "status": 200
        }, 200)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return make_response({"error": "Endpoint not found", "status": 404}, 404)


@app.errorhandler(405)
def not_found_error(error):
    return make_response({"error": "Method not allowed", "status": 405}, 405)


@app.errorhandler(500)
def internal_error(error):
    return make_response({"error": "500 Internal server error", "status": 500}, 500)
