import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import find_peaks, savgol_filter

# Set the specific path to the CSV file 
data_ma_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_MA', '3', 'Rec_1'))
csv_file_name = "Psoncms.csv"

# Construct the full path
csv_file_path = os.path.join(data_ma_dir, csv_file_name)

# Check if the file exists
if os.path.exists(csv_file_path):
    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)
else:
    raise FileNotFoundError(f"{csv_file_name} not found in {data_ma_dir}")


# Convert Unix timestamp to readable time
df['time'] = pd.to_datetime(df['UNIX timestamp'], unit='ns')

# Calculate total acceleration
df['total_acceleration'] = np.sqrt(df['a_x']**2 + df['a_y']**2 + df['a_z']**2)

# Apply Savitzky-Golay filter to denoise the signal
df['denoised_acceleration'] = savgol_filter(df['total_acceleration'], window_length=11, polyorder=2)

# Identify peaks (local maxima) in the original noisy signal
peaks, _ = find_peaks(df['total_acceleration'], height=None, distance=10)

# Identify valleys (local minima) by inverting the signal
valleys, _ = find_peaks(-df['total_acceleration'], height=None, distance=10)

# Plot the noisy and denoised signals
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['total_acceleration'], label='Noisy Signal', color='blue', alpha=0.7)
plt.plot(df['time'], df['denoised_acceleration'], label='Denoised Signal', color='green', linewidth=2)

# Highlight peaks and valleys
plt.scatter(df['time'].iloc[peaks], df['total_acceleration'].iloc[peaks], color='red', label='Peaks')
plt.scatter(df['time'].iloc[valleys], df['total_acceleration'].iloc[valleys], color='orange', label='Valleys')

# Add labels and legend
plt.xlabel('Time')
plt.ylabel('Total Acceleration (m/s²)')
plt.title('Total Acceleration with Peaks, Valleys, and Denoised Signal')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

print('end')

