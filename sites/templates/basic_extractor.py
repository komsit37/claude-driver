#!/usr/bin/env python3
"""
🏗️ Basic Site Extractor Template

CLAUDE: Copy this file to sites/YOUR_SITE/ and modify the extraction logic.

EXAMPLE WORKFLOW:
1. Analyze page: python ../../tools/page_analyzer.py captured_page.html
2. Find containers: soup.find_all('div', class_='item-container')  
3. Extract fields: order_id, date, price, title
4. Test on small sample first
5. Iterate and improve

COMMON PATTERNS:
- E-commerce orders: Look for .order, .purchase, .transaction
- Product listings: Look for .product, .item, .listing
- Pagination: Look for .next, .pagination, [aria-label="Next"]

CLAUDE: Always test on small samples first, then scale up!
"""

import os
import json
import csv
from datetime import datetime
from bs4 import BeautifulSoup
import re
import glob


def find_latest_html_file(search_dir="../tmp"):
    """Find the latest HTML file for extraction"""
    html_pattern = os.path.join(search_dir, "page_*.html")
    html_files = glob.glob(html_pattern)
    
    if not html_files:
        # Try sessions directory
        sessions_files = []
        if os.path.exists("../sessions"):
            for session_dir in os.listdir("../sessions"):
                session_path = os.path.join("../sessions", session_dir)
                if os.path.isdir(session_path):
                    session_pattern = os.path.join(session_path, "*.html")
                    session_files = glob.glob(session_pattern)
                    sessions_files.extend(session_files)
        
        if sessions_files:
            html_files = sessions_files
        else:
            raise FileNotFoundError(f"No HTML files found in {search_dir} or ../sessions/")
    
    # Sort by modification time (newest first)
    latest_file = max(html_files, key=lambda x: os.path.getmtime(x))
    print(f"📄 Using latest HTML file: {os.path.basename(latest_file)}")
    
    return latest_file


def extract_sample_data(html_file, limit=3):
    """
    CLAUDE: Always start with this function to test extraction!
    Extract a small sample to validate your selectors and logic.
    """
    print("🧪 EXTRACTING SAMPLE DATA")
    print("=" * 40)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # TODO: CLAUDE - Customize these selectors based on your page analysis
    container_selector = "div"  # Change this to your actual container selector
    containers = soup.select(container_selector)
    
    print(f"🔍 Found {len(containers)} containers with selector: {container_selector}")
    
    if len(containers) == 0:
        print("❌ No containers found!")
        print("💡 CLAUDE: You need to:")
        print("   1. Run page_analyzer.py on this HTML file")
        print("   2. Update the container_selector above")
        print("   3. Test selectors with selector_tester.py")
        return []
    
    sample_data = []
    
    for i, container in enumerate(containers[:limit]):
        print(f"\n📦 Container {i+1}:")
        
        # TODO: CLAUDE - Extract your specific fields here
        item = extract_item_from_container(container, i)
        
        if item:
            sample_data.append(item)
            print(f"✅ Extracted: {item}")
        else:
            print("❌ Failed to extract data from this container")
    
    print(f"\n✅ Sample extraction complete: {len(sample_data)} items")
    return sample_data


def extract_item_from_container(container, index):
    """
    CLAUDE: This is where you extract specific fields from each container.
    Customize this function based on your target data.
    """
    item = {}
    
    # TODO: CLAUDE - Replace these with your actual field extractions
    
    # Example: Extract ID
    id_elem = container.find(attrs={"data-id": True})  # Adjust selector
    if id_elem:
        item['id'] = id_elem.get('data-id')
    else:
        # Fallback: try other patterns
        id_text = container.find(string=re.compile(r'ID.*\d+'))
        if id_text:
            item['id'] = re.search(r'\d+', id_text).group()
    
    # Example: Extract title/name
    title_elem = container.find(['h1', 'h2', 'h3', '.title', '.name'])  # Adjust selector
    if title_elem:
        item['title'] = title_elem.get_text().strip()
    
    # Example: Extract price
    price_elem = container.find(string=re.compile(r'[¥$€£]\d+'))
    if price_elem:
        item['price'] = price_elem.strip()
    
    # Example: Extract date
    date_elem = container.find(string=re.compile(r'\d{4}-\d{2}-\d{2}|\w+ \d+, \d{4}'))
    if date_elem:
        item['date'] = date_elem.strip()
    
    # Example: Extract URL
    link_elem = container.find('a', href=True)
    if link_elem:
        item['url'] = link_elem['href']
    
    # Add metadata
    item['container_index'] = index
    item['extraction_timestamp'] = datetime.now().isoformat()
    
    # Validate: only return if we got some meaningful data
    required_fields = ['id', 'title']  # TODO: CLAUDE - adjust required fields
    if any(field in item for field in required_fields):
        return item
    else:
        return None


