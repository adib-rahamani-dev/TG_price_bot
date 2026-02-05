#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

print("=" * 70)
print("تست API endpoints")
print("=" * 70)

base_url = "http://127.0.0.1:8080"

# تست dashboard-data
print("\n📊 /dashboard-data")
print("-" * 70)
try:
    res = requests.get(f"{base_url}/dashboard-data")
    data = res.json()
    
    print(f"✓ Stats:")
    print(f"  - Total Users: {data['stats']['total_users']}")
    print(f"  - Total Configs: {data['stats']['total_configs']}")
    print(f"  - Total Feedback: {data['stats']['total_feedback']}")
    print(f"  - Last Update: {data['stats']['last_update']}")
    
    print(f"\n✓ Prices ({len(data['prices'])} items):")
    for price in data['prices']:
        print(f"  - {price.get('symbol', 'N/A')}: {price.get('name', 'N/A')}")
        print(f"    Price: {price.get('price')} {price.get('unit')}")
        print(f"    Change: {price.get('change_value')} ({price.get('change_percent')}%)")
except Exception as e:
    print(f"❌ Error: {e}")

# تست /list (کانفیگ‌ها)
print("\n\n📋 /list (Configs)")
print("-" * 70)
try:
    res = requests.get(f"{base_url}/list")
    data = res.json()
    print(f"✓ Total configs: {len(data)}")
    for cfg in data[:3]:
        print(f"  - Name: {cfg.get('name', 'N/A')}")
        print(f"    Time: {cfg.get('time')}")
        print(f"    Config: {cfg.get('config')[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# تست /settings
print("\n\n⚙️ /settings")
print("-" * 70)
try:
    res = requests.get(f"{base_url}/settings")
    data = res.json()
    print(f"✓ Settings loaded:")
    for key, val in data.items():
        print(f"  - {key}: {val}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("تست تمام شد")
print("=" * 70)
