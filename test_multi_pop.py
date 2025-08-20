#!/usr/bin/env python3
"""
Test script for Multi-POP correlation feature
"""

import sys
import pandas as pd
from data_loader import DataCleaner

def test_multi_pop_loading():
    """Test the multi-POP loading functionality"""
    print("🧪 Testing Multi-POP Data Loading Feature")
    print("=" * 50)
    
    # Initialize DataCleaner
    cleaner = DataCleaner()
    
    # Test 1: Get available regions
    print("\n📍 Test 1: Get available regions")
    regions = cleaner.get_regions()
    print(f"Found {len(regions)} regions: {regions[:3]}...")
    
    # Test 2: Get POPs for first region
    if regions:
        test_region = regions[0]
        print(f"\n📍 Test 2: Get POPs for region '{test_region}'")
        pops = cleaner.get_pops(test_region)
        print(f"Found {len(pops)} POPs in {test_region}")
        if pops:
            print(f"First 3 POPs: {pops[:3]}")
    
    # Test 3: Load data for a few POPs
    print("\n📍 Test 3: Load data for multiple POPs")
    test_pops = []
    for region in regions[:2]:  # Test with first 2 regions
        region_pops = cleaner.get_pops(region)
        for pop in region_pops[:2]:  # Take first 2 POPs from each
            test_pops.append((region, pop))
    
    if test_pops:
        print(f"Loading data for {len(test_pops)} POPs...")
        all_pops_data = cleaner.load_multiple_pops(pop_list=test_pops[:3])  # Limit to 3 for quick test
        
        if all_pops_data:
            print(f"✅ Successfully loaded {len(all_pops_data)} POPs")
            
            # Test 4: Calculate correlations
            print("\n📍 Test 4: Calculate correlations")
            correlation_df = cleaner.calculate_pop_correlations(all_pops_data)
            
            if not correlation_df.empty:
                print(f"✅ Calculated correlations for {len(correlation_df)} POPs")
                print("\nSample correlation results:")
                print(correlation_df[['Region', 'POP', 'Temp_Ambiante_Mean', 'Data_Points']].head())
                
                # Check for correlation columns
                corr_cols = [col for col in correlation_df.columns if 'Spearman' in col]
                print(f"\nFound {len(corr_cols)} correlation metrics")
                if corr_cols:
                    print(f"Sample correlations: {corr_cols[:3]}")
            else:
                print("❌ No correlation data generated")
        else:
            print("❌ Failed to load POP data")
    else:
        print("❌ No POPs found to test")
    
    print("\n" + "=" * 50)
    print("✅ Multi-POP feature test completed!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_multi_pop_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)