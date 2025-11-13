"""Generate SecureCart360 synthetic CSV files in /data
Run: python3 scripts/generate_data.py
"""
import csv
import random
from datetime import datetime, timedelta
import os

os.makedirs('data', exist_ok=True)

random.seed(42)

# helper pools
first = ['Asha','Rohan','Mira','Karan','Zara','Ishaan','Lina','Vivaan','Neha','Arjun','Priya','Sameer']
last = ['Patel','Sharma','Iyer','Gupta','Khan','Menon','Reddy','Das']
countries = ['India','USA','UK','Germany','Canada','Australia']
products_list = [
    ('Smartphone X', 'Electronics'),('Laptop Pro','Electronics'),('Air Purifier','Home'),
    ('Coffee Maker','Home'),('Running Shoes','Fashion'),('Yoga Mat','Fitness'),
    ('Wireless Earbuds','Electronics'),('Blender','Home'),('Jacket','Fashion'),('Smartwatch','Electronics')]
payment_methods = ['Card','UPI','NetBanking','Wallet']

# 1) customers.csv
customers = []
for i in range(1,51):
    name = f"{random.choice(first)} {random.choice(last)}"
    customers.append({
        'customer_id': i,
        'full_name': name,
        'email': f"{name.replace(' ','').lower()}{i}@example.com",
        'signup_date': (datetime.now() - timedelta(days=random.randint(30,900))).strftime('%Y-%m-%d'),
        'country': random.choice(countries),
        'loyalty_tier': random.choice(['Bronze','Silver','Gold'])
    })

with open('data/customers.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)

# 2) products.csv
products = []
pid = 1
for name, cat in products_list:
    products.append({
        'product_id': pid,
        'product_name': name,
        'category': cat,
        'price': round(random.uniform(499,99999)/100,2),
        'sku': f"SKU{1000+pid}"
    })
    pid += 1

with open('data/products.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(products)

# 3) orders.csv and 4) order_items.csv
orders = []
order_items = []
item_id = 1
order_id = 1
for _ in range(120):
    cust = random.choice(customers)
    num_items = random.randint(1,4)
    order_total = 0
    items = []
    for _ in range(num_items):
        prod = random.choice(products)
        qty = random.randint(1,3)
        order_total += prod['price'] * qty
        items.append((prod['product_id'], qty, prod['price']))
    order_date = (datetime.now() - timedelta(days=random.randint(0,365))).strftime('%Y-%m-%d %H:%M:%S')
    orders.append({
        'order_id': order_id,
        'customer_id': cust['customer_id'],
        'order_date': order_date,
        'order_total': round(order_total,2),
        'payment_method': random.choice(payment_methods),
        'order_status': random.choices(['COMPLETED','PENDING','CANCELLED'], weights=[80,15,5])[0]
    })
    for pid_, qty, price in items:
        order_items.append({
            'item_id': item_id,
            'order_id': order_id,
            'product_id': pid_,
            'quantity': qty,
            'unit_price': price
        })
        item_id += 1
    order_id += 1

with open('data/orders.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=orders[0].keys())
    writer.writeheader()
    writer.writerows(orders)

with open('data/order_items.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=order_items[0].keys())
    writer.writeheader()
    writer.writerows(order_items)

# 5) fraud_signals.csv
fraud = []
for o in orders:
    # simulate some risky cases
    hv_threshold = 500.0
    high_value = 1 if o['order_total'] > hv_threshold else 0
    device_change = random.choices([0,1], weights=[85,15])[0]
    payment_risk = round(random.random(),2)
    billing_country = random.choice(countries + ['Malta','Singapore'])
    ip_country = random.choice(countries + ['Russia','Ukraine'])
    fraud.append({
        'order_id': o['order_id'],
        'ip_country': ip_country,
        'billing_country': billing_country,
        'device_change_flag': device_change,
        'high_value_flag': high_value,
        'payment_risk_score': payment_risk
    })

with open('data/fraud_signals.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fraud[0].keys())
    writer.writeheader()
    writer.writerows(fraud)

print('Generated data in /data')
