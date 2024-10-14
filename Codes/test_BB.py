import pandas as pd

# Sample DataFrame with Longitude values
data = {
    'Longitude NMEA': [938.584, 938.725, 938.200]
}
gps_df = pd.DataFrame(data)

# Function to convert NMEA longitude to decimal degrees
def nmea_to_decimal(coord):
    # Convert to string in case it's not
    coord_str = str(coord)
    
    # Extract degrees and minutes
    degrees = int(coord_str[0])  # First character for degrees
    minutes = float(coord_str[1:])  # Remaining characters for minutes

    # Convert to decimal degrees
    decimal = degrees + (minutes / 60)
    
    return decimal

# Apply the conversion to create a new column
gps_df['Longitude Decimal'] = gps_df['Longitude NMEA'].apply(nmea_to_decimal)

# Display the updated DataFrame
print(gps_df)
