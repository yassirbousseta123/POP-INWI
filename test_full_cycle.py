#!/usr/bin/env python3
from data_loader import DataCleaner
import pandas as pd

print("=== FULL CYCLE DETECTION TEST ===\n")

# Load data using DataCleaner
cleaner = DataCleaner()
data = cleaner.load_all_data()

# Check door data before merge
print("1. DOOR DATA BEFORE MERGE:")
if 'porte' in data:
    door_data = data['porte']
    print(f"   Shape: {door_data.shape}")
    if 'Value' in door_data.columns:
        print(f"   Value counts: {dict(door_data['Value'].value_counts())}")
    print()

# Merge data
merged_data = cleaner.merge_all_data(data)

# Check door data after merge
print("2. DOOR DATA AFTER MERGE:")
if 'Porte_Status' in merged_data.columns:
    door_status = merged_data['Porte_Status']
    print(f"   Total rows in merged: {len(merged_data)}")
    print(f"   Non-null door status: {door_status.notna().sum()}")
    print(f"   Value counts: {dict(door_status.value_counts())}")
    
    # Get just the door events
    door_events = merged_data[merged_data['Porte_Status'].notna()][['Timestamp', 'Porte_Status']].copy()
    print(f"\n3. DOOR EVENTS ONLY:")
    print(f"   Total events: {len(door_events)}")
    print(f"   Open (1): {(door_events['Porte_Status'] == 1).sum()}")
    print(f"   Close (0): {(door_events['Porte_Status'] == 0).sum()}")
    
    # Show first 20 events
    print("\n   First 20 events:")
    for i, row in door_events.head(20).iterrows():
        print(f"   {row['Timestamp']} - {row['Porte_Status']}")
    
    # Test cycle detection
    print("\n4. CYCLE DETECTION TEST:")
    cycles = []
    df_sorted = door_events.sort_values('Timestamp').reset_index(drop=True)
    i = 0
    
    while i < len(df_sorted):
        if df_sorted.iloc[i]['Porte_Status'] == 1:
            open_time = df_sorted.iloc[i]['Timestamp']
            
            # Skip consecutive opens
            j = i + 1
            while j < len(df_sorted) and df_sorted.iloc[j]['Porte_Status'] == 1:
                j += 1
            
            # Find close
            if j < len(df_sorted) and df_sorted.iloc[j]['Porte_Status'] == 0:
                close_time = df_sorted.iloc[j]['Timestamp']
                cycles.append((open_time, close_time))
                i = j + 1
            else:
                i = j
        else:
            i += 1
    
    print(f"   Cycles detected: {len(cycles)}")
    if cycles:
        print("\n   First 5 cycles:")
        for idx, (open_t, close_t) in enumerate(cycles[:5]):
            duration = (close_t - open_t).total_seconds() / 60
            print(f"   Cycle {idx+1}: {open_t} → {close_t} ({duration:.1f} min)")
else:
    print("   No Porte_Status column in merged data!")