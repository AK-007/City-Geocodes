import unittest
from src import app
from src.routes import geocode_cache


class GeocodeUnitTest(unittest.TestCase):
    def setUp(self):
        self.__app = app
        self.__client = self.__app.test_client()

    def test_get_geocode(self):
        # Testing successful GET request
        resp = self.__client.get(path='/geocode/Bengaluru')
        self.assertEqual(resp.status_code, 200)

        # Response must contain latitude and longitude
        self.assertIn('latitude', resp.json['data'])
        self.assertIn('longitude', resp.json['data'])

        # Request must be served from API call
        self.assertNotIn('from', resp.json)

        # The city must be added to the cache
        self.assertIn('bengaluru', geocode_cache)

        # GET request with the same query
        resp = self.__client.get(path='/geocode/Bengaluru')
        self.assertEqual(resp.status_code, 200)

        # Response must contain latitude and longitude
        self.assertIn('latitude', resp.json['data'])
        self.assertIn('longitude', resp.json['data'])

        # The request must be served from the cache
        self.assertIn('from', resp.json)
        self.assertEqual('cache', resp.json['from'])

        # Size of cache must remain same
        self.assertEqual(len(geocode_cache), 1)

    def test_post_geocode(self):
        # Testing POST request
        resp = self.__client.post(path='/geocode/Bengaluru')

        # The request must fail as only GET request is allowed
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json['error'], "Method not allowed")

    def test_undefined_route(self):
        resp = self.__client.post(path='/location')

        # The request should return 404 as no such endpoint defined in the REST API
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json['error'], "Endpoint not found")


if __name__ == '__main__':
    unittest.main()
