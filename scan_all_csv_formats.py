#!/usr/bin/env python3
"""Scan all CSV files to identify different formats and delimiters"""

import os
from pathlib import Path
import pandas as pd

def scan_csv_formats():
    print("=" * 80)
    print("SCANNING ALL CSV FILES FOR FORMAT VARIATIONS")
    print("=" * 80)
    
    data_dir = Path("/Users/boussetayassir/Desktop/POP1/data")
    
    # Dictionary to store format patterns
    formats = {
        'delimiters': set(),
        'encodings': {},
        'header_patterns': set(),
        'files_by_delimiter': {';': [], ',': [], '|': [], 'mixed': []},
        'problematic_files': []
    }
    
    total_files = 0
    
    # Walk through all directories
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.csv'):
                total_files += 1
                file_path = Path(root) / file
                relative_path = file_path.relative_to(data_dir)
                
                print(f"\n📄 Checking: {relative_path}")
                
                try:
                    # Try to read first few lines with different encodings
                    encodings_to_try = ['utf-8', 'utf-8-sig', 'ISO-8859-1', 'cp1252', 'latin1']
                    successful_encoding = None
                    first_lines = []
                    
                    for encoding in encodings_to_try:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                first_lines = [f.readline().strip() for _ in range(5)]
                                successful_encoding = encoding
                                break
                        except (UnicodeDecodeError, Exception):
                            continue
                    
                    if not successful_encoding:
                        formats['problematic_files'].append(str(relative_path))
                        print(f"  ❌ Could not read file with any encoding")
                        continue
                    
                    formats['encodings'][str(relative_path)] = successful_encoding
                    
                    # Analyze delimiters
                    header = first_lines[0] if first_lines else ""
                    data_line = first_lines[1] if len(first_lines) > 1 else ""
                    
                    # Clean BOM if present
                    header = header.replace('\ufeff', '').replace('ï»¿', '')
                    
                    # Check delimiters in header
                    semicolon_count_header = header.count(';')
                    comma_count_header = header.count(',')
                    pipe_count_header = header.count('|')
                    
                    # Check delimiters in data
                    semicolon_count_data = data_line.count(';')
                    comma_count_data = data_line.count(',')
                    pipe_count_data = data_line.count('|')
                    
                    print(f"  📊 Header delimiters - Semicolon: {semicolon_count_header}, Comma: {comma_count_header}, Pipe: {pipe_count_header}")
                    print(f"  📊 Data delimiters - Semicolon: {semicolon_count_data}, Comma: {comma_count_data}, Pipe: {pipe_count_data}")
                    print(f"  🔤 Encoding: {successful_encoding}")
                    
                    # Determine primary delimiter
                    if semicolon_count_header > 0 and comma_count_data > semicolon_count_data:
                        # Mixed format: semicolon in header, comma in data
                        formats['files_by_delimiter']['mixed'].append(str(relative_path))
                        formats['delimiters'].add('mixed: ; header, , data')
                        print(f"  ⚠️  MIXED FORMAT: Semicolon header, comma data")
                    elif pipe_count_header > max(semicolon_count_header, comma_count_header):
                        formats['files_by_delimiter']['|'].append(str(relative_path))
                        formats['delimiters'].add('|')
                    elif semicolon_count_header > comma_count_header:
                        formats['files_by_delimiter'][';'].append(str(relative_path))
                        formats['delimiters'].add(';')
                    elif comma_count_header > 0:
                        formats['files_by_delimiter'][','].append(str(relative_path))
                        formats['delimiters'].add(',')
                    else:
                        formats['problematic_files'].append(str(relative_path))
                        print(f"  ⚠️  No clear delimiter found")
                    
                    # Store header pattern
                    formats['header_patterns'].add(header[:50] + "..." if len(header) > 50 else header)
                    
                except Exception as e:
                    formats['problematic_files'].append(str(relative_path))
                    print(f"  ❌ Error: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Total CSV files scanned: {total_files}")
    
    print(f"\n📁 Files by delimiter:")
    print(f"  Semicolon (;): {len(formats['files_by_delimiter'][';'])} files")
    print(f"  Comma (,): {len(formats['files_by_delimiter'][','])} files")
    print(f"  Pipe (|): {len(formats['files_by_delimiter']['|'])} files")
    print(f"  Mixed format: {len(formats['files_by_delimiter']['mixed'])} files")
    
    print(f"\n🔤 Encodings used:")
    encoding_counts = {}
    for enc in formats['encodings'].values():
        encoding_counts[enc] = encoding_counts.get(enc, 0) + 1
    for enc, count in encoding_counts.items():
        print(f"  {enc}: {count} files")
    
    if formats['files_by_delimiter']['mixed']:
        print(f"\n⚠️  Files with MIXED format (need special handling):")
        for f in formats['files_by_delimiter']['mixed'][:5]:  # Show first 5
            print(f"  - {f}")
        if len(formats['files_by_delimiter']['mixed']) > 5:
            print(f"  ... and {len(formats['files_by_delimiter']['mixed']) - 5} more")
    
    if formats['files_by_delimiter']['|']:
        print(f"\n📝 Files using PIPE delimiter:")
        for f in formats['files_by_delimiter']['|'][:5]:
            print(f"  - {f}")
        if len(formats['files_by_delimiter']['|']) > 5:
            print(f"  ... and {len(formats['files_by_delimiter']['|']) - 5} more")
    
    if formats['problematic_files']:
        print(f"\n❌ Problematic files ({len(formats['problematic_files'])}):")
        for f in formats['problematic_files'][:5]:
            print(f"  - {f}")
        if len(formats['problematic_files']) > 5:
            print(f"  ... and {len(formats['problematic_files']) - 5} more")
    
    return formats

if __name__ == "__main__":
    formats = scan_csv_formats()