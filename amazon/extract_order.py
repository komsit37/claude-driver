#!/usr/bin/env python3
"""
Extract first order details from Amazon orders page HTML
"""

from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_all_order_details(html_file_path):
    """Extract details of all orders from Amazon orders page HTML"""
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return {"error": f"File not found: {html_file_path}"}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Debug: Get page title first
    title = soup.find('title')
    page_title = title.get_text() if title else "Unknown"
    
    result = {"page_title": page_title}
    
    # Find all potential order containers using multiple strategies
    all_containers = set()
    
    # Strategy 1: Look for order-specific class patterns
    patterns = [
        {'class': re.compile(r'order', re.I)},
        {'data-order-id': True},
        {'class': re.compile(r'a-box-group')},
        {'class': re.compile(r'shipment', re.I)},
        {'id': re.compile(r'order|OrderID', re.I)},
    ]
    
    for pattern in patterns:
        containers = soup.find_all('div', pattern)
        all_containers.update(containers)
    
    # Strategy 2: Look for text containing order indicators and get parent containers
    order_indicators = [
        r'Order.*#[\d-]+',
        r'注文番号.*[\d-]+', 
        r'Delivered.*\d{4}',
        r'¥[\d,]+.*total',
        r'Order placed.*\d{4}',
        r'Shipped.*\d{4}'
    ]
    
    for indicator in order_indicators:
        text_elements = soup.find_all(string=re.compile(indicator, re.I))
        for elem in text_elements:
            # Get the container that likely holds the full order
            container = elem.find_parent('div')
            while container and len(container.get_text()) < 200:  # Find substantial container
                container = container.find_parent('div')
            if container:
                all_containers.add(container)
    
    order_containers = list(all_containers)
    result['containers_found'] = len(order_containers)
    
    # Process all containers to extract order details
    all_orders = []
    
    def extract_order_from_container(container):
        """Extract order details from a single container"""
        text = container.get_text().strip()
        if not text or len(text) < 50:  # Skip containers with minimal content
            return None
            
        order = {}
        
        # Score container to see if it's likely an order
        score = 0
        order_keywords = ['order', '注文', '¥', 'delivered', 'shipped', 'placed', '#']
        for keyword in order_keywords:
            if keyword.lower() in text.lower():
                score += 1
        
        # Must have some order indicators to be considered
        if score < 2:
            return None
        
        # Extract order ID
        order_id_patterns = [
            r'Order.*?#[\s]*([A-Z0-9-]+)',
            r'注文番号.*?([A-Z0-9-]+)', 
            r'Order ID.*?([A-Z0-9-]+)',
            r'#([0-9-]+)',
        ]
        
        for pattern in order_id_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                order['order_id'] = match.group(1)
                break
        
        # Must have order ID to be valid order
        if 'order_id' not in order:
            return None
            
        # Extract order date
        date_patterns = [
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'Order placed\s+([^\n]+)',
            r'Placed on\s+([^\n]+)',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                order['order_date'] = match.group(1) if 'placed' in pattern.lower() else match.group(0)
                break
        
        # Extract total amount
        total_patterns = [
            r'Order total:?\s*¥([\d,]+)',
            r'Total:?\s*¥([\d,]+)', 
            r'¥([\d,]+)\s*total',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                order['total_amount'] = f"¥{match.group(1)}"
                break
        
        # Extract all prices found (but filter out unrealistic ones)
        price_matches = re.findall(r'¥[\d,]+', text)
        if price_matches:
            # Remove prices that are too large or likely page artifacts
            filtered_prices = []
            for price in price_matches:
                price_value = float(price.replace('¥', '').replace(',', ''))
                # Keep prices between ¥1 and ¥1,000,000 (reasonable range)
                if 1 <= price_value <= 1000000:
                    filtered_prices.append(price)
            
            if filtered_prices:
                order['all_prices'] = filtered_prices[:5]  # Limit to first 5 reasonable prices
        
        # Extract delivery status
        status_keywords = ['delivered', 'shipped', 'processing', 'cancelled', '配送済み', '発送済み', 'お届け済み', 'pending']
        for keyword in status_keywords:
            if keyword.lower() in text.lower():
                order['status'] = keyword
                break
        
        # Extract products
        product_links = container.find_all('a', href=re.compile(r'/dp/|/gp/product|amazon\.co\.jp.*product'))
        products = []
        seen_products = set()  # Avoid duplicate products
        
        for link in product_links:
            product_text = link.get_text().strip()
            # Filter out navigation links and short text
            if (product_text and 
                len(product_text) > 15 and 
                product_text not in seen_products and
                not re.match(r'^(see|view|details|more|track|return|buy|again|reorder)$', product_text, re.I)):
                products.append(product_text)
                seen_products.add(product_text)
        
        if products:
            order['products'] = products[:3]  # Limit to first 3 unique products
        
        # Extract delivery address info if present
        if re.search(r'deliver(ed)?\s+to', text, re.I):
            delivery_match = re.search(r'deliver(ed)?\s+to[:\s]*([^\n]+)', text, re.I)
            if delivery_match:
                order['delivery_info'] = delivery_match.group(2).strip()
        
        return order
    
    # Extract orders from all containers and deduplicate
    if order_containers:
        orders_dict = {}  # Use dict to deduplicate by order_id
        
        for i, container in enumerate(order_containers):
            order = extract_order_from_container(container)
            if order:
                order_id = order['order_id']
                
                # If this order_id hasn't been seen, or this container has more data
                if order_id not in orders_dict:
                    order['container_index'] = i
                    order['extraction_timestamp'] = datetime.now().isoformat()
                    orders_dict[order_id] = order
                else:
                    # Merge additional data from this container
                    existing_order = orders_dict[order_id]
                    
                    # Keep the most complete product list
                    if 'products' in order and len(order.get('products', [])) > len(existing_order.get('products', [])):
                        existing_order['products'] = order['products']
                    
                    # Add status if missing
                    if 'status' in order and 'status' not in existing_order:
                        existing_order['status'] = order['status']
                    
                    # Merge all prices (remove duplicates)
                    if 'all_prices' in order:
                        existing_prices = set(existing_order.get('all_prices', []))
                        new_prices = set(order.get('all_prices', []))
                        combined_prices = list(existing_prices.union(new_prices))
                        existing_order['all_prices'] = sorted(combined_prices, key=lambda x: float(x.replace('¥', '').replace(',', '')))
                    
                    # Update delivery info if available
                    if 'delivery_info' in order and 'delivery_info' not in existing_order:
                        existing_order['delivery_info'] = order['delivery_info']
        
        # Convert back to list and sort by date (newest first)
        all_orders = list(orders_dict.values())
        all_orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        
        result['total_orders_found'] = len(all_orders)
        result['orders'] = all_orders
        result['extraction_metadata'] = {
            'total_containers_analyzed': len(order_containers),
            'orders_deduplicated': True,
            'extraction_date': datetime.now().isoformat(),
            'source_file': html_file_path
        }
    
    else:
        # No containers found - debug the page structure
        result['debug_info'] = {
            'total_divs': len(soup.find_all('div')),
            'body_text_sample': soup.get_text()[:500] + "..." if len(soup.get_text()) > 500 else soup.get_text(),
            'has_main': bool(soup.find('main')),
            'div_classes': [div.get('class') for div in soup.find_all('div')[:10] if div.get('class')]
        }
    
    return result

def main():
    html_file = '/Users/pkomsit/code/python/browser-script/tmp/page_003.html'
    output_file = '/Users/pkomsit/code/python/browser-script/amazon/orders.json'
    
    print("Extracting all order details from:", html_file)
    print("=" * 60)
    
    result = extract_all_order_details(html_file)
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Extraction complete!")
    print(f"📊 Total containers analyzed: {result.get('containers_found', 0)}")
    print(f"📦 Orders found: {result.get('total_orders_found', 0)}")
    print(f"💾 Results saved to: {output_file}")
    
    # Print summary of orders
    if 'orders' in result:
        print("\n📋 Order Summary:")
        print("-" * 40)
        for i, order in enumerate(result['orders'][:5], 1):  # Show first 5 orders
            print(f"{i}. Order ID: {order.get('order_id', 'N/A')}")
            print(f"   Date: {order.get('order_date', 'N/A')}")
            print(f"   Status: {order.get('status', 'N/A')}")
            print(f"   Total: {order.get('total_amount', 'N/A')}")
            print(f"   Products: {len(order.get('products', []))} items")
            print()
        
        if len(result['orders']) > 5:
            print(f"... and {len(result['orders']) - 5} more orders")
    
    # Print statistics
    if 'orders' in result:
        total_value = 0
        status_counts = {}
        for order in result['orders']:
            # Calculate total value
            if 'total_amount' in order:
                amount_str = order['total_amount'].replace('¥', '').replace(',', '')
                try:
                    total_value += float(amount_str)
                except ValueError:
                    pass
            
            # Count statuses
            status = order.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n💰 Total order value: ¥{total_value:,.0f}")
        print(f"📊 Order statuses: {dict(status_counts)}")
        print(f"📅 Date range: {result['orders'][-1].get('order_date', 'N/A')} to {result['orders'][0].get('order_date', 'N/A')}")
    
    print(f"\n✨ Clean, deduplicated order data saved to: {output_file}")

if __name__ == "__main__":
    main()