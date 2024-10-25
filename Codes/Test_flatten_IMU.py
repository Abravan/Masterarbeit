import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate the slope between points
def calculate_slope(series):
    return np.gradient(series)

# Function to detect vibration based on both acceleration magnitude and slope
def detect_vibrations(df, magnitude_threshold, slope_threshold):
    df['Magnitude Change'] = df['Smoothed Magnitude'].diff().abs()
    df['Slope'] = calculate_slope(df['Smoothed Magnitude'])

    # Mark vibrations where magnitude changes significantly and the slope is steep (but not long-term slope)
    df['Vibration'] = (df['Magnitude Change'] > magnitude_threshold) & (df['Slope'].abs() > slope_threshold)
    
    return df

# Get the current directory where the script is running
current_directory = os.getcwd()

# Go one folder back (to the parent directory) and then into the 'Data' folder
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
folder_path = os.path.join(parent_directory, "Data")

# List all the CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Create a dictionary to store DataFrame
dataframes = {}

# Loop through each CSV file and read it into a DataFrame
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df_name = os.path.splitext(file)[0]  # Get the file name without extension
    dataframes[df_name] = pd.read_csv(file_path)  # Read CSV into a DataFrame and store it in the dictionary

# Accessing DataFrame
IMU_df = dataframes.get("Golo's Field Database Platform_IMU")

# Define the Drive ID you want to filter
drive_id = 7

# Filter the DataFrame by Drive ID
df_filtered = IMU_df[IMU_df['Drive ID'] == drive_id]

# Convert Unix Timestamp to a readable datetime format (nanoseconds to seconds)
df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Unix Timestamp'], unit='ns')

# Step 1: Calculate the acceleration magnitude (Euclidean norm)
df_filtered['Acceleration Magnitude'] = np.sqrt(df_filtered['Acceleration (x)']**2 + df_filtered['Acceleration (y)']**2 + df_filtered['Acceleration (z)']**2)

# Smoothing the data using a rolling window to reduce noise
df_filtered['Smoothed Magnitude'] = df_filtered['Acceleration Magnitude'].rolling(window=5).mean()

# Step 2: Define thresholds for identifying vibrations
# Magnitude threshold can be adjusted based on the dataset
magnitude_threshold = df_filtered['Smoothed Magnitude'].mean() + 1.0 * df_filtered['Smoothed Magnitude'].std()
slope_threshold = df_filtered['Smoothed Magnitude'].std() * 0.8  # Adjust this based on what you consider "steep"

# Detect vibrations using both magnitude and slope criteria
df_filtered = detect_vibrations(df_filtered, magnitude_threshold, slope_threshold)

# Step 4: Find vibration segments
vibration_phases = []
phase_start = None

for idx, row in df_filtered.iterrows():
    if row['Vibration'] and phase_start is None:
        # Start of a new vibration phase
        phase_start = row['Timestamp']
    elif not row['Vibration'] and phase_start is not None:
        # End of a vibration phase
        phase_end = row['Timestamp']
        duration = (phase_end - phase_start).total_seconds()
        vibration_phases.append((phase_start, phase_end, duration))
        phase_start = None  # Reset for the next phase

# Step 5: Compute average acceleration during each vibration period
average_accelerations = []

for phase in vibration_phases:
    start, end, duration = phase
    mask = (df_filtered['Timestamp'] >= start) & (df_filtered['Timestamp'] <= end)
    avg_accel = df_filtered.loc[mask, 'Acceleration Magnitude'].mean()
    average_accelerations.append((start, end, avg_accel))

# Step 6: Create a new column 'Flattened Acceleration' for the flattened result
df_filtered['Flattened Acceleration'] = df_filtered['Acceleration Magnitude']

# Step 7: Flatten the acceleration only during vibration periods
for start, end, avg_accel in average_accelerations:
    mask = (df_filtered['Timestamp'] >= start) & (df_filtered['Timestamp'] <= end)
    df_filtered.loc[mask, 'Flattened Acceleration'] = avg_accel  # Set flattened values during vibration

# Step 8: Plot the results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

# Plot 1: Original Acceleration Magnitude
ax1.plot(df_filtered['Timestamp'], df_filtered['Acceleration Magnitude'], label='Acceleration Magnitude', color='blue')
ax1.set_title('Original Acceleration Magnitude')
ax1.set_xlabel('Time')
ax1.set_ylabel('Acceleration Magnitude')
ax1.grid(True)

# Plot 2: Vibration periods with flattened acceleration (dots) during vibrations
ax2.plot(df_filtered['Timestamp'], df_filtered['Acceleration Magnitude'], label='Original Acceleration', color='blue', alpha=0.6)
ax2.plot(df_filtered['Timestamp'], df_filtered['Flattened Acceleration'], label='Flattened during Vibration', color='red', linestyle='None', marker='o')  # Use dots for flattened acceleration

# Highlight vibration periods with shading
for start, end, avg_accel in average_accelerations:
    ax2.axvspan(start, end, color='red', alpha=0.2)  # Highlight the vibration periods
    # Optionally: add green trendlines (remove if you don't want)
    ax2.hlines(y=avg_accel, xmin=start, xmax=end, colors='green', linewidth=2)

ax2.set_title('Flattened Acceleration During Vibration Periods')
ax2.set_xlabel('Time')
ax2.set_ylabel('Acceleration Magnitude')
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()

print('end')