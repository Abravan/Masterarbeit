import csv
from geopy.geocoders import Nominatim

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to get address from latitude and longitude
def get_address(lat, lon):
    location = geolocator.reverse((lat, lon), exactly_one=True)
    return location.address if location else "Address not found"

# Read the CSV file
with open('GPS_D7.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        latitude = float(row['Latitude NMEA'])
        longitude = float(row['Longitude NMEA'])
        address = get_address(latitude, longitude)
        print(f"Latitude: {latitude}, Longitude: {longitude} => Address: {address}")
