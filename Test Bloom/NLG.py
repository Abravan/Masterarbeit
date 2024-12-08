import pandas as pd

# Load the CSV file (replace with your actual file path)
file_path = "results.csv"  # Ensure this points to your CSV file
data = pd.read_csv(file_path)

# Ensure correct data types
data['time'] = pd.to_datetime(data['time'])  # Convert time column to datetime

# Summary of Route Information
unique_locations = data['location'].nunique()
most_common_location = data['location'].mode()[0]
location_summary = data['location'].value_counts().head(5)  # Top 5 locations by occurrence

# Speed Analysis
average_speed = data['speed_kmh'].mean()
max_speed = data['speed_kmh'].max()
min_speed = data['speed_kmh'].min()
max_speed_row = data.loc[data['speed_kmh'].idxmax()]
min_speed_row = data.loc[data['speed_kmh'].idxmin()]

# Speed changes
speed_diff = data['speed_kmh'].diff().abs()
significant_speed_changes = speed_diff[speed_diff > 10].count()

# Acceleration Analysis
average_acceleration = data['total_acceleration'].mean()
max_acceleration = data['total_acceleration'].max()
min_acceleration = data['total_acceleration'].min()
max_accel_row = data.loc[data['total_acceleration'].idxmax()]
min_accel_row = data.loc[data['total_acceleration'].idxmin()]

# Drastic Acceleration Changes
accel_diff = data['total_acceleration'].diff().abs()
significant_accel_changes = accel_diff[accel_diff > 2].count()

# Generate a Natural-Language Summary
summary = f"""
### Ride Summary
- **Total Data Points:** {len(data)}
- **Unique Locations Visited:** {unique_locations}
  - Most Common Location: {most_common_location}
  - Top Locations: 
    {location_summary.to_string()}

### Speed Statistics
- **Average Speed:** {average_speed:.2f} km/h
- **Maximum Speed:** {max_speed:.2f} km/h at {max_speed_row['time']} ({max_speed_row['location']})
- **Minimum Speed:** {min_speed:.2f} km/h at {min_speed_row['time']} ({min_speed_row['location']})
- **Significant Speed Changes (>10 km/h):** {significant_speed_changes}

### Acceleration Statistics
- **Average Acceleration:** {average_acceleration:.2f} m/s²
- **Maximum Acceleration:** {max_acceleration:.2f} m/s² at {max_accel_row['time']} ({max_accel_row['location']})
- **Minimum Acceleration:** {min_acceleration:.2f} m/s² at {min_accel_row['time']} ({min_accel_row['location']})
- **Significant Acceleration Changes (>2 m/s²):** {significant_accel_changes}

### Notable Observations
- The ride experienced {significant_speed_changes} significant speed changes and {significant_accel_changes} drastic changes in acceleration.
- The most frequently visited location was {most_common_location}.
"""

# Print the summary
print(summary)
