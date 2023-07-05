import openrouteservice
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="My App")
location = geolocator.geocode("Avenue de la garenne Gramat")
print(location.address)
print(location.longitude,location.latitude)
#print(routes)

def find_travel_time(from_place,to_place):
    geolocator = Nominatim(user_agent="My App")
    from_place = geolocator.geocode(from_place)
    print(from_place.address)
    to_place = geolocator.geocode(to_place)
    print(to_place.address)
    client = openrouteservice.Client(key='5b3ce3597851110001cf6248a579a11b1c3641b78e76a62508c7620d') # Specify your personal API key
    routes = client.directions(((from_place.latitude,from_place.longitude),(to_place.latitude,to_place.longitude)))
    #print(routes)
    #print(routes.get('routes')[0].get('summary').get('distance'),routes.get('routes')[0].get('summary').get('duration'))

find_travel_time("new york","los angeles")