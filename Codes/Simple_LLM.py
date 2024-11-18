import openai
import os
import pandas as pd
import time
from openai.error import RateLimitError

openai.api_key =""
# Function to generate text using OpenAI GPT
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
# Function to generate text using OpenAI GPT
# Function to generate text using OpenAI GPT
def generate_description_llm(row):
    prompt = (
        f"Generate a driving scenario description based on the following data:\n"
        f"- Drive time: {row['Start UTC']} to {row['End UTC']}\n"
        f"- Time of day: {row['DayNight']}\n"
        f"- Weather: {row['Weather Conditions']}\n"
        f"- Visibility: {row['Visibility']} meters\n"
        f"- Temperature: {row['TemperatureC']}°C\n"
        f"- Humidity: {row['Humidity']}%\n"
        f"- PM10: {row['PM_10μgm³']} μg/m³, PM2.5: {row['PM_25μgm³']} μg/m³\n\n"
        f"Write a detailed description:"
    )

     # Retry logic in case of rate limit error
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Replace with your chosen model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response['choices'][0]['message']['content'].strip()
        except RateLimitError:
            print("Rate limit exceeded. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying

# Example: Generate text for a single row
example_row = data.iloc[0]
description = generate_description_llm(example_row)
print(description)