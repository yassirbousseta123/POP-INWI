#!/usr/bin/env python3
"""
Data Quality Analysis for CLIM Status Values
Investigates why CLIM_B and CLIM_C have opposite correlations
"""

import pandas as pd
import numpy as np
from collections import Counter

def analyze_clim_states(csv_file):
    """Analyze CLIM status patterns and data quality issues"""
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    print("=== DATA QUALITY ANALYSIS FOR CLIM STATUS ===\n")
    
    # Basic info
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")
    print()
    
    # Check for missing values in CLIM columns
    clim_cols = ['CLIM_A_Status', 'CLIM_B_Status', 'CLIM_C_Status', 'CLIM_D_Status']
    print("=== MISSING DATA ANALYSIS ===")
    for col in clim_cols:
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        print(f"{col}: {missing_count} missing ({missing_pct:.1f}%)")
    
    # Filter rows where we have both CLIM_B and CLIM_C data
    valid_bc = df.dropna(subset=['CLIM_B_Status', 'CLIM_C_Status'])
    print(f"\nRows with both CLIM_B and CLIM_C data: {len(valid_bc)}")
    
    if len(valid_bc) == 0:
        print("ERROR: No rows found with both CLIM_B and CLIM_C data!")
        return
    
    # Analyze CLIM_B and CLIM_C state combinations
    print("\n=== CLIM_B and CLIM_C STATE COMBINATIONS ===")
    
    # Create state combination analysis
    combinations = []
    for _, row in valid_bc.iterrows():
        b_state = row['CLIM_B_Status']
        c_state = row['CLIM_C_Status']
        temp = row['Temp_Ambiante']
        combinations.append({
            'B_state': b_state,
            'C_state': c_state,
            'temp': temp,
            'combination': f"B={b_state}, C={c_state}"
        })
    
    combo_df = pd.DataFrame(combinations)
    combo_counts = combo_df['combination'].value_counts()
    
    print("State combination counts:")
    for combo, count in combo_counts.items():
        pct = (count / len(combo_df)) * 100
        print(f"  {combo}: {count} times ({pct:.1f}%)")
    
    # Check for opposite states (B=1,C=0 or B=0,C=1)
    opposite_states = combo_df[
        ((combo_df['B_state'] == 1.0) & (combo_df['C_state'] == 0.0)) |
        ((combo_df['B_state'] == 0.0) & (combo_df['C_state'] == 1.0))
    ]
    
    same_states = combo_df[
        ((combo_df['B_state'] == 1.0) & (combo_df['C_state'] == 1.0)) |
        ((combo_df['B_state'] == 0.0) & (combo_df['C_state'] == 0.0))
    ]
    
    print(f"\nOpposite states (B≠C): {len(opposite_states)} occurrences")
    print(f"Same states (B=C): {len(same_states)} occurrences")
    
    if len(opposite_states) > 0:
        print("\n=== OPPOSITE STATE ANALYSIS ===")
        print("Times when B and C are in opposite states:")
        for _, row in opposite_states.iterrows():
            print(f"  B={row['B_state']}, C={row['C_state']}, Temp={row['temp']}")
    
    # Temperature analysis for different states
    print("\n=== TEMPERATURE ANALYSIS BY STATE ===")
    
    # Group by state combinations and analyze temperature
    for combo in combo_counts.index:
        mask = combo_df['combination'] == combo
        temps = combo_df[mask]['temp'].dropna()
        if len(temps) > 0:
            print(f"{combo}: Temp range {temps.min():.1f}-{temps.max():.1f}°C, "
                  f"mean {temps.mean():.1f}°C, count {len(temps)}")
    
    # Calculate correlations to understand the issue
    print("\n=== CORRELATION ANALYSIS ===")
    
    # Only use rows with temperature data for correlation
    corr_data = valid_bc.dropna(subset=['Temp_Ambiante'])
    
    if len(corr_data) > 1:
        b_temp_corr = corr_data['CLIM_B_Status'].corr(corr_data['Temp_Ambiante'])
        c_temp_corr = corr_data['CLIM_C_Status'].corr(corr_data['Temp_Ambiante'])
        bc_corr = corr_data['CLIM_B_Status'].corr(corr_data['CLIM_C_Status'])
        
        print(f"CLIM_B vs Temperature: {b_temp_corr:.4f}")
        print(f"CLIM_C vs Temperature: {c_temp_corr:.4f}")
        print(f"CLIM_B vs CLIM_C: {bc_corr:.4f}")
        
        # Check if correlations are exactly opposite
        if abs(b_temp_corr + c_temp_corr) < 0.001:
            print("⚠️  WARNING: CLIM_B and CLIM_C correlations are exactly opposite!")
            print("   This suggests a data inversion issue.")
    
    # Check for data inversion patterns
    print("\n=== DATA INVERSION DETECTION ===")
    
    # Look for temporal patterns that might indicate inversion
    clim_a_data = valid_bc.dropna(subset=['CLIM_A_Status', 'Temp_Ambiante'])
    clim_b_data = valid_bc.dropna(subset=['CLIM_B_Status', 'Temp_Ambiante'])
    clim_c_data = valid_bc.dropna(subset=['CLIM_C_Status', 'Temp_Ambiante'])
    
    if len(clim_a_data) > 1:
        a_temp_corr = clim_a_data['CLIM_A_Status'].corr(clim_a_data['Temp_Ambiante'])
        print(f"CLIM_A vs Temperature: {a_temp_corr:.4f}")
    
    # Check for impossible value patterns
    print("\n=== VALUE VALIDATION ===")
    
    for col in clim_cols:
        unique_values = df[col].dropna().unique()
        print(f"{col} unique values: {sorted(unique_values)}")
        
        # Check for non-binary values
        non_binary = [v for v in unique_values if v not in [0.0, 1.0]]
        if non_binary:
            print(f"  ⚠️  Non-binary values found: {non_binary}")
    
    # Check timestamp patterns
    print("\n=== TIMESTAMP ANALYSIS ===")
    
    # Look for duplicate or problematic timestamps
    df['timestamp_parsed'] = pd.to_datetime(df['Timestamp'])
    duplicated_timestamps = df[df['timestamp_parsed'].duplicated()]
    
    if len(duplicated_timestamps) > 0:
        print(f"⚠️  Found {len(duplicated_timestamps)} rows with duplicate timestamps")
        print("Sample duplicate timestamps:")
        for ts in duplicated_timestamps['Timestamp'].head(5):
            print(f"  {ts}")
    
    # Look for rows with xxx:xx:01 timestamps (potential merge artifacts)
    second_01_rows = df[df['Timestamp'].str.contains(':01', na=False)]
    print(f"Rows with :01 seconds (potential merge artifacts): {len(second_01_rows)}")
    
    return {
        'total_rows': len(df),
        'valid_bc_rows': len(valid_bc),
        'opposite_states': len(opposite_states),
        'same_states': len(same_states),
        'combo_counts': combo_counts.to_dict()
    }

if __name__ == "__main__":
    results = analyze_clim_states('/Users/boussetayassir/Desktop/POP1/merged_data_sample.csv')
    print("\n=== SUMMARY ===")
    print(f"Analysis complete. Found {results['opposite_states']} opposite states out of {results['valid_bc_rows']} valid data points.")