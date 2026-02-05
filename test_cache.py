#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

# فیلتر نماد‌ها
FILTER_SYMBOLS = ["IR_GOLD_18K", "IR_COIN_EMAMI", "USDT"]

# خواندن market_cache.json
print("=" * 60)
print("خواندن market_cache.json...")
print("=" * 60)

try:
    with open('market_cache.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filtered = []
    for category, items in data.items():
        print(f"\n📂 Category: {category}")
        for item in items:
            symbol = item.get("symbol")
            if symbol in FILTER_SYMBOLS:
                name = item.get("name")
                price = item.get("price")
                unit = item.get("unit", "تومان")
                filtered.append({
                    "symbol": symbol,
                    "name": name,
                    "price": price,
                    "change_value": item.get("change_value"),
                    "change_percent": item.get("change_percent"),
                    "unit": unit,
                    "time": f"{item.get('date')} {item.get('time')}"
                })
                print(f"  ✓ {symbol}: {name} → {price} {unit}")
    
    print(f"\n{'=' * 60}")
    print(f"✅ تعداد نماد فیلتر شده: {len(filtered)}")
    print(f"{'=' * 60}\n")
    
    # ذخیره به prices_cache.json
    with open('prices_cache.json', 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print("✅ داده‌ها به prices_cache.json ذخیره شدند\n")
    
    # نمایش نتیجه
    print("محتوای prices_cache.json:")
    print(json.dumps(filtered, ensure_ascii=False, indent=2))
    
except Exception as e:
    print(f"❌ خطا: {e}")
