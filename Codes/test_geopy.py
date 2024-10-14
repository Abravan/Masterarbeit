import os
import time
import pandas as pd
from geopy.geocoders import Nominatim

# Get the current directory where the script is running
current_directory = os.getcwd()

# Go one folder back (to the parent directory) and then into the 'Data' folder
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
folder_path = os.path.join(parent_directory, "Data")

# List all the CSV files in the 'Data' folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Create a dictionary to store DataFrames with file names (without extension) as keys
dataframes = {}

# Initialize the geocoder
from geopy.geocoders import Photon
geolocator = Photon(user_agent="measurements")

# Function to convert NMEA latitude/longitude to decimal degrees
def nmea_to_decimal(degree_minute, indicator):
    try:
        degree_minute_str = str(degree_minute)
        degrees = float(degree_minute_str[:2])
        minutes = float(degree_minute_str[2:])
        decimal = degrees + (minutes / 60)
        if indicator in ['S', 'W']:
            decimal = -decimal
        return decimal
    except (ValueError, IndexError) as e:
        print(f"Error converting NMEA to decimal: {e}")
        return None

# Function to perform reverse geocoding with delay
def reverse_geocode(lat, lon):
    try:
        if lat is not None and lon is not None:
            location = geolocator.reverse((lat, lon), language='en', timeout=10)
            return location.address if location else None
        return "Invalid coordinates"
    except Exception as e:
        print(f"Error during geocoding: {e}")
        return None

# Loop through each CSV file and read it into a DataFrame
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df_name = os.path.splitext(file)[0]  # Get the file name without extension
    dataframes[df_name] = pd.read_csv(file_path)  # Read CSV into a DataFrame and store it in the dictionary

# Accessing individual DataFrames
df_pgs_d7 = dataframes.get("GPS_D7")

# Check if the DataFrame was loaded correctly
if df_pgs_d7 is not None:
    # Ensure columns exist and convert NMEA coordinates to decimal degrees
    if 'Latitude NMEA' in df_pgs_d7.columns and 'Longitude NMEA' in df_pgs_d7.columns:
        df_pgs_d7['Latitude Decimal'] = df_pgs_d7.apply(
            lambda row: nmea_to_decimal(row['Latitude NMEA'], row['Indicator Latitude NMEA']),
            axis=1
        )
        df_pgs_d7['Longitude Decimal'] = df_pgs_d7.apply(
            lambda row: nmea_to_decimal(row['Longitude NMEA'], row['Indicator Longitude NMEA']),
            axis=1
        )

        # Initialize a list to store the addresses
        addresses = []

        # Loop through the DataFrame and perform reverse geocoding with a delay
        for index, row in df_pgs_d7.iterrows():
            lat = row['Latitude Decimal']
            lon = row['Longitude Decimal']
            address = reverse_geocode(lat, lon)
            addresses.append(address)
            
            # Print progress (optional)
            print(f"Processed row {index+1}/{len(df_pgs_d7)}: {address}")

            # Add a delay of 1 second to respect the Nominatim rate limit
            time.sleep(1)

        # Add the addresses to the DataFrame
        df_pgs_d7['Address'] = addresses

        # Save the updated DataFrame to a new CSV file
        output_file_path = os.path.join(folder_path, "GPS_D7_with_Address.csv")
        df_pgs_d7.to_csv(output_file_path, index=False)

        print(f"Updated DataFrame with addresses saved to {output_file_path}")
    else:
        print("Required columns are missing in the GPS DataFrame.")
else:
    print("GPS DataFrame not found.")
print("end")
