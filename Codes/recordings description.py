import pandas as pd
import os
# Load the CSV file
# Get the current directory where the script is running
current_directory = os.getcwd()

# Go one folder back (to the parent directory) and then into the 'Data' folder
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
folder_path = os.path.join(parent_directory, "Data")
dataframes = {}
# List all the CSV files in the 'Data' folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
# Loop through each CSV file and read it into a DataFrame
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df_name = os.path.splitext(file)[0]  # Get the file name without extension
    dataframes[df_name] = pd.read_csv(file_path)  # Read CSV into a DataFrame and store it in the dictionary

# Accessing individual DataFrames
df = dataframes.get("Golo's Field Database Platform_recordings")


# Function to classify temperature
def classify_temperature(temp):
    if temp < 0:
        return "cold"
    elif 0 <= temp <= 18:
        return "cool"
    elif 18 < temp <= 30:
        return "warm"
    else:
        return "hot"

# Function to generate descriptive text for each drive
def generate_description(row):
    temp_description = classify_temperature(row['Temperature[°C]'])
    description = (
        f"Drive ID {row['Drive ID']} was recorded from {row['Start (UTC)']} to {row['End (UTC)']} "
        f"at the location with latitude {row['Latitude NMEA']} and longitude {row['Longitude NMEA']}. "
        f"The drive occurred during the {row['Day/Night'].lower()} under {row['Weather Conditions'].lower()} "
        f"conditions. The temperature was {row['Temperature[°C]']}°C, which is considered {temp_description}, "
        f"and the humidity level was {row['Humidity[%]']}%."
    )
    return description

# Apply the description generation function to each row in the dataframe
df['Description'] = df.apply(generate_description, axis=1)

# Save the descriptions to a new CSV file or print them
df[['Drive ID', 'Description']].to_csv('drive_descriptions.csv', index=False)

# Optionally print the descriptions
for description in df['Description']:
    print(description)
print('end')