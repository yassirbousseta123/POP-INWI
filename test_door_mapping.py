#!/usr/bin/env python3
import pandas as pd

# Test the mapping
print("Testing door status mapping...")

# Sample data
test_data = pd.DataFrame({
    'Status': ['Ouverte', 'Fermé', 'Fermée', 'FERME', 'FERMEE', 'ouverte', 'fermé'],
})

# The mapping from data_loader
mapping = {
    'Ouverte': 1, 'Ouvert': 1, 'OUVERTE': 1,
    'Fermé': 0, 'Fermée': 0, 'FERME': 0, 'FERMEE': 0
}

# Test mapping
test_data['Mapped'] = test_data['Status'].map(mapping)

print("\nMapping results:")
print(test_data)

# Load actual door data and test
df = pd.read_csv('/Users/boussetayassir/Desktop/benguerir-POP/data/Etat de porte BGU-ONE.csv', 
                 delimiter=';', encoding='utf-8-sig')

print(f"\n\nActual data columns: {df.columns.tolist()}")
print(f"First 10 'Value' entries:")
print(df['Value'].head(10))

# Check unique values
print(f"\nUnique values in 'Value' column:")
unique_vals = df['Value'].unique()
for val in unique_vals:
    print(f"  '{val}' (type: {type(val).__name__})")

# Test the mapping
df['Mapped'] = df['Value'].map(mapping)
print(f"\nMapping results:")
print(f"Non-null mapped values: {df['Mapped'].notna().sum()}")
print(f"Null mapped values: {df['Mapped'].isna().sum()}")

# Show where mapping failed
failed = df[df['Mapped'].isna() & df['Value'].notna()]
if len(failed) > 0:
    print(f"\nFailed mappings:")
    print(failed[['Value', 'Mapped']].head())