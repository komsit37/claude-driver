#!/usr/bin/env python3
"""
🧪 Selector Tester - Test CSS Selectors Quickly

WHEN TO USE:
- After page analysis suggests selectors
- When extraction returns unexpected results
- To validate selectors before building extractors

HOW TO USE:
    python selector_tester.py ../tmp/page_011.html
    # Then interactively test selectors

WHAT IT DOES:
- Test CSS selectors against captured HTML
- Show sample matches and counts
- Help you refine selectors iteratively

CLAUDE: Use this to validate selectors before extraction!
"""

import sys
import os
from bs4 import BeautifulSoup
import re


def test_selector_interactive(html_file):
    """Interactive selector testing for Claude"""
    print("🧪 CLAUDE SELECTOR TESTER")
    print("=" * 50)
    
    if not os.path.exists(html_file):
        print(f"❌ File not found: {html_file}")
        return
    
    # Load HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print(f"📄 Testing selectors on: {html_file}")
    print("💡 Enter CSS selectors to test (or 'help' for examples)")
    print("💡 Type 'quit' to exit")
    print()
    
    # Suggested selectors to try
    suggestions = [
        "div[class*='order']",
        "div[class*='item']", 
        "div[class*='product']",
        "a[href*='/dp/']",
        "[data-order-id]",
        "[class*='price']",
        "[class*='date']",
        ".title, .name, h1, h2, h3"
    ]
    
    print("🎯 Suggested selectors to try:")
    for i, selector in enumerate(suggestions, 1):
        print(f"  {i}. {selector}")
    print()
    
    while True:
        try:
            user_input = input("🔍 Enter selector (or number from suggestions): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'help':
                show_help()
                continue
            
            # Handle numbered suggestions
            if user_input.isdigit():
                num = int(user_input)
                if 1 <= num <= len(suggestions):
                    selector = suggestions[num - 1]
                    print(f"Testing: {selector}")
                else:
                    print("❌ Invalid number")
                    continue
            else:
                selector = user_input
            
            if not selector:
                continue
            
            # Test the selector
            test_selector(soup, selector)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def test_selector(soup, selector):
    """Test a single selector and show results"""
    try:
        elements = soup.select(selector)
        count = len(elements)
        
        print(f"✅ Selector: {selector}")
        print(f"📊 Found: {count} elements")
        
        if count == 0:
            print("💡 No matches found. Try:")
            print("   - Check if classes/IDs exist")
            print("   - Use broader selectors (e.g., just 'div' instead of 'div.specific-class')")
            print("   - Look for partial matches with [class*='partial']")
            
        elif count > 0:
            print("📝 Sample matches:")
            
            # Show first few matches
            for i, elem in enumerate(elements[:3]):
                print(f"\n  Match {i+1}:")
                
                # Show element info
                tag_info = f"<{elem.name}"
                if elem.get('class'):
                    tag_info += f" class=\"{' '.join(elem['class'])}\""
                if elem.get('id'):
                    tag_info += f" id=\"{elem['id']}\""
                tag_info += ">"
                print(f"    Tag: {tag_info}")
                
                # Show text content (truncated)
                text = elem.get_text().strip()
                if text:
                    if len(text) > 100:
                        text = text[:97] + "..."
                    print(f"    Text: {text}")
                else:
                    print("    Text: (empty)")
                
                # Show key attributes
                attrs = elem.attrs
                important_attrs = ['href', 'src', 'data-id', 'data-order-id', 'value']
                for attr in important_attrs:
                    if attr in attrs:
                        value = attrs[attr]
                        if isinstance(value, list):
                            value = ' '.join(value)
                        if len(str(value)) > 50:
                            value = str(value)[:47] + "..."
                        print(f"    {attr}: {value}")
            
            if count > 3:
                print(f"\n  ... and {count - 3} more matches")
            
            # Provide extraction suggestions
            if count > 1:
                print(f"\n💡 This selector found {count} elements - good for batch extraction!")
                print("   Next steps:")
                print("   1. Use this in your extractor loop")
                print("   2. Extract specific fields from each element")
                print("   3. Test field extraction on sample elements")
            
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Invalid selector: {e}")
        print("💡 CSS selector syntax help:")
        print("   .class-name    - elements with class")
        print("   #id-name       - element with ID")
        print("   [attr='value'] - elements with attribute value")
        print("   [attr*='part'] - elements with attribute containing text")
        print("   div.class      - div elements with class")
        print("   parent > child - direct children")


def show_help():
    """Show help for selector syntax"""
    print("\n📚 CSS SELECTOR HELP")
    print("-" * 30)
    
    examples = [
        ("Basic selectors", [
            "div - all div elements",
            ".class-name - elements with class",
            "#id-name - element with ID",
            "div.class - div with specific class"
        ]),
        ("Attribute selectors", [
            "[data-id] - elements with data-id attribute",
            "[href*='product'] - links containing 'product'",
            "[class*='order'] - elements with class containing 'order'",
            "[data-order-id='123'] - exact attribute match"
        ]),
        ("Combinators", [
            "div > span - direct child spans of divs",
            "div span - all spans inside divs",
            ".container .item - items inside containers",
            ".order + .order - adjacent orders"
        ]),
        ("Common patterns", [
            "a[href*='/dp/'] - Amazon product links",
            "[class*='price'] - price elements",
            "[class*='date'] - date elements",
            "div[data-order-id] - order containers"
        ])
    ]
    
    for category, selectors in examples:
        print(f"\n{category}:")
        for selector in selectors:
            print(f"  {selector}")
    
    print("\n💡 Start broad, then narrow down!")
    print()


def main():
    if len(sys.argv) < 2:
        print("❌ CLAUDE: You need to provide an HTML file!")
        print("📖 Usage: python selector_tester.py path/to/page.html")
        print("💡 Tip: Use the HTML file from your latest capture")
        
        # Show recent files
        if os.path.exists('./tmp'):
            html_files = [f for f in os.listdir('./tmp') if f.startswith('page_') and f.endswith('.html')]
            if html_files:
                html_files.sort()
                print(f"\n🔍 Recent files: ./tmp/{html_files[-1]}")
        return
    
    html_file = sys.argv[1]
    test_selector_interactive(html_file)


if __name__ == "__main__":
    main()