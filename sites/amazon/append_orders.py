import json
import csv

# Load extracted orders
with open('outputs/orders.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

orders = data['orders']

# Load existing CSV
existing_orders = []
try:
    with open('outputs/amazon_orders_2024_formatted.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_orders = list(reader)
except FileNotFoundError:
    pass

# Get existing order IDs
existing_ids = {row['Order#'] for row in existing_orders}

# Convert new orders to CSV format
new_orders = []
for order in orders:
    order_id = order['order_id']
    if order_id not in existing_ids and order_id != '1':
        # Clean price
        price = order.get('total_amount', 'N/A')
        
        # Get first product name
        product = order.get('products', ['N/A'])[0] if order.get('products') else 'N/A'
        if len(product) > 70:
            product = product[:67] + '...'
        
        new_orders.append({
            'No.': len(existing_orders) + len(new_orders) + 1,
            'Order#': order_id,
            'Date': order.get('order_date', 'N/A'),
            'Price': price,
            'Product Title': product
        })

if new_orders:
    # Append to existing CSV
    with open('outputs/amazon_orders_2024_formatted.csv', 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['No.', 'Order#', 'Date', 'Price', 'Product Title']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(new_orders)
    
    print(f'✅ Appended {len(new_orders)} new orders to CSV')
    for order in new_orders:
        print(f'  {order["Order#"]} - {order["Date"]} - {order["Price"]}')
else:
    print('No new orders to append (all already exist)')