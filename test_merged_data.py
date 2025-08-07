#!/usr/bin/env python3
from data_loader import DataCleaner
import pandas as pd

print("Testing merged data door status...")

# Load data as the app does
cleaner = DataCleaner()
data = cleaner.load_all_data()
merged_data = cleaner.merge_all_data(data)

print(f"\nMerged data shape: {merged_data.shape}")
print(f"Columns: {merged_data.columns.tolist()}")

if 'Porte_Status' in merged_data.columns:
    print("\n=== DOOR STATUS ANALYSIS ===")
    porte_data = merged_data[['Timestamp', 'Porte_Status']].copy()
    
    # Remove NaN
    porte_data_clean = porte_data[porte_data['Porte_Status'].notna()].copy()
    
    print(f"Total records: {len(porte_data)}")
    print(f"Non-null records: {len(porte_data_clean)}")
    print(f"Data type: {porte_data_clean['Porte_Status'].dtype}")
    print(f"Unique values: {sorted(porte_data_clean['Porte_Status'].unique())}")
    
    # Count by value
    value_counts = porte_data_clean['Porte_Status'].value_counts().sort_index()
    print("\nValue counts:")
    for val, count in value_counts.items():
        print(f"  {val}: {count}")
    
    # Show some records where door is open
    open_records = porte_data_clean[porte_data_clean['Porte_Status'] == 1]
    print(f"\nRecords where door is open (1): {len(open_records)}")
    if len(open_records) > 0:
        print("First 10 open events:")
        print(open_records.head(10))
    
    # Test the cycle detection logic
    print("\n=== TESTING CYCLE DETECTION ===")
    
    # Simple algorithm
    cycles_list = []
    df_sorted = porte_data_clean.sort_values('Timestamp').reset_index(drop=True)
    i = 0
    
    while i < len(df_sorted):
        if df_sorted.iloc[i]['Porte_Status'] == 1:  # Open
            open_time = df_sorted.iloc[i]['Timestamp']
            
            # Skip consecutive opens
            j = i + 1
            while j < len(df_sorted) and df_sorted.iloc[j]['Porte_Status'] == 1:
                j += 1
            
            # Find close
            if j < len(df_sorted) and df_sorted.iloc[j]['Porte_Status'] == 0:
                close_time = df_sorted.iloc[j]['Timestamp']
                duration = (close_time - open_time).total_seconds()
                cycles_list.append({
                    'open_ts': open_time,
                    'close_ts': close_time,
                    'duration_min': duration / 60
                })
                i = j + 1
            else:
                i = j
        else:
            i += 1
    
    print(f"Cycles detected: {len(cycles_list)}")
    if len(cycles_list) > 0:
        print("\nFirst 5 cycles:")
        for idx, cycle in enumerate(cycles_list[:5]):
            print(f"  Cycle {idx+1}: {cycle['open_ts']} → {cycle['close_ts']} ({cycle['duration_min']:.1f} min)")
else:
    print("\nNo Porte_Status column found in merged data!")