#!/usr/bin/env python3
"""
Deep Investigation of CLIM_B vs CLIM_C Correlation Issue
Investigates the exact opposite correlation values (-0.140 vs +0.140)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

def load_and_process_data():
    """Load data using the same pipeline as the app"""
    try:
        # Import the actual data loader used by the app
        from data_loader import DataCleaner
        from src.incident_lens.preprocessor import DataPreprocessor
        
        # Load data using both approaches to compare
        results = {}
        
        # Method 1: Original DataCleaner
        print("=== LOADING WITH DATACLEANER ===")
        cleaner = DataCleaner()
        raw_data = cleaner.load_all_data()
        merged_data_cleaner = cleaner.merge_all_data(raw_data)
        results['datacleaner'] = merged_data_cleaner
        
        # Method 2: Preprocessor
        print("\n=== LOADING WITH PREPROCESSOR ===")
        preprocessor = DataPreprocessor()
        merged_data_preprocessor = preprocessor.load_data()
        results['preprocessor'] = merged_data_preprocessor
        
        # Method 3: Direct CSV load
        print("\n=== LOADING MERGED SAMPLE DIRECTLY ===")
        sample_path = Path("/Users/boussetayassir/Desktop/POP1/merged_data_sample.csv")
        if sample_path.exists():
            merged_sample = pd.read_csv(sample_path)
            merged_sample['Timestamp'] = pd.to_datetime(merged_sample['Timestamp'])
            results['sample'] = merged_sample
        
        return results
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def analyze_correlation_patterns(data_dict):
    """Analyze correlation patterns across different data loading methods"""
    
    print("\n" + "="*80)
    print("CORRELATION ANALYSIS ACROSS DATA LOADING METHODS")
    print("="*80)
    
    correlations_summary = {}
    
    for method_name, df in data_dict.items():
        if df is None or df.empty:
            print(f"\n❌ {method_name.upper()}: No data available")
            continue
            
        print(f"\n📊 {method_name.upper()} ANALYSIS")
        print("-" * 40)
        
        # Find CLIM columns
        clim_b_cols = [col for col in df.columns if 'CLIM_B' in col or 'clim_b' in col.lower()]
        clim_c_cols = [col for col in df.columns if 'CLIM_C' in col or 'clim_c' in col.lower()]
        temp_cols = [col for col in df.columns if 'Temp' in col or 'AMBIANTE' in col]
        
        print(f"CLIM_B columns found: {clim_b_cols}")
        print(f"CLIM_C columns found: {clim_c_cols}")
        print(f"Temperature columns found: {temp_cols}")
        
        if not clim_b_cols or not clim_c_cols:
            print("❌ Missing CLIM_B or CLIM_C columns")
            continue
            
        clim_b_col = clim_b_cols[0]
        clim_c_col = clim_c_cols[0]
        
        # Get clean data
        clean_data = df.dropna(subset=[clim_b_col, clim_c_col])
        
        if len(clean_data) == 0:
            print("❌ No clean data available")
            continue
            
        print(f"Clean data points: {len(clean_data)}")
        
        # Analyze CLIM values
        print("\nCLIM Value Analysis:")
        b_values = clean_data[clim_b_col]
        c_values = clean_data[clim_c_col]
        
        print(f"CLIM_B unique values: {sorted(b_values.unique())}")
        print(f"CLIM_C unique values: {sorted(c_values.unique())}")
        print(f"CLIM_B value counts: {b_values.value_counts().to_dict()}")
        print(f"CLIM_C value counts: {c_values.value_counts().to_dict()}")
        
        # State combinations
        print("\nState Combinations:")
        state_combinations = pd.crosstab(b_values, c_values, margins=True)
        print(state_combinations)
        
        # Calculate correlations
        correlations = {}
        
        # B vs C correlation
        try:
            bc_corr, bc_p = pearsonr(b_values, c_values)
            correlations['B_vs_C'] = bc_corr
            print(f"\n📈 CLIM_B vs CLIM_C correlation: {bc_corr:.6f} (p={bc_p:.6f})")
        except Exception as e:
            print(f"❌ Error calculating B vs C correlation: {e}")
            
        # Temperature correlations
        for temp_col in temp_cols:
            if temp_col in clean_data.columns:
                temp_data = clean_data[temp_col].dropna()
                if len(temp_data) > 1:
                    # Align data
                    aligned_df = clean_data.dropna(subset=[clim_b_col, clim_c_col, temp_col])
                    if len(aligned_df) > 1:
                        try:
                            b_temp_corr, b_temp_p = pearsonr(aligned_df[clim_b_col], aligned_df[temp_col])
                            c_temp_corr, c_temp_p = pearsonr(aligned_df[clim_c_col], aligned_df[temp_col])
                            
                            correlations[f'B_vs_{temp_col}'] = b_temp_corr
                            correlations[f'C_vs_{temp_col}'] = c_temp_corr
                            
                            print(f"📈 CLIM_B vs {temp_col}: {b_temp_corr:.6f} (p={b_temp_p:.6f})")
                            print(f"📈 CLIM_C vs {temp_col}: {c_temp_corr:.6f} (p={c_temp_p:.6f})")
                            
                            # Check for exact opposite correlations
                            if abs(b_temp_corr + c_temp_corr) < 0.001:
                                print("🚨 EXACT OPPOSITE CORRELATIONS DETECTED!")
                                
                        except Exception as e:
                            print(f"❌ Error calculating temperature correlations: {e}")
        
        correlations_summary[method_name] = correlations
        
        # Advanced pattern analysis
        analyze_temporal_patterns(clean_data, clim_b_col, clim_c_col, method_name)
        
    return correlations_summary

def analyze_temporal_patterns(df, clim_b_col, clim_c_col, method_name):
    """Analyze temporal patterns in CLIM status changes"""
    print(f"\n🔍 TEMPORAL PATTERN ANALYSIS ({method_name})")
    print("-" * 40)
    
    if 'Timestamp' in df.columns:
        df_sorted = df.sort_values('Timestamp').reset_index(drop=True)
    else:
        df_sorted = df.reset_index(drop=True)
    
    # Look for state change patterns
    b_changes = df_sorted[clim_b_col].diff()
    c_changes = df_sorted[clim_c_col].diff()
    
    # Find simultaneous changes
    simultaneous_changes = ((b_changes != 0) & (c_changes != 0)).sum()
    opposite_changes = ((b_changes * c_changes) < 0).sum()  # Changes in opposite directions
    
    print(f"Total state changes - B: {(b_changes != 0).sum()}, C: {(c_changes != 0).sum()}")
    print(f"Simultaneous changes: {simultaneous_changes}")
    print(f"Opposite direction changes: {opposite_changes}")
    
    # Check for data inversion patterns
    detect_data_inversion(df_sorted, clim_b_col, clim_c_col, method_name)

def detect_data_inversion(df, clim_b_col, clim_c_col, method_name):
    """Detect potential data inversion issues"""
    print(f"\n🔎 DATA INVERSION DETECTION ({method_name})")
    print("-" * 40)
    
    # Look for patterns that suggest data swapping/inversion
    issues_found = []
    
    # Pattern 1: Check if B and C have identical sequences but shifted
    b_values = df[clim_b_col].values
    c_values = df[clim_c_col].values
    
    if len(b_values) > 10:  # Need enough data
        # Check for identical sequences
        if np.array_equal(b_values, c_values):
            issues_found.append("IDENTICAL_SEQUENCES")
        
        # Check for inverted sequences (B = 1-C)
        if np.array_equal(b_values, 1 - c_values):
            issues_found.append("PERFECTLY_INVERTED")
        
        # Check for shifted sequences
        for shift in range(1, min(5, len(b_values)//4)):
            if np.array_equal(b_values[shift:], c_values[:-shift]):
                issues_found.append(f"SHIFTED_BY_{shift}")
            if np.array_equal(b_values[:-shift], c_values[shift:]):
                issues_found.append(f"REVERSE_SHIFTED_BY_{shift}")
    
    # Pattern 2: Check timestamp alignment issues
    if 'Timestamp' in df.columns:
        check_timestamp_alignment(df, clim_b_col, clim_c_col, issues_found)
    
    # Pattern 3: Check for column mapping errors in preprocessing
    check_preprocessing_artifacts(df, clim_b_col, clim_c_col, issues_found)
    
    if issues_found:
        print("🚨 DATA INVERSION ISSUES FOUND:")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("✅ No obvious data inversion patterns detected")
    
    return issues_found

def check_timestamp_alignment(df, clim_b_col, clim_c_col, issues_found):
    """Check for timestamp-related alignment issues"""
    
    # Look for rows where only one CLIM value is present
    b_only = df[clim_b_col].notna() & df[clim_c_col].isna()
    c_only = df[clim_c_col].notna() & df[clim_b_col].isna()
    
    b_only_count = b_only.sum()
    c_only_count = c_only.sum()
    
    if b_only_count > 0 or c_only_count > 0:
        issues_found.append(f"MISALIGNED_DATA_B:{b_only_count}_C:{c_only_count}")
    
    # Check for duplicate timestamps with different CLIM values
    if 'Timestamp' in df.columns:
        duplicated_timestamps = df[df['Timestamp'].duplicated(keep=False)]
        if len(duplicated_timestamps) > 0:
            issues_found.append(f"DUPLICATE_TIMESTAMPS:{len(duplicated_timestamps)}")

def check_preprocessing_artifacts(df, clim_b_col, clim_c_col, issues_found):
    """Check for artifacts from data preprocessing"""
    
    # Look for non-standard values that might indicate processing errors
    b_values = df[clim_b_col].dropna()
    c_values = df[clim_c_col].dropna()
    
    # Check for unexpected value ranges
    b_range = [b_values.min(), b_values.max()]
    c_range = [c_values.min(), c_values.max()]
    
    if not (set(b_values.unique()).issubset({0, 1, 0.0, 1.0})):
        issues_found.append(f"NON_BINARY_B_VALUES:{b_values.unique()}")
    
    if not (set(c_values.unique()).issubset({0, 1, 0.0, 1.0})):
        issues_found.append(f"NON_BINARY_C_VALUES:{c_values.unique()}")

def investigate_column_mapping():
    """Investigate how columns are mapped during processing"""
    print("\n" + "="*80)
    print("COLUMN MAPPING INVESTIGATION")
    print("="*80)
    
    # Check the data loader column mappings
    try:
        from data_loader import DataCleaner
        cleaner = DataCleaner()
        
        # Look at the data file mappings
        print("\n📁 DATA FILE MAPPINGS:")
        data_files = {
            'clim_a': 'Etat CLIM A.csv',
            'clim_b': 'Etat CLIM B.csv',
            'clim_c': 'Etat CLIM C.csv',
            'clim_d': 'Etat CLIM D.csv',
        }
        
        for key, filename in data_files.items():
            print(f"{key}: {filename}")
        
        # Check if files exist and load samples
        base_path = cleaner.data_dir
        print(f"\nBase data directory: {base_path}")
        
        clim_files = {}
        for key, filename in data_files.items():
            file_path = base_path / filename
            if file_path.exists():
                print(f"✅ Found: {filename}")
                try:
                    # Load a small sample
                    sample_df = cleaner.load_and_clean_csv(file_path)
                    if not sample_df.empty:
                        clim_files[key] = sample_df.head(10)
                        print(f"   Sample columns: {sample_df.columns.tolist()}")
                        print(f"   Sample values: {sample_df.iloc[:3, -1].tolist()}")
                except Exception as e:
                    print(f"   ❌ Error loading: {e}")
            else:
                print(f"❌ Missing: {filename}")
        
        return clim_files
        
    except Exception as e:
        print(f"❌ Error investigating column mapping: {e}")
        return {}

def create_visual_analysis(data_dict):
    """Create visualizations to understand the correlation issue"""
    print("\n" + "="*80)
    print("VISUAL ANALYSIS")
    print("="*80)
    
    # Create plots for each data source
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('CLIM Status Analysis Across Data Loading Methods', fontsize=16)
    
    plot_idx = 0
    for method_name, df in data_dict.items():
        if df is None or df.empty or plot_idx >= 4:
            continue
        
        row = plot_idx // 2
        col = plot_idx % 2
        ax = axes[row, col]
        
        # Find CLIM columns
        clim_b_cols = [col for col in df.columns if 'CLIM_B' in col or 'clim_b' in col.lower()]
        clim_c_cols = [col for col in df.columns if 'CLIM_C' in col or 'clim_c' in col.lower()]
        
        if clim_b_cols and clim_c_cols:
            b_col = clim_b_cols[0]
            c_col = clim_c_cols[0]
            
            # Clean data
            clean_df = df.dropna(subset=[b_col, c_col])
            
            if len(clean_df) > 0:
                # Scatter plot
                ax.scatter(clean_df[b_col], clean_df[c_col], alpha=0.6)
                ax.set_xlabel(f'CLIM_B ({b_col})')
                ax.set_ylabel(f'CLIM_C ({c_col})')
                ax.set_title(f'{method_name.upper()}\n{len(clean_df)} points')
                
                # Add correlation text
                try:
                    corr, _ = pearsonr(clean_df[b_col], clean_df[c_col])
                    ax.text(0.05, 0.95, f'r = {corr:.4f}', 
                           transform=ax.transAxes, 
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                except:
                    pass
                
                # Grid for clarity
                ax.grid(True, alpha=0.3)
        
        plot_idx += 1
    
    # Remove empty subplots
    for i in range(plot_idx, 4):
        row = i // 2
        col = i % 2
        axes[row, col].remove()
    
    plt.tight_layout()
    plt.savefig('/Users/boussetayassir/Desktop/POP1/clim_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Visual analysis saved as: clim_correlation_analysis.png")

def main():
    """Main investigation function"""
    print("🔍 INVESTIGATING CLIM_B vs CLIM_C CORRELATION ISSUE")
    print("=" * 80)
    print("Looking for data quality issues causing opposite correlations...")
    
    # Load data using different methods
    data_dict = load_and_process_data()
    
    if not data_dict:
        print("❌ No data could be loaded for analysis")
        return
    
    # Analyze correlations
    correlations = analyze_correlation_patterns(data_dict)
    
    # Investigate column mappings
    clim_files = investigate_column_mapping()
    
    # Create visualizations
    create_visual_analysis(data_dict)
    
    # Summary report
    print("\n" + "="*80)
    print("INVESTIGATION SUMMARY")
    print("="*80)
    
    print("\n📊 CORRELATION SUMMARY:")
    for method, corrs in correlations.items():
        print(f"\n{method.upper()}:")
        for metric, value in corrs.items():
            print(f"  {metric}: {value:.6f}")
    
    # Look for the exact opposite correlation issue
    opposite_found = False
    for method, corrs in correlations.items():
        temp_corrs = {k: v for k, v in corrs.items() if 'Temp' in k or 'AMBIANTE' in k}
        temp_corr_values = list(temp_corrs.values())
        
        for i in range(len(temp_corr_values)):
            for j in range(i+1, len(temp_corr_values)):
                if abs(temp_corr_values[i] + temp_corr_values[j]) < 0.001:
                    opposite_found = True
                    print(f"\n🚨 EXACT OPPOSITE CORRELATIONS FOUND in {method}!")
                    print(f"   Correlation 1: {temp_corr_values[i]:.6f}")
                    print(f"   Correlation 2: {temp_corr_values[j]:.6f}")
                    print(f"   Sum: {temp_corr_values[i] + temp_corr_values[j]:.6f}")
    
    if not opposite_found:
        print("\n✅ No exact opposite correlations found in current data")
        print("   This suggests the issue may be:")
        print("   - In a different time period")
        print("   - In the live processing pipeline")
        print("   - Related to specific data subsets")
    
    # Recommendations
    print("\n🔧 RECOMMENDATIONS:")
    print("1. Check the live data processing pipeline for column swapping")
    print("2. Verify timestamp alignment during data merging")
    print("3. Examine the preprocessor's column mapping logic")
    print("4. Check if different time periods show the opposite correlation issue")
    print("5. Validate that CLIM_B and CLIM_C sensor data sources are correct")
    
    return correlations

if __name__ == "__main__":
    main()