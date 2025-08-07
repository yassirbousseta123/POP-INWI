#!/usr/bin/env python3
from data_loader import DataCleaner
import pandas as pd

print("Testing door data loading only...")

# Load just door data
cleaner = DataCleaner()
all_data = cleaner.load_all_data()

if 'porte' in all_data:
    door_data = all_data['porte']
    print(f"\nDoor data shape: {door_data.shape}")
    print(f"Columns: {door_data.columns.tolist()}")
    print(f"\nFirst 20 rows:")
    print(door_data.head(20))
    
    # Check values
    if 'Value' in door_data.columns:
        print(f"\nValue counts:")
        print(door_data['Value'].value_counts())
        
        # Count by numeric value
        open_count = (door_data['Value'] == 1).sum()
        close_count = (door_data['Value'] == 0).sum()
        print(f"\nOpen events (1): {open_count}")
        print(f"Close events (0): {close_count}")
else:
    print("No door data found!")