# middleware.py
from django.http import HttpResponseForbidden
from haversine import haversine
from django.conf import settings
import geopy.distance

class LocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("LocationMiddleware is loaded")

    def __call__(self, request):
        print("LocationMiddleware is called")
        allowed_coordinate = settings.ALLOWED_COORDINATE
        print("allowed coord: ",allowed_coordinate)
        user_coordinate = self.get_user_coordinate(request)
        print("user coord: ",user_coordinate)
        if user_coordinate:
            if request.path == '/table/scan' or request.path == '/order':
                # Check access only for the specific URLs
                if self.is_within_radius(allowed_coordinate, user_coordinate):
                    return self.get_response(request)
                else:
                    return HttpResponseForbidden("Access denied. You are not within the allowed area.")
            else:
                # Allow access to all other URLs
                return self.get_response(request)
        else:
            # Handle cases where user coordinates are not available
            return self.get_response(request)

    def get_user_coordinate(self, request):
        print("coordinates are called")
        # Try to get latitude and longitude from GET parameters
        user_latitude = 47.472484  #request.GET.get('latitude')
        user_longitude = 19.060647 #request.GET.get('longitude')
        print(request.POST)
        # Check if both latitude and longitude are available
        if user_latitude is not None and user_longitude is not None:
            try:
                # Convert latitude and longitude to floats
                user_latitude = float(user_latitude)
                user_longitude = float(user_longitude)
                return (user_latitude, user_longitude)
            except ValueError:
                pass

        # Return None if coordinates are not available or invalid
        return None

    def is_within_radius(self, allowed_coordinate, user_coordinate):
        print("is within radius is called")
        dist = geopy.distance.geodesic(allowed_coordinate, user_coordinate).m
        print("disance",dist)
        return dist <= settings.RADIUS 