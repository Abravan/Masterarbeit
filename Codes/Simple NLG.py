import pandas as pd
import os
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
data = dataframes.get("Golo's Field Database Platform_recordings")

# # Define a function for text generation
# def generate_description_nlg(row):
#     template = (
#         "During a {Day/Night} drive from {Start (UTC)} to {End (UTC)}, "
#         "the weather was {Weather Conditions} with {Visibility} meters visibility. "
#         "The temperature was {Temperature[°C]}°C, and humidity was {Humidity[%]}%. "
#         "Particulate levels included PM10 at {PM_10[μg/m³]} μg/m³ and PM2.5 at {PM_25[μg/m³]} μg/m³."
#     )
#     return template.format(
#         **{
#             "Day/Night": row.get("Day/Night", "Unknown"),
#             "Start (UTC)": row.get("Start (UTC)", "Unknown"),
#             "End (UTC)": row.get("End (UTC)", "Unknown"),
#             "Weather Conditions": row.get("Weather Conditions", "Unknown"),
#             "Visibility": row.get("Visibility", "Unknown"),
#             "Temperature[°C]": row.get("Temperature[°C]", "Unknown"),  # Safely access the column
#             "Humidity[%]": row.get("Humidity[%]", "Unknown"),
#             "PM_10[μg/m³]": row.get("PM_10[μg/m³]", "Unknown"),
#             "PM_25[μg/m³]": row.get("PM_25[μg/m³]", "Unknown"),
#         }
#     )

# Step 1: Remove special characters from column names and strip extra spaces
data.columns = data.columns.str.replace(r'[^\w\s]', '', regex=True).str.strip()

# Step 2: Print column names to confirm the cleaning
print("Cleaned column names:", data.columns)

# Step 3: Define the updated template using the correct cleaned column names
def generate_description_nlg(row):
    template = (
        "During a {DayNight} drive from {Start_UTC} to {End_UTC}, "
        "the weather was {Weather_Conditions} with {Visibility} meters visibility. "
        "The temperature was {TemperatureC}°C, and humidity was {Humidity}%. "
        "Particulate levels included PM10 at {PM_10} μg/m³ and PM2_5 at {PM_25} μg/m³."
    )
    return template.format(
        **{
            "DayNight": row["DayNight"],  # Updated column name
            "Start_UTC": row["Start UTC"],  # Updated column name
            "End_UTC": row["End UTC"],  # Updated column name
            "Weather_Conditions": row["Weather Conditions"],  # Updated column name
            "Visibility": row["Visibility"],
            "TemperatureC": row["TemperatureC"],  # Updated column name
            "Humidity": row["Humidity"],  # Updated column name
            "PM_10": row["PM_10μgm³"],  # Updated column name
            "PM_25": row["PM_25μgm³"],  # Updated column name
        }
    )

# Apply the function to each row and generate individual descriptions
data['Description'] = data.apply(generate_description_nlg, axis=1)

# Concatenate all individual descriptions into one long text
full_description = "\n\n".join(data['Description'])

# Print the full description (for all drives)
print(full_description)
