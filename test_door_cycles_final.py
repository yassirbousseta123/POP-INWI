#!/usr/bin/env python3
import pandas as pd
from datetime import datetime, timedelta

def detect_door_cycles_correct(df, ts_col='Timestamp', status_col='Value'):
    """
    Correct cycle detection: skip consecutive open events
    """
    df_sorted = df.sort_values(ts_col).reset_index(drop=True)
    cycles_list = []
    i = 0
    
    while i < len(df_sorted):
        if df_sorted.iloc[i][status_col] == 'Ouverte' and pd.notna(df_sorted.iloc[i][ts_col]):
            open_time = df_sorted.iloc[i][ts_col]
            open_idx = i
            
            # Skip all consecutive 'Ouverte' events
            j = i + 1
            while j < len(df_sorted) and df_sorted.iloc[j][status_col] == 'Ouverte':
                j += 1
            
            # Now j points to either a 'Fermé' or end of data
            if j < len(df_sorted) and df_sorted.iloc[j][status_col] == 'Fermé':
                close_time = df_sorted.iloc[j][ts_col]
                if pd.notna(close_time):
                    duration = (close_time - open_time).total_seconds()
                    cycles_list.append({
                        'open_ts': open_time,
                        'close_ts': close_time,
                        'duration_sec': duration,
                        'open_idx': open_idx,
                        'close_idx': j
                    })
                # Move to after the close event
                i = j + 1
            else:
                # No close found, move past all the open events
                i = j
        else:
            i += 1
    
    return cycles_list

# Load data
print("Loading door data...")
df = pd.read_csv('/Users/boussetayassir/Desktop/benguerir-POP/data/Etat de porte BGU-ONE.csv', 
                 delimiter=';', 
                 encoding='utf-8-sig')

# Clean and parse timestamps
df['Timestamp_clean'] = df['Timestamp'].str.replace(' WEST', '').str.replace(' WET', '')
df['Timestamp'] = pd.to_datetime(df['Timestamp_clean'], format='%d-%b-%y %I:%M:%S %p', errors='coerce')

print(f"Loaded {len(df)} rows")
print(f"Successfully parsed: {df['Timestamp'].notna().sum()} timestamps")

# Detect cycles with correct algorithm
print("\n" + "="*80)
print("DETECTING CYCLES - Correct Algorithm (skip consecutive opens)")
print("="*80)

cycles = detect_door_cycles_correct(df)

print(f"\nTotal cycles found: {len(cycles)}")

# Show all cycles
print("\nAll detected cycles:")
for i, cycle in enumerate(cycles):
    print(f"Cycle {i+1}: [{cycle['open_idx']}→{cycle['close_idx']}] "
          f"{cycle['open_ts'].strftime('%Y-%m-%d %H:%M')} → {cycle['close_ts'].strftime('%Y-%m-%d %H:%M')} "
          f"({cycle['duration_sec']/60:.1f} min)")

# Verify specific cases
print("\n" + "="*80)
print("VERIFICATION OF SPECIFIC CASES")
print("="*80)

# Check the problematic area (indices 49-58)
print("\nData from index 49-60:")
for i in range(49, min(60, len(df))):
    ts = df.iloc[i]['Timestamp']
    val = df.iloc[i]['Value']
    ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(ts) else 'NaT'
    print(f"  [{i}] {ts_str} - {val}")

# Summary
print(f"\n{'='*80}")
print(f"FINAL RESULT: {len(cycles)} cycles detected")
print(f"{'='*80}")