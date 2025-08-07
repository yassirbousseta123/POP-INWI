#!/usr/bin/env python3
import pandas as pd
from datetime import datetime, timedelta

# Load and check raw data first
print("Loading door data...")
df_raw = pd.read_csv('/Users/boussetayassir/Desktop/benguerir-POP/data/Etat de porte BGU-ONE.csv', 
                     delimiter=';', 
                     encoding='utf-8-sig')

print(f"Loaded {len(df_raw)} rows")
print(f"Columns: {df_raw.columns.tolist()}")
print("\nFirst 5 raw timestamps:")
print(df_raw['Timestamp'].head(5).tolist())

# Remove timezone info and parse
df = df_raw.copy()
df['Timestamp_clean'] = df['Timestamp'].str.replace(' WEST', '').str.replace(' WET', '')

# Parse without timezone
df['Timestamp'] = pd.to_datetime(df['Timestamp_clean'], format='%d-%b-%y %I:%M:%S %p', errors='coerce')

# Check parsing results
print(f"\nSuccessfully parsed: {df['Timestamp'].notna().sum()} / {len(df)}")
print("\nFirst 10 parsed timestamps:")
print(df[['Timestamp', 'Value']].head(10))

# Check for open events
open_events = df[df['Value'] == 'Ouverte']
print(f"\nTotal 'Ouverte' events: {len(open_events)}")

# Simple cycle detection
print("\n" + "="*80)
print("DETECTING CYCLES - Simple Algorithm")
print("="*80)

cycles_list = []
df_sorted = df.sort_values('Timestamp').reset_index(drop=True)

for i in range(len(df_sorted)):
    if df_sorted.iloc[i]['Value'] == 'Ouverte':
        open_time = df_sorted.iloc[i]['Timestamp']
        
        # Find next Fermé
        for j in range(i + 1, len(df_sorted)):
            if df_sorted.iloc[j]['Value'] == 'Fermé':
                close_time = df_sorted.iloc[j]['Timestamp']
                
                if pd.notna(open_time) and pd.notna(close_time):
                    duration = (close_time - open_time).total_seconds()
                    cycles_list.append({
                        'open_ts': open_time,
                        'close_ts': close_time,
                        'duration_sec': duration,
                        'open_idx': i,
                        'close_idx': j
                    })
                break

print(f"\nTotal cycles found: {len(cycles_list)}")

# Show all cycles
print("\nAll detected cycles:")
for i, cycle in enumerate(cycles_list):
    print(f"Cycle {i+1}: idx {cycle['open_idx']} → {cycle['close_idx']}, "
          f"{cycle['open_ts']} → {cycle['close_ts']} "
          f"(duration: {cycle['duration_sec']/60:.1f} min)")