import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM

# Step 1: Load BLOOM model and tokenizer
model_name = "bigscience/bloom-560m"  # You can choose a larger model if needed
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Step 2: Load the CSV file
file_path = "results.csv"  # Replace with the path to your file
data = pd.read_csv(file_path)

# Ensure time column is in datetime format
data['time'] = pd.to_datetime(data['time'])

# Step 3: Analyze the data
# Route Summary
unique_locations = data['location'].nunique()
most_common_location = data['location'].mode()[0]
top_locations = data['location'].value_counts().head(5).to_dict()

# Speed Summary
average_speed = data['speed_kmh'].mean()
max_speed = data['speed_kmh'].max()
min_speed = data['speed_kmh'].min()
max_speed_time = data.loc[data['speed_kmh'].idxmax(), 'time']
min_speed_time = data.loc[data['speed_kmh'].idxmin(), 'time']

# Acceleration Summary
average_acceleration = data['total_acceleration'].mean()
max_acceleration = data['total_acceleration'].max()
min_acceleration = data['total_acceleration'].min()
max_accel_time = data.loc[data['total_acceleration'].idxmax(), 'time']
min_accel_time = data.loc[data['total_acceleration'].idxmin(), 'time']

# Step 4: Prepare prompt for BLOOM
# Refined prompt
prompt = """
Analyze and summarize the following ride data. Provide a clear and concise summary of key insights without repetition.

- Total Data Points: 869
- Unique Locations Visited: 7
- Most Common Location: Auf der Horst 24, 30823 Garbsen, Germany
- Top 5 Locations: {'Auf der Horst 24, 30823 Garbsen, Germany': 313, 'Auf der Horst 29, 30823 Garbsen, Germany': 293, 'Auf der Horst 35, 30823 Garbsen, Germany': 126, 'Auf der Horst 22, 30823 Garbsen, Germany': 98, 'Auf der Horst 31, 30823 Garbsen, Germany': 19}

Speed:
- Average Speed: 7.10 km/h
- Maximum Speed: 34.83 km/h at 2023-11-28 15:16:07.828696917
- Minimum Speed: 0.02 km/h at 2023-11-28 15:16:26.528707606

Acceleration:
- Average Acceleration: 9.86 m/s²
- Maximum Acceleration: 16.95 m/s² at 2023-11-28 15:16:07.328700015
- Minimum Acceleration: 3.06 m/s² at 2023-11-28 15:16:07.928678211

Generate a detailed summary, focusing on significant changes in speed and acceleration and the route overview.
"""

# Tokenize input and generate output
inputs = tokenizer(prompt, return_tensors="pt")
output = model.generate(
    inputs["input_ids"],
    max_new_tokens=200,  # Limit only the generated tokens to 200
    temperature=0.7,
    top_p=0.9
)

# Decode and print the response
response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)