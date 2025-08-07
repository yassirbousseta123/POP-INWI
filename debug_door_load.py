#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

# Simulate the data loading process from data_loader.py
data_dir = Path('/Users/boussetayassir/Desktop/benguerir-POP/data')
file_path = data_dir / 'Etat de porte BGU-ONE.csv'

print(f"Loading {file_path.name}...")

# Step 1: Load raw data
df = pd.read_csv(
    file_path,
    delimiter=';',
    skiprows=2,  # Skip first 2 lines
    names=['Timestamp', 'Trend Flags', 'Status', 'Value'],
    encoding='utf-8-sig',
    on_bad_lines='skip'
)

print(f"Step 1 - Raw load: {len(df)} rows")
print(f"Value column unique values: {df['Value'].unique()}")
print(f"Value counts:\n{df['Value'].value_counts()}")

# Step 2: Process timestamps
df['Timestamp'] = df['Timestamp'].str.strip()
df['Timestamp'] = (
    df['Timestamp']
    .str.replace(r'\s+(WEST|WET|GMT|UTC|CET|CEST)$', '', regex=True)
)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

print(f"\nStep 2 - After timestamp processing: {len(df)} rows")
print(f"Timestamps with NaN: {df['Timestamp'].isna().sum()}")

# Step 3: Drop NaN timestamps
df = df.dropna(subset=['Timestamp'])

print(f"\nStep 3 - After dropping NaN timestamps: {len(df)} rows")

# Step 4: Map door values
print(f"\nStep 4 - Mapping door values...")
print(f"Before mapping - Value counts:\n{df['Value'].value_counts()}")

value_col = 'Value'
df[value_col] = df[value_col].map({
    'Ouverte': 1, 'Ouvert': 1, 'OUVERTE': 1,
    'Fermé': 0, 'Fermée': 0, 'FERME': 0, 'FERMEE': 0
})

print(f"After mapping - Value counts:\n{df['Value'].value_counts()}")

# Show some records where value = 0
zeros = df[df['Value'] == 0]
print(f"\nRecords with Value=0: {len(zeros)}")
if len(zeros) > 0:
    print("First 5 records with Value=0:")
    print(zeros.head())

# Show the final data
print(f"\nFinal data shape: {df.shape}")
print("First 20 rows:")
print(df.head(20))