#!/usr/bin/env python3
"""
Investigate actual data sources and directory structure
Look for the source of CLIM_B and CLIM_C data differences
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

def scan_directory_structure():
    """Scan the entire data directory structure"""
    print("🔍 SCANNING DIRECTORY STRUCTURE")
    print("=" * 60)
    
    base_path = Path("/Users/boussetayassir/Desktop/POP1")
    data_paths = []
    
    # Find all potential data directories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.csv') and ('CLIM' in file or 'clim' in file.lower()):
                full_path = Path(root) / file
                data_paths.append(full_path)
                print(f"📄 Found CLIM file: {full_path}")
    
    return data_paths

def investigate_marrakech_data():
    """Check the Marrakech hierarchical data structure"""
    print("\n🏙️ INVESTIGATING MARRAKECH DATA")
    print("=" * 60)
    
    marrakech_path = Path("/Users/boussetayassir/Desktop/POP1/data/Marrakech")
    
    if not marrakech_path.exists():
        print("❌ Marrakech directory not found")
        return {}
    
    print(f"✅ Found Marrakech directory: {marrakech_path}")
    
    # List all subdirectories
    clim_data = {}
    for subdir in marrakech_path.iterdir():
        if subdir.is_dir():
            print(f"\n📂 Examining: {subdir.name}")
            
            # Look for CLIM files
            clim_files = {}
            for file in subdir.glob("*.csv"):
                if "CLIM" in file.name:
                    print(f"  📄 CLIM file: {file.name}")
                    try:
                        # Load a sample
                        df = pd.read_csv(file, encoding='utf-8-sig', nrows=10, sep=';')
                        clim_files[file.name] = df
                        print(f"     Columns: {df.columns.tolist()}")
                        print(f"     Sample values: {df.iloc[0].tolist()}")
                    except Exception as e:
                        print(f"     ❌ Error loading: {e}")
                        # Try alternative loading
                        try:
                            df = pd.read_csv(file, encoding='latin-1', nrows=10, sep=';')
                            clim_files[file.name] = df
                            print(f"     Columns (latin-1): {df.columns.tolist()}")
                        except Exception as e2:
                            print(f"     ❌ Alternative loading failed: {e2}")
            
            if clim_files:
                clim_data[subdir.name] = clim_files
    
    return clim_data

def analyze_raw_clim_files(clim_data):
    """Analyze the raw CLIM files for data differences"""
    print("\n🔬 ANALYZING RAW CLIM FILES")
    print("=" * 60)
    
    for site_name, files in clim_data.items():
        print(f"\n🏢 SITE: {site_name}")
        print("-" * 40)
        
        clim_b_data = None
        clim_c_data = None
        
        # Find CLIM B and C files
        for filename, df in files.items():
            if "CLIM B" in filename:
                clim_b_data = df
                print(f"📊 CLIM B file: {filename}")
            elif "CLIM C" in filename:
                clim_c_data = df
                print(f"📊 CLIM C file: {filename}")
        
        if clim_b_data is not None and clim_c_data is not None:
            print("\n🔍 COMPARING CLIM B vs CLIM C RAW DATA:")
            
            # Find value columns
            b_value_col = find_value_column(clim_b_data)
            c_value_col = find_value_column(clim_c_data)
            
            if b_value_col and c_value_col:
                print(f"CLIM B value column: {b_value_col}")
                print(f"CLIM C value column: {c_value_col}")
                
                b_values = clim_b_data[b_value_col].head(10).tolist()
                c_values = clim_c_data[c_value_col].head(10).tolist()
                
                print(f"CLIM B first 10 values: {b_values}")
                print(f"CLIM C first 10 values: {c_values}")
                
                # Check if they're identical
                if b_values == c_values:
                    print("🚨 RAW DATA IS IDENTICAL!")
                else:
                    print("✅ Raw data differs - investigating patterns...")
                    
                    # Check for inversion patterns
                    if len(set(b_values + c_values)) <= 2:  # Binary data
                        # Convert to binary for comparison
                        b_binary = [1 if str(v).upper() in ['ON', '1', 'TRUE'] else 0 for v in b_values]
                        c_binary = [1 if str(v).upper() in ['ON', '1', 'TRUE'] else 0 for v in c_values]
                        
                        print(f"CLIM B binary: {b_binary}")
                        print(f"CLIM C binary: {c_binary}")
                        
                        # Check for inversion
                        c_inverted = [1-x for x in c_binary]
                        if b_binary == c_inverted:
                            print("🚨 CLIM C IS INVERTED VERSION OF CLIM B!")
                        elif c_binary == [1-x for x in b_binary]:
                            print("🚨 CLIM B IS INVERTED VERSION OF CLIM C!")

def find_value_column(df):
    """Find the value column in a dataframe"""
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['value', 'val', 'status', 'état']):
            return col
    # If no specific value column, assume last column
    return df.columns[-1] if len(df.columns) > 0 else None

def load_and_compare_full_datasets():
    """Load full datasets and compare them"""
    print("\n📊 LOADING FULL DATASETS FOR COMPARISON")
    print("=" * 60)
    
    try:
        from src.incident_lens.preprocessor import DataPreprocessor
        
        # Load with different region/site combinations
        sites_to_check = [
            ("Marrakech", "BGU-ONE"),
            ("Marrakech", "BGU-TWO"), 
        ]
        
        for region, site in sites_to_check:
            try:
                print(f"\n🔍 Checking {region}/{site}")
                preprocessor = DataPreprocessor(region=region, site=site)
                data = preprocessor.load_data()
                
                if not data.empty:
                    print(f"✅ Loaded {len(data)} rows")
                    
                    # Check CLIM columns
                    clim_cols = [col for col in data.columns if 'CLIM' in col]
                    print(f"CLIM columns: {clim_cols}")
                    
                    if 'CLIM_B_Status' in data.columns and 'CLIM_C_Status' in data.columns:
                        analyze_clim_correlation(data, f"{region}/{site}")
                else:
                    print("❌ No data loaded")
            except Exception as e:
                print(f"❌ Error loading {region}/{site}: {e}")
                
    except Exception as e:
        print(f"❌ Error with preprocessor: {e}")

def analyze_clim_correlation(data, source_name):
    """Analyze CLIM correlation in a dataset"""
    print(f"\n📈 CORRELATION ANALYSIS FOR {source_name}")
    print("-" * 50)
    
    clim_b = data['CLIM_B_Status'].dropna()
    clim_c = data['CLIM_C_Status'].dropna()
    
    # Find common indices
    common_idx = clim_b.index.intersection(clim_c.index)
    if len(common_idx) == 0:
        print("❌ No common data points")
        return
    
    b_common = clim_b.loc[common_idx]
    c_common = clim_c.loc[common_idx]
    
    print(f"Common data points: {len(common_idx)}")
    print(f"CLIM B unique values: {sorted(b_common.unique())}")
    print(f"CLIM C unique values: {sorted(c_common.unique())}")
    
    # Calculate correlation
    if len(b_common) > 1 and b_common.std() > 0 and c_common.std() > 0:
        correlation = b_common.corr(c_common)
        print(f"📊 CLIM B vs C correlation: {correlation:.6f}")
        
        # Check state combinations
        state_combos = pd.crosstab(b_common, c_common, margins=True)
        print("State combinations:")
        print(state_combos)
        
        # Temperature correlations if available
        if 'T°C AMBIANTE' in data.columns:
            temp_data = data['T°C AMBIANTE'].loc[common_idx].dropna()
            if len(temp_data) > 1:
                temp_common_idx = temp_data.index.intersection(common_idx)
                if len(temp_common_idx) > 1:
                    b_temp_corr = b_common.loc[temp_common_idx].corr(temp_data.loc[temp_common_idx])
                    c_temp_corr = c_common.loc[temp_common_idx].corr(temp_data.loc[temp_common_idx])
                    
                    print(f"📊 CLIM B vs Temperature: {b_temp_corr:.6f}")
                    print(f"📊 CLIM C vs Temperature: {c_temp_corr:.6f}")
                    
                    # Check for opposite correlations
                    if abs(b_temp_corr + c_temp_corr) < 0.001:
                        print("🚨 EXACT OPPOSITE TEMPERATURE CORRELATIONS FOUND!")
                    elif abs(b_temp_corr - c_temp_corr) < 0.001:
                        print("⚠️ Identical temperature correlations")

def main():
    """Main investigation"""
    print("🔍 INVESTIGATING DATA SOURCES FOR CORRELATION ISSUE")
    print("=" * 80)
    
    # Scan directory structure
    data_paths = scan_directory_structure()
    
    # Investigate Marrakech data
    marrakech_data = investigate_marrakech_data()
    
    # Analyze raw CLIM files
    if marrakech_data:
        analyze_raw_clim_files(marrakech_data)
    
    # Load and compare full datasets
    load_and_compare_full_datasets()
    
    print("\n" + "="*80)
    print("INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()