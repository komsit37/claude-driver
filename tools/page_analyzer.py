#!/usr/bin/env python3
"""
🔍 Page Analyzer - Claude's First Analysis Tool

WHEN TO USE:
- After capturing any new page
- When extraction returns unexpected results  
- To understand page structure before building extractors

HOW TO USE:
    python page_analyzer.py ../sessions/2024-07-03_amazon/page_001.html
    python page_analyzer.py ../tmp/page_011.html

WHAT IT SHOWS:
- Page structure overview
- Detected patterns (lists, tables, forms)
- Suggested container selectors
- Common elements that might contain data

CLAUDE: This tool helps you understand what you're working with!
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import re
import json
from collections import Counter


def analyze_page(html_file):
    """Analyze page structure and provide insights for Claude"""
    print("🔍 CLAUDE PAGE ANALYSIS")
    print("=" * 50)
    
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        print("🔍 Recent captures:")
        show_recent_captures()
        return
    
    # Load and parse HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Basic page info
    title = soup.find('title')
    page_title = title.get_text().strip() if title else "No title"
    
    print(f"📄 Page: {page_title}")
    print(f"📁 File: {html_file}")
    print()
    
    # Structure analysis
    analyze_structure(soup)
    
    # Pattern detection
    analyze_patterns(soup)
    
    # Suggest containers
    suggest_containers(soup)
    
    # Show next steps for Claude
    show_claude_next_steps(html_file)


def analyze_structure(soup):
    """Analyze basic page structure"""
    print("📊 PAGE STRUCTURE")
    print("-" * 30)
    
    stats = {
        'Total elements': len(soup.find_all()),
        'Divs': len(soup.find_all('div')),
        'Links': len(soup.find_all('a')),
        'Images': len(soup.find_all('img')),
        'Forms': len(soup.find_all('form')),
        'Tables': len(soup.find_all('table')),
        'Lists': len(soup.find_all(['ul', 'ol'])),
        'Buttons': len(soup.find_all(['button', 'input[type="button"]']))
    }
    
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print()


def analyze_patterns(soup):
    """Detect common data patterns"""
    print("🎯 DETECTED PATTERNS")
    print("-" * 30)
    
    # Price patterns
    price_patterns = [
        r'[¥$€£]\s*[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*[¥$€£]',
        r'price.*[\d,]+',
        r'cost.*[\d,]+',
        r'total.*[\d,]+'
    ]
    
    prices_found = 0
    for pattern in price_patterns:
        matches = soup.find_all(string=re.compile(pattern, re.I))
        prices_found += len(matches)
    
    print(f"  💰 Price indicators: {prices_found}")
    
    # Date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        r'\d{4}年\d{1,2}月\d{1,2}日'
    ]
    
    dates_found = 0
    for pattern in date_patterns:
        matches = soup.find_all(string=re.compile(pattern, re.I))
        dates_found += len(matches)
    
    print(f"  📅 Date indicators: {dates_found}")
    
    # ID patterns
    id_patterns = [
        r'id[:\s]*[A-Z0-9-]+',
        r'order[:\s]*[A-Z0-9-]+',
        r'#[A-Z0-9-]+',
        r'[A-Z0-9]{3}-[A-Z0-9]{7}-[A-Z0-9]{7}'  # Amazon-style IDs
    ]
    
    ids_found = 0
    for pattern in id_patterns:
        matches = soup.find_all(string=re.compile(pattern, re.I))
        ids_found += len(matches)
    
    print(f"  🆔 ID indicators: {ids_found}")
    
    # Container patterns
    container_keywords = ['item', 'order', 'product', 'card', 'box', 'row', 'entry']
    container_classes = []
    
    for elem in soup.find_all(['div', 'section', 'article']):
        classes = elem.get('class', [])
        for cls in classes:
            if any(keyword in cls.lower() for keyword in container_keywords):
                container_classes.append(cls)
    
    container_counter = Counter(container_classes)
    print(f"  📦 Container patterns: {len(container_counter)}")
    
    if container_counter:
        print("     Top containers:")
        for cls, count in container_counter.most_common(5):
            print(f"       .{cls} ({count} elements)")
    
    print()


def suggest_containers(soup):
    """Suggest likely data containers for extraction"""
    print("💡 SUGGESTED SELECTORS")
    print("-" * 30)
    
    # Find containers with multiple child elements (likely data containers)
    potential_containers = []
    
    for elem in soup.find_all(['div', 'section', 'article', 'li']):
        # Count meaningful children
        children = elem.find_all(['a', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img'])
        text_length = len(elem.get_text().strip())
        
        # Score container
        score = 0
        if len(children) >= 3:  # Multiple elements
            score += 2
        if 50 <= text_length <= 1000:  # Reasonable amount of text
            score += 1
        if elem.get('class'):  # Has classes
            score += 1
        if elem.get('id'):  # Has ID
            score += 1
        
        # Check for data attributes
        data_attrs = [attr for attr in elem.attrs.keys() if attr.startswith('data-')]
        if data_attrs:
            score += 2
        
        if score >= 3:
            container_info = {
                'element': elem.name,
                'classes': elem.get('class', []),
                'id': elem.get('id'),
                'children_count': len(children),
                'text_length': text_length,
                'score': score
            }
            potential_containers.append(container_info)
    
    # Sort by score and show top suggestions
    potential_containers.sort(key=lambda x: x['score'], reverse=True)
    
    print("  🎯 Top container candidates:")
    for i, container in enumerate(potential_containers[:5]):
        classes_str = '.'.join(container['classes']) if container['classes'] else 'no-class'
        id_str = f"#{container['id']}" if container['id'] else ''
        
        selector = f"{container['element']}"
        if container['classes']:
            selector += f".{container['classes'][0]}"
        if container['id']:
            selector += f"#{container['id']}"
        
        print(f"    {i+1}. {selector}")
        print(f"       Children: {container['children_count']}, Text: {container['text_length']} chars")
    
    # Suggest specific field selectors
    print("\n  🔍 Field selector suggestions:")
    
    # Look for common patterns
    selectors = {
        'Links (products/details)': 'a[href*="product"], a[href*="/dp/"], a[href*="item"]',
        'Prices': '[class*="price"], [data-price], .amount, .cost',
        'Dates': '[class*="date"], [datetime], .timestamp',
        'IDs/Numbers': '[data-id], [data-order], .order-id, .item-id',
        'Titles': 'h1, h2, h3, .title, .name, .product-name'
    }
    
    for label, selector in selectors.items():
        elements = soup.select(selector)
        print(f"    {label}: {selector} ({len(elements)} found)")
    
    print()


def show_recent_captures():
    """Show recent capture files to help Claude"""
    tmp_files = []
    sessions_files = []
    
    # Check tmp directory
    if os.path.exists('./tmp'):
        tmp_files = [f for f in os.listdir('./tmp') if f.startswith('page_') and f.endswith('.html')]
        tmp_files.sort()
    
    # Check sessions directory
    if os.path.exists('./sessions'):
        for session_dir in os.listdir('./sessions'):
            session_path = os.path.join('./sessions', session_dir)
            if os.path.isdir(session_path):
                session_files = [f for f in os.listdir(session_path) if f.endswith('.html')]
                for f in session_files:
                    sessions_files.append(os.path.join(session_path, f))
    
    print("Recent HTML files:")
    all_files = []
    for f in tmp_files[-5:]:  # Last 5 from tmp
        all_files.append(f"./tmp/{f}")
    for f in sessions_files[-5:]:  # Last 5 from sessions
        all_files.append(f)
    
    for f in all_files:
        if os.path.exists(f):
            mtime = os.path.getmtime(f)
            import datetime
            time_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  {f} ({time_str})")


def show_claude_next_steps(html_file):
    """Show Claude what to do next"""
    print("🚀 CLAUDE NEXT STEPS")
    print("-" * 30)
    
    steps = [
        "1. Review the analysis above to understand page structure",
        "2. Try suggested selectors in browser dev tools or selector_tester.py",
        "3. If this is a new site, copy sites/templates/basic_extractor.py",
        "4. Customize extraction logic based on patterns found",
        "5. Test extraction on 2-3 items first before scaling up",
        "6. Use tools/extraction_validator.py to check results"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print()
    print("📝 Useful commands:")
    print(f"  python tools/selector_tester.py {html_file}")
    print("  cp sites/templates/basic_extractor.py sites/NEWSITE/extractor.py")
    print("  python tools/extraction_validator.py results.json")
    
    print()
    print("💡 Remember: Always test small samples first!")


def main():
    if len(sys.argv) < 2:
        print("❌ CLAUDE: You need to provide an HTML file!")
        print("📖 Usage: python page_analyzer.py path/to/page.html")
        print("💡 Tip: Check tmp/ folder or sessions/ folder for recent captures")
        print()
        show_recent_captures()
        return
    
    html_file = sys.argv[1]
    analyze_page(html_file)


if __name__ == "__main__":
    main()