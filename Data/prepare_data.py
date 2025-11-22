import pandas as pd
import random
import os

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '911.csv'))

print(f"Loaded {len(df)} rows")
print(df.head())

print("Columns:", df.columns)

print("\nMissing values:\n", df.isnull().sum())

# Renaming columns for clarity
df.rename(columns={
    'lat': 'latitude',
    'lng': 'longitude',
    'desc': 'description',
    'zip': 'zipcode',
    'title': 'emergency_title',
    'timeStamp': 'timestamp',
    'twp': 'township',
    'addr': 'address',
    'e': 'priority_flag'
}, inplace=True)

# Split emergency title into type and subtype
df[['emergency_type', 'emergency_subtype']] = df['emergency_title'].str.split(pat=':', n=1, expand=True)

# Remove whitespaces
df['emergency_type'] = df['emergency_type'].str.strip()
df['emergency_subtype'] = df['emergency_subtype'].str.strip()

#simulated demographic columns
df['caller_gender'] = [random.choice(['Male', 'Female']) for _ in range(len(df))]
df['caller_age'] = [random.randint(18, 65) for _ in range(len(df))]
df['response_time'] = [random.randint(5, 30) for _ in range(len(df))]

# Clean timestamps
df['timestamp'] = df['timestamp'].str.replace(';', '', regex=False).str.replace('@', '', regex=False).str.strip()
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

print("\nDate range after cleaning:")
print(f"Earliest: {df['timestamp'].min()}")
print(f"Latest: {df['timestamp'].max()}")
print("\nRecords per year:")
print(df['timestamp'].dt.year.value_counts().sort_index())

# Drop rows where timestamp conversion failed
df = df.dropna(subset=['timestamp'])

#MySQL format
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save with new name
df.to_csv(os.path.join(os.path.dirname(__file__), 'cleaned_data_full.csv'), index=False)
print(f"\nData saved to cleaned_data_full.csv with {len(df)} total rows")