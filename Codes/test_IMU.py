import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the folder path where the CSV files are located
folder_path = "C:\\My_Stuff\\Study\\4-WS-2024-25\\Einarbeitung\\Data"

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

# # Create subplots
# fig, axs = plt.subplots(2, 1, figsize=(12, 8))

# # Plot Acceleration on the first subplot
# axs[0].plot(df_filtered['Timestamp'], df_filtered['Acceleration (x)'], label='Acceleration (x)', color='r')
# axs[0].plot(df_filtered['Timestamp'], df_filtered['Acceleration (y)'], label='Acceleration (y)', color='g')
# axs[0].plot(df_filtered['Timestamp'], df_filtered['Acceleration (z)'], label='Acceleration (z)', color='b')
# axs[0].set_title(f'Acceleration over Time for Drive ID {drive_id}')
# axs[0].set_xlabel('Time')
# axs[0].set_ylabel('Acceleration')
# axs[0].legend()
# axs[0].grid(True) 


# # Plot Rate of Turn on the second subplot
# axs[1].plot(df_filtered['Timestamp'], df_filtered['Rate of turn (x)'], label='Rate of turn (x)', color='r')
# axs[1].plot(df_filtered['Timestamp'], df_filtered['Rate of turn (y)'], label='Rate of turn (y)', color='g')
# axs[1].plot(df_filtered['Timestamp'], df_filtered['Rate of turn (z)'], label='Rate of turn (z)', color='b')
# axs[1].set_title(f'Rate of Turn over Time for Drive ID {drive_id}')
# axs[1].set_xlabel('Time')
# axs[1].set_ylabel('Rate of Turn')
# axs[1].legend()
# axs[1].grid(True)

# # Adjust layout to prevent overlapping
# plt.tight_layout()

# # Show the plot
# plt.show()
#######################################################################################################

# Step 1: Calculate the acceleration magnitude (Euclidean norm)
df_filtered['Acceleration Magnitude'] = np.sqrt(df_filtered['Acceleration (x)']**2 + df_filtered['Acceleration (y)']**2 + df_filtered['Acceleration (z)']**2)

# Step 2: Calculate the rate of change (difference) of the acceleration magnitude
df_filtered['Acceleration Change'] = df_filtered['Acceleration Magnitude'].diff()

# Step 3: Identify periods of increasing or decreasing acceleration
# Mark periods where acceleration is increasing
df_filtered['Acceleration Increasing'] = df_filtered['Acceleration Change'] > 0

# Step 4: Identify the start and stop of acceleration phases
# Start where the acceleration begins (increasing) and stops where it stabilizes (decreasing or zero change)

# Create a list to store acceleration phases
acceleration_phases = []
phase_start = None

for idx, row in df_filtered.iterrows():
    if row['Acceleration Increasing'] and phase_start is None:
        # Start of a new acceleration phase
        phase_start = row['Timestamp']
    elif not row['Acceleration Increasing'] and phase_start is not None:
        # End of an acceleration phase
        phase_end = row['Timestamp']
        duration = (phase_end - phase_start).total_seconds()
        acceleration_phases.append((phase_start, phase_end, duration))
        phase_start = None  # Reset for the next phase

# Step 5: Output the identified phases
for phase in acceleration_phases:
    start, end, duration = phase
    print(f"Acceleration phase from {start} to {end}, lasting {duration:.2f} seconds")

# Optional: Plot the acceleration magnitude with the critical points highlighted
plt.figure(figsize=(10, 6))
plt.plot(df_filtered['Timestamp'], df_filtered['Acceleration Magnitude'], label='Acceleration Magnitude', color='blue')

# Highlight the start and stop times of acceleration phases
for phase in acceleration_phases:
    start, end, _ = phase
    plt.axvspan(start, end, color='red', alpha=0.3)

plt.title('Acceleration Phases Over Time')
plt.xlabel('Time')
plt.ylabel('Acceleration Magnitude')
plt.grid(True)
plt.legend()
plt.show()
########################################################################################################

# Step 1: Calculate the acceleration magnitude (Euclidean norm)
df_filtered['Acceleration Magnitude'] = np.sqrt(df_filtered['Acceleration (x)']**2 + df_filtered['Acceleration (y)']**2 + df_filtered['Acceleration (z)']**2)

# Step 2: Apply smoothing (e.g., rolling mean) to reduce noise
df_filtered['Smoothed Acceleration'] = df_filtered['Acceleration Magnitude'].rolling(window=5).mean()

# Step 3: Calculate the rate of change of the smoothed acceleration magnitude
df_filtered['Acceleration Change'] = df_filtered['Smoothed Acceleration'].diff()

# Step 4: Set a threshold for significant changes (ignore minor vibrations)
threshold = 0.02  # Adjust based on your data's characteristics
df_filtered['Significant Change'] = np.abs(df_filtered['Acceleration Change']) > threshold

# Step 5: Identify the start and stop times for significant acceleration phases
acceleration_phases = []
phase_start = None

for idx, row in df_filtered.iterrows():
    if row['Significant Change'] and phase_start is None:
        # Start of a new significant acceleration phase
        phase_start = row['Timestamp']
    elif not row['Significant Change'] and phase_start is not None:
        # End of the significant acceleration phase
        phase_end = row['Timestamp']
        duration = (phase_end - phase_start).total_seconds()
        acceleration_phases.append((phase_start, phase_end, duration))
        phase_start = None  # Reset for the next phase

# Step 6: Output the identified phases lasting more than 5 seconds
for phase in acceleration_phases:
    start, end, duration = phase
    if duration > 5:  # Only consider phases that last more than 5 seconds
        print(f"Significant acceleration phase from {start} to {end}, lasting {duration:.2f} seconds")


# Optional: Plot the smoothed acceleration magnitude with critical periods highlighted
plt.figure(figsize=(10, 6))
plt.plot(df_filtered['Timestamp'], df_filtered['Smoothed Acceleration'], label='Smoothed Acceleration Magnitude', color='blue')

# Highlight the start and stop times of significant acceleration phases
for phase in acceleration_phases:
    start, end, _ = phase
    plt.axvspan(start, end, color='red', alpha=0.3)

plt.title('Significant Acceleration Phases Over Time')
plt.xlabel('Time')
plt.ylabel('Acceleration Magnitude')
plt.grid(True)
plt.legend()
plt.show()

print('end')