import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import find_peaks, savgol_filter
from opencage.geocoder import OpenCageGeocode
from tqdm import tqdm

# Set the specific path to the CSV file 
data_ma_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_MA', '3', 'Rec_1'))
csv_file_name_imu = "Psoncms.csv"
csv_file_name_gps = "gprmc.csv"

# Construct the full path
csv_file_path_imu = os.path.join(data_ma_dir, csv_file_name_imu)
csv_file_path_gps = os.path.join(data_ma_dir, csv_file_name_gps)

# Check if the file exists
if os.path.exists(csv_file_path_imu):
    # Load the CSV into a DataFrame
    df_IMU = pd.read_csv(csv_file_path_imu)
else:
    raise FileNotFoundError(f"{csv_file_name_imu} not found in {data_ma_dir}")

if os.path.exists(csv_file_path_gps):
    # Load the CSV into a DataFrame
    df_GPS = pd.read_csv(csv_file_path_gps)
else:
    raise FileNotFoundError(f"{csv_file_name_gps} not found in {data_ma_dir}")

# Initialize the geocoder with your actual API key
api_key = '3df64903c6bc4bdaaefc314da1fb93c6'  
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
    
# Check if the DataFrame was loaded correctly
if df_GPS is not None:
    # Ensure columns exist and convert NMEA coordinates to decimal degrees
    if ('Latitude NMEA' in df_GPS.columns and 
        'Longitude NMEA' in df_GPS.columns and 
        'Indicator Latitude NMEA' in df_GPS.columns and 
        'Indicator Longitude NMEA' in df_GPS.columns):
        
        df_GPS['Latitude Decimal'] = df_GPS.apply(
            lambda row: nmea_to_decimal(row['Latitude NMEA'], row['Indicator Latitude NMEA']),
            axis=1
        )
        df_GPS['Longitude Decimal'] = df_GPS.apply(
            lambda row: nmea_to_decimal(row['Longitude NMEA'], row['Indicator Longitude NMEA']),
            axis=1
        )

        # Print the output for debugging
        print(df_GPS[['Latitude NMEA', 'Longitude NMEA', 'Latitude Decimal', 'Longitude Decimal']])
        
        # Perform reverse geocoding and add the address column with a progress bar
        df_GPS['location'] = [reverse_geocode(row['Latitude Decimal'], row['Longitude Decimal']) 
                             for _, row in tqdm(df_GPS.iterrows(), total=df_GPS.shape[0], desc="Processing rows")]

        print("Updated DataFrame")
    else:
        print("Required columns are missing in the GPS DataFrame.")
else:
    print("GPS DataFrame not found.")
    
# Process IMU Data
# Convert Unix timestamp to readable time
df_IMU['time'] = pd.to_datetime(df_IMU['UNIX timestamp'], unit='ns')
# Calculate total acceleration
df_IMU['total_acceleration'] = np.sqrt(df_IMU['a_x']**2 + df_IMU['a_y']**2 + df_IMU['a_z']**2)
# Apply Savitzky-Golay filter to denoise the signal
df_IMU['denoised_acceleration'] = savgol_filter(df_IMU['total_acceleration'], window_length=11, polyorder=2)

# Identify peaks (local maxima) in the original noisy signal
peaks, _ = find_peaks(df_IMU['total_acceleration'], height=None, distance=10)

# Identify valleys (local minima) by inverting the signal
valleys, _ = find_peaks(-df_IMU['total_acceleration'], height=None, distance=10)

# Plot the noisy and denoised signals
plt.figure(figsize=(12, 6))
plt.plot(df_IMU['time'], df_IMU['total_acceleration'], label='Noisy Signal', color='blue', alpha=0.7)
plt.plot(df_IMU['time'], df_IMU['denoised_acceleration'], label='Denoised Signal', color='green', linewidth=2)

# Highlight peaks and valleys
plt.scatter(df_IMU['time'].iloc[peaks], df_IMU['total_acceleration'].iloc[peaks], color='red', label='Peaks')
plt.scatter(df_IMU['time'].iloc[valleys], df_IMU['total_acceleration'].iloc[valleys], color='orange', label='Valleys')

# Add labels and legend
plt.xlabel('Time')
plt.ylabel('Total Acceleration (m/s²)')
plt.title('Total Acceleration with Peaks, Valleys, and Denoised Signal')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Process GPS Data
# Convert GPS timestamp to time
df_GPS['time'] = pd.to_datetime(df_GPS['UNIX timestamp'], unit='ns')  
# Convert knots to km/h
df_GPS['speed_kmh'] = df_GPS['Speed [Knots]'] * 1.852  

# Plot Speed vs Time
plt.figure(figsize=(12, 6))
plt.plot(df_GPS['time'], df_GPS['speed_kmh'], label='Speed (km/h)', color='purple', linewidth=2)
plt.xlabel('Time')
plt.ylabel('Speed (km/h)')
plt.title('Speed Over Time')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Merge the DataFrames
df_merged = pd.merge_asof(
    df_IMU.sort_values('UNIX timestamp'),  # Sort by timestamp for merging
    df_GPS.sort_values('UNIX timestamp'),
    on='UNIX timestamp',
    suffixes=('_imu', '_gps')
)

# Select only relevant columns for merged DataFrame
df_merged = df_merged[['UNIX timestamp', 'time_imu', 'total_acceleration', 'denoised_acceleration', 'speed_kmh', 'location']]
df_merged.rename(columns={'time_imu': 'time'}, inplace=True)

# Save the merged DataFrame
df_merged.to_csv("results.csv", index=False)

# Plot Total Acceleration and Speed on the Same Graph
plt.figure(figsize=(12, 6))
plt.plot(df_merged['time'], df_merged['total_acceleration'], label='Total Acceleration (m/s²)', color='blue', alpha=0.7)
plt.plot(df_merged['time'], df_merged['speed_kmh'], label='Speed (km/h)', color='purple', linewidth=2)
plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Total Acceleration and Speed Over Time')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

print('end')

