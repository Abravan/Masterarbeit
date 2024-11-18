from transformers import pipeline
import os
import pandas as pd

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
# Step 1: Remove special characters from column names and strip extra spaces
data.columns = data.columns.str.replace(r'[^\w\s]', '', regex=True).str.strip()
print("Cleaned column names:", data.columns)

# Load GPT-Neo model from HuggingFace pipeline
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')

# Function to generate a description based on data row
def generate_description(row):
    prompt = (
        f"Generate a driving scenario description based on the following data:\n"
        f"- Drive time: {row['Start UTC']} to {row['End UTC']}\n"
        f"- Time of day: {row['DayNight']}\n"
        f"- Weather: {row['Weather Conditions']}\n"
        f"- Visibility: {row['Visibility']} meters\n"
        f"- Temperature: {row['TemperatureC']}°C\n"
        f"- Humidity: {row['Humidity']}%\n"
        f"- PM10: {row['PM_10μgm³']} μg/m³, PM2.5: {row['PM_25μgm³']} μg/m³\n\n"
        f"Write a detailed description of the driving scenario based on these conditions."
    )
    
    # Generate text using the model
    response = generator(prompt, max_length=200, num_return_sequences=1)
    return response[0]['generated_text']

# Example: Generate descriptions for the first 5 rows
for i in range(min(5, len(data))):  # Limiting to first 5 rows for testing
    description = generate_description(data.iloc[i])
    print(f"Description for row {i+1}:\n{description}\n\n")
    
print('end')