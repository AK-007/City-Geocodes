class Geocode():
    def __init__(self, latitude, longitude):
        self.__latitude = latitude
        self.__longitude = longitude

    def get_result(self):
        return {
            "latitude": self.__latitude,
            "longitude": self.__longitude
        }