def extract_all_data(html_file):
    """
    CLAUDE: Use this after testing sample extraction.
    This processes all containers on the page.
    """
    print("🚀 EXTRACTING ALL DATA")
    print("=" * 40)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Use the same selector as in sample extraction
    container_selector = "div"  # TODO: CLAUDE - update this
    containers = soup.select(container_selector)
    
    print(f"🔍 Processing {len(containers)} containers...")
    
    all_data = []
    success_count = 0
    
    for i, container in enumerate(containers):
        item = extract_item_from_container(container, i)
        
        if item:
            all_data.append(item)
            success_count += 1
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"📊 Processed {i + 1}/{len(containers)} containers ({success_count} successful)")
    
    print(f"\n✅ Extraction complete!")
    print(f"📊 Total containers: {len(containers)}")
    print(f"📦 Successful extractions: {success_count}")
    print(f"⚠️  Failed extractions: {len(containers) - success_count}")
    
    return all_data


def save_results(data, output_dir="outputs"):
    """Save extraction results in multiple formats"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as JSON
    json_file = f"{output_dir}/extraction_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "extraction_date": datetime.now().isoformat(),
            "total_items": len(data),
            "items": data
        }, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    if data:
        csv_file = f"{output_dir}/extraction_{timestamp}.csv"
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"💾 Results saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file
    
    return json_file, None


def validate_extraction(data):
    """
    CLAUDE: Always validate your extraction results!
    """
    print("\n🔍 VALIDATION RESULTS")
    print("=" * 40)
    
    if not data:
        print("❌ No data to validate!")
        return False
    
    total_items = len(data)
    print(f"📊 Total items extracted: {total_items}")
    
    # Check field completeness
    all_fields = set()
    for item in data:
        all_fields.update(item.keys())
    
    print(f"📋 Fields found: {', '.join(sorted(all_fields))}")
    
    # Check for required fields (customize this)
    required_fields = ['id', 'title']  # TODO: CLAUDE - adjust as needed
    missing_required = 0
    
    for field in required_fields:
        count_with_field = sum(1 for item in data if field in item and item[field])
        missing = total_items - count_with_field
        completion_rate = (count_with_field / total_items) * 100
        
        print(f"   {field}: {count_with_field}/{total_items} ({completion_rate:.1f}%)")
        
        if completion_rate < 80:  # Less than 80% completion
            print(f"   ⚠️  {field} has low completion rate!")
            missing_required += 1
    
    # Overall assessment
    if missing_required == 0:
        print("✅ Validation passed! Data quality looks good.")
        return True
    else:
        print(f"❌ Validation concerns: {missing_required} fields have low completion rates")
        print("💡 Consider improving selectors or extraction logic")
        return False


def main():
    """
    CLAUDE: Main extraction workflow
    
    IMPORTANT: Always test sample extraction first!
    """
    print("🏗️ BASIC SITE EXTRACTOR")
    print("=" * 50)
    print("📖 CLAUDE: Read the docstring at the top of this file!")
    print("🧪 Testing sample extraction first...")
    print()
    
    try:
        # Find latest HTML file
        html_file = find_latest_html_file()
        
        # STEP 1: Test sample extraction
        sample_data = extract_sample_data(html_file, limit=3)
        
        if not sample_data:
            print("\n❌ Sample extraction failed!")
            print("🔧 CLAUDE: You need to customize the extraction logic:")
            print("   1. Update container_selector in extract_sample_data()")
            print("   2. Customize extract_item_from_container() function")
            print("   3. Test with selector_tester.py if needed")
            return
        
        # Validate sample
        print(f"\n🧪 Sample data preview:")
        for i, item in enumerate(sample_data, 1):
            print(f"  {i}. {item}")
        
        # Ask Claude to confirm
        print(f"\n💡 CLAUDE: Review the sample data above.")
        print("If it looks good, modify this script to extract all data.")
        print("If not, adjust the extraction logic and run again.")
        
        # For automated runs, you can uncomment below to extract all data
        # print("\n🚀 Proceeding with full extraction...")
        # all_data = extract_all_data(html_file)
        # validate_extraction(all_data)
        # save_results(all_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 CLAUDE: Troubleshooting steps:")
        print("   1. Make sure you have captured HTML files")
        print("   2. Run page_analyzer.py to understand page structure")
        print("   3. Use selector_tester.py to validate selectors")


if __name__ == "__main__":
    main()