import os
import pandas as pd
from opencage.geocoder import OpenCageGeocode
from tqdm import tqdm  # Import tqdm for the progress bar

# Get the current directory where the script is running
current_directory = os.getcwd()

# Go one folder back (to the parent directory) and then into the 'Data' folder
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
folder_path = os.path.join(parent_directory, "Data")

# List all the CSV files in the 'Data' folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Create a dictionary to store DataFrames with file names (without extension) as keys
dataframes = {}

# Initialize the geocoder with your actual API key
api_key = '3df64903c6bc4bdaaefc314da1fb93c6'  # Replace with your actual OpenCage API key
geocoder = OpenCageGeocode(api_key)

# Function to convert NMEA latitude/longitude to decimal degrees
def nmea_to_decimal(coord, direction):
    coord_str = str(coord).strip()  # Ensure no leading/trailing whitespace

    if not coord_str:  # Handle empty string
        return None

    if direction in ['N', 'S']:  # Latitude
        degrees = float(coord_str[:2])  # First two characters for degrees
        minutes = float(coord_str[2:]) / 60  # Remaining characters for minutes
    else:  # Longitude
        degrees = int(coord_str[0])  # For longitude, first three characters
        minutes = float(coord_str[1:]) / 60  # Remaining characters for minutes

    # Convert to decimal
    decimal = degrees + minutes 

    # Apply direction
    if direction in ['S', 'W']:
        decimal = -decimal
        
    return decimal

def reverse_geocode(lat, lon):
    try:
        if lat is not None and lon is not None:
            query = f"{lat}, {lon}"
            results = geocoder.geocode(query)
            if results:
                return results[0]['formatted']
            return "Address not found"
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
gps_df = dataframes.get("GPS_D7")

# # Only process the first 10 rows for testing
# gps_df = gps_df.head(10)

# Check if the DataFrame was loaded correctly
if gps_df is not None:
    # Ensure columns exist and convert NMEA coordinates to decimal degrees
    if ('Latitude NMEA' in gps_df.columns and 
        'Longitude NMEA' in gps_df.columns and 
        'Indicator Latitude NMEA' in gps_df.columns and 
        'Indicator Longitude NMEA' in gps_df.columns):
        
        gps_df['Latitude Decimal'] = gps_df.apply(
            lambda row: nmea_to_decimal(row['Latitude NMEA'], row['Indicator Latitude NMEA']),
            axis=1
        )
        gps_df['Longitude Decimal'] = gps_df.apply(
            lambda row: nmea_to_decimal(row['Longitude NMEA'], row['Indicator Longitude NMEA']),
            axis=1
        )

        # Print the output for debugging
        print(gps_df[['Latitude NMEA', 'Longitude NMEA', 'Latitude Decimal', 'Longitude Decimal']])
        
        # Perform reverse geocoding and add the address column with a progress bar
        gps_df['Address'] = [reverse_geocode(row['Latitude Decimal'], row['Longitude Decimal']) 
                             for _, row in tqdm(gps_df.iterrows(), total=gps_df.shape[0], desc="Processing rows")]

        # Save the updated DataFrame to a new CSV file
        output_file_path = os.path.join(folder_path, "Golo's Field Database Platform_GPS_with_Address_D7.csv")
        gps_df.to_csv(output_file_path, index=False)

        print(f"Updated DataFrame with addresses saved to {output_file_path}")
    else:
        print("Required columns are missing in the GPS DataFrame.")
else:
    print("GPS DataFrame not found.")

print("end")




