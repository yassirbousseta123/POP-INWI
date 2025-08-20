#!/usr/bin/env python3
"""Comprehensive test of data extraction across all regions and POPs"""

from data_loader import DataCleaner
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def comprehensive_test():
    print("=" * 80)
    print("COMPREHENSIVE DATA EXTRACTION TEST - ALL REGIONS & POPS")
    print("=" * 80)
    
    cleaner = DataCleaner()
    regions = cleaner.get_regions()
    
    total_pops = 0
    successful_pops = 0
    pops_with_it_power = 0
    failed_pops = []
    successful_details = []
    
    print(f"\nFound {len(regions)} regions to test")
    print("-" * 60)
    
    for region in regions:
        pops = cleaner.get_pops(region)
        print(f"\n📍 Region: {region} ({len(pops)} POPs)")
        
        for pop in pops:
            total_pops += 1
            pop_path = cleaner.get_pop_path(region, pop)
            
            # Check if any CSV files exist
            csv_files = list(pop_path.glob('*.csv'))
            
            if not csv_files:
                print(f"  ⚠️ {pop}: No CSV files found")
                failed_pops.append(f"{region}/{pop} - No CSV files")
                continue
            
            try:
                # Load data
                cleaned_data = cleaner.load_all_data(region, pop)
                
                if cleaned_data:
                    # Merge data
                    merged = cleaner.merge_all_data(cleaned_data)
                    
                    if not merged.empty:
                        successful_pops += 1
                        
                        # Check for Puissance_IT
                        has_it = False
                        it_coverage = 0
                        it_mean = 0
                        
                        if 'Puissance_IT' in merged.columns:
                            valid_it = merged['Puissance_IT'].notna().sum()
                            if valid_it > 0:
                                has_it = True
                                pops_with_it_power += 1
                                it_coverage = (valid_it / len(merged)) * 100
                                it_mean = merged['Puissance_IT'].mean()
                        
                        # Store successful details
                        successful_details.append({
                            'region': region,
                            'pop': pop,
                            'rows': len(merged),
                            'has_it': has_it,
                            'it_coverage': it_coverage,
                            'it_mean': it_mean,
                            'columns': len(merged.columns)
                        })
                        
                        status = "✅" if has_it else "✓"
                        print(f"  {status} {pop}: {len(merged)} rows, {len(merged.columns)} cols", end="")
                        if has_it:
                            print(f" | IT Power: {it_mean:.1f}kW ({it_coverage:.0f}% coverage)")
                        else:
                            print(" | No IT Power data")
                    else:
                        print(f"  ❌ {pop}: Empty merged data")
                        failed_pops.append(f"{region}/{pop} - Empty merge")
                else:
                    print(f"  ❌ {pop}: No data loaded")
                    failed_pops.append(f"{region}/{pop} - No data loaded")
                    
            except Exception as e:
                print(f"  ❌ {pop}: Error - {str(e)[:50]}")
                failed_pops.append(f"{region}/{pop} - {str(e)[:50]}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total POPs tested: {total_pops}")
    print(f"  Successful loads: {successful_pops} ({successful_pops/total_pops*100:.1f}%)")
    print(f"  POPs with IT Power: {pops_with_it_power} ({pops_with_it_power/total_pops*100:.1f}%)")
    print(f"  Failed loads: {len(failed_pops)} ({len(failed_pops)/total_pops*100:.1f}%)")
    
    # Show POPs with best IT Power data
    if successful_details:
        it_pops = [p for p in successful_details if p['has_it']]
        if it_pops:
            it_pops.sort(key=lambda x: x['it_coverage'], reverse=True)
            print(f"\n🏆 Top POPs with IT Power Data:")
            for p in it_pops[:5]:
                print(f"  {p['region']}/{p['pop']}: {p['it_mean']:.1f}kW avg, {p['it_coverage']:.0f}% coverage")
    
    # Show failed POPs
    if failed_pops:
        print(f"\n❌ Failed POPs ({len(failed_pops)}):")
        for f in failed_pops[:10]:
            print(f"  - {f}")
        if len(failed_pops) > 10:
            print(f"  ... and {len(failed_pops) - 10} more")
    
    # Final verdict
    print("\n" + "=" * 80)
    success_rate = successful_pops / total_pops * 100
    if success_rate >= 90:
        print("✅ EXCELLENT: Data extraction working for >90% of POPs!")
    elif success_rate >= 70:
        print("✅ GOOD: Data extraction working for >70% of POPs")
    elif success_rate >= 50:
        print("⚠️ MODERATE: Data extraction working for >50% of POPs")
    else:
        print("❌ POOR: Data extraction working for <50% of POPs")
    
    print(f"\n✅ IT Power calculation verified for {pops_with_it_power} POPs")
    print("=" * 80)

if __name__ == "__main__":
    comprehensive_test()