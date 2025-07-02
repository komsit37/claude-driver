#!/usr/bin/env python3
"""
✅ Extraction Validator - Validate Extraction Results

WHEN TO USE:
- After running any extraction script
- To check data quality before saving
- To identify issues with extraction logic

HOW TO USE:
    python extraction_validator.py ../sites/amazon/outputs/orders.json
    python extraction_validator.py results.json

WHAT IT CHECKS:
- Data completeness and quality
- Field validation and patterns
- Duplicate detection
- Statistical analysis

CLAUDE: Always validate your extraction results!
"""

import sys
import os
import json
from collections import Counter
import re
from datetime import datetime


def validate_extraction_results(results_file):
    """Comprehensive validation of extraction results"""
    print("✅ CLAUDE EXTRACTION VALIDATOR")
    print("=" * 50)
    
    if not os.path.exists(results_file):
        print(f"❌ File not found: {results_file}")
        return False
    
    # Load results
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {results_file}")
        return False
    
    print(f"📄 Validating: {results_file}")
    print()
    
    # Extract items (handle different formats)
    items = []
    if isinstance(data, dict):
        if 'orders' in data:
            items = data['orders']
        elif 'items' in data:
            items = data['items']
        elif 'data' in data:
            items = data['data']
        else:
            # Assume the dict values are the items
            items = list(data.values()) if data else []
    elif isinstance(data, list):
        items = data
    
    if not items:
        print("❌ No items found in results file!")
        return False
    
    print(f"📊 Total items to validate: {len(items)}")
    print()
    
    # Run validation checks
    validation_passed = True
    
    validation_passed &= check_data_completeness(items)
    validation_passed &= check_field_quality(items)
    validation_passed &= check_duplicates(items)
    validation_passed &= analyze_patterns(items)
    
    # Final assessment
    print("🎯 VALIDATION SUMMARY")
    print("-" * 30)
    if validation_passed:
        print("✅ All validation checks passed!")
        print("💾 Data is ready for use.")
    else:
        print("⚠️  Some validation issues found.")
        print("🔧 Consider improving extraction logic.")
    
    return validation_passed


def check_data_completeness(items):
    """Check field completeness across all items"""
    print("📋 DATA COMPLETENESS CHECK")
    print("-" * 30)
    
    if not items:
        print("❌ No items to check!")
        return False
    
    # Collect all fields
    all_fields = set()
    for item in items:
        if isinstance(item, dict):
            all_fields.update(item.keys())
    
    print(f"📝 Fields found: {', '.join(sorted(all_fields))}")
    
    # Check completeness for each field
    issues = 0
    total_items = len(items)
    
    for field in sorted(all_fields):
        count_with_field = 0
        count_non_empty = 0
        
        for item in items:
            if isinstance(item, dict) and field in item:
                count_with_field += 1
                if item[field] and str(item[field]).strip():
                    count_non_empty += 1
        
        presence_rate = (count_with_field / total_items) * 100
        completeness_rate = (count_non_empty / total_items) * 100
        
        status = "✅"
        if completeness_rate < 50:
            status = "❌"
            issues += 1
        elif completeness_rate < 80:
            status = "⚠️ "
            issues += 1
        
        print(f"  {status} {field}: {count_non_empty}/{total_items} ({completeness_rate:.1f}%)")
    
    print(f"\n📊 Summary: {len(all_fields)} fields, {issues} with issues")
    print()
    
    return issues == 0


def check_field_quality(items):
    """Check quality of specific field types"""
    print("🔍 FIELD QUALITY CHECK")
    print("-" * 30)
    
    issues = 0
    
    # Check common field patterns
    field_patterns = {
        'id': [r'[A-Z0-9-]+', "Should contain alphanumeric characters and dashes"],
        'order_id': [r'[A-Z0-9-]+', "Should contain alphanumeric characters and dashes"],
        'price': [r'[¥$€£]?\d+', "Should contain currency symbol and numbers"],
        'total_amount': [r'[¥$€£]?\d+', "Should contain currency symbol and numbers"],
        'date': [r'\d{4}', "Should contain a year (4 digits)"],
        'order_date': [r'\d{4}', "Should contain a year (4 digits)"],
        'email': [r'@.*\.', "Should contain @ and domain"],
        'url': [r'https?://', "Should start with http:// or https://"]
    }
    
    for item in items:
        if not isinstance(item, dict):
            continue
            
        for field, (pattern, description) in field_patterns.items():
            if field in item and item[field]:
                value = str(item[field])
                if not re.search(pattern, value, re.I):
                    print(f"⚠️  {field}: '{value}' - {description}")
                    issues += 1
                    break  # Only show first few issues per field
    
    if issues == 0:
        print("✅ No field quality issues found")
    else:
        print(f"⚠️  Found {issues} field quality issues")
    
    print()
    return issues == 0


def check_duplicates(items):
    """Check for duplicate items"""
    print("🔍 DUPLICATE CHECK")
    print("-" * 30)
    
    # Check for duplicates based on different keys
    duplicate_keys = ['id', 'order_id', 'url', 'title', 'name']
    
    duplicates_found = 0
    
    for key in duplicate_keys:
        values = []
        for item in items:
            if isinstance(item, dict) and key in item and item[key]:
                values.append(str(item[key]).strip().lower())
        
        if not values:
            continue
        
        value_counts = Counter(values)
        duplicates = {v: count for v, count in value_counts.items() if count > 1}
        
        if duplicates:
            print(f"⚠️  {key}: {len(duplicates)} duplicate values found")
            for value, count in list(duplicates.items())[:3]:  # Show first 3
                print(f"     '{value}' appears {count} times")
            duplicates_found += len(duplicates)
        else:
            print(f"✅ {key}: No duplicates found")
    
    print(f"\n📊 Summary: {duplicates_found} total duplicate values")
    print()
    
    return duplicates_found == 0


def analyze_patterns(items):
    """Analyze data patterns and statistics"""
    print("📈 PATTERN ANALYSIS")
    print("-" * 30)
    
    # Analyze numeric fields (prices, quantities, etc.)
    numeric_fields = []
    for item in items:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    numeric_fields.append(key)
                elif isinstance(value, str):
                    # Check if string contains numbers (like prices)
                    if re.search(r'\d+', value):
                        numeric_fields.append(key)
    
    numeric_fields = list(set(numeric_fields))
    
    if numeric_fields:
        print("📊 Numeric field analysis:")
        for field in numeric_fields:
            values = []
            for item in items:
                if isinstance(item, dict) and field in item:
                    value = item[field]
                    if isinstance(value, (int, float)):
                        values.append(value)
                    elif isinstance(value, str):
                        # Extract numbers from strings
                        numbers = re.findall(r'\d+', value)
                        if numbers:
                            try:
                                values.append(float(numbers[0]))
                            except ValueError:
                                pass
            
            if values:
                print(f"  {field}: min={min(values)}, max={max(values)}, avg={sum(values)/len(values):.1f}")
    
    # Check date ranges
    date_fields = ['date', 'order_date', 'created_at', 'timestamp']
    for field in date_fields:
        dates = []
        for item in items:
            if isinstance(item, dict) and field in item and item[field]:
                date_str = str(item[field])
                # Try to extract year
                year_match = re.search(r'\d{4}', date_str)
                if year_match:
                    dates.append(int(year_match.group()))
        
        if dates:
            print(f"📅 {field}: {min(dates)} to {max(dates)} ({len(set(dates))} unique years)")
    
    print()
    return True


def main():
    if len(sys.argv) < 2:
        print("❌ CLAUDE: You need to provide a results file!")
        print("📖 Usage: python extraction_validator.py results.json")
        print("💡 Common locations:")
        print("   sites/amazon/outputs/orders.json")
        print("   sites/sitename/outputs/extraction_*.json")
        print()
        
        # Show recent files
        show_recent_results()
        return
    
    results_file = sys.argv[1]
    validate_extraction_results(results_file)


def show_recent_results():
    """Show recent results files to help Claude"""
    print("🔍 Recent results files:")
    
    # Check sites directories
    if os.path.exists('./sites'):
        for site_dir in os.listdir('./sites'):
            site_path = os.path.join('./sites', site_dir)
            if os.path.isdir(site_path):
                outputs_path = os.path.join(site_path, 'outputs')
                if os.path.exists(outputs_path):
                    json_files = [f for f in os.listdir(outputs_path) if f.endswith('.json')]
                    for json_file in json_files:
                        full_path = os.path.join(outputs_path, json_file)
                        mtime = os.path.getmtime(full_path)
                        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                        print(f"  {full_path} ({time_str})")


if __name__ == "__main__":
    main()