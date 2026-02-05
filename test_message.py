#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

def build_message(prices, from_cache=False):
    if not prices:
        return "❌ داده‌ای موجود نیست"
    now = prices[0]["time"]
    cache_indicator = "📊 (کش‌شده)" if from_cache else "💰"
    msg = f"{cache_indicator} <b>آخرین قیمت‌ها</b>\n⏰ {now}\n\n"
    for item in prices:
        unit = item.get("unit", "تومان")
        change_val = item.get("change_value", 0)
        change_pct = item.get("change_percent", 0)
        
        # اگر change_value None است، 0 استفاده کنید
        if change_val is None:
            change_val = 0
        
        arrow = "🔺" if change_val >= 0 else "🔻"
        
        # نمایش درست قیمت با unit
        msg += f"<b>{item['name']}:</b> {item['price']} {unit}"
        msg += f" ({arrow} {change_pct}%)"
        msg += "\n"
    return msg

# خواندن prices_cache.json
print("خواندن prices_cache.json...")
try:
    with open('prices_cache.json', 'r', encoding='utf-8') as f:
        prices = json.load(f)
    
    msg = build_message(prices, from_cache=True)
    
    print("\n" + "=" * 60)
    print("پیام نمایش داده شده در بات:")
    print("=" * 60 + "\n")
    print(msg)
    print("\n" + "=" * 60)
    print("HTML version:")
    print("=" * 60)
    print(msg)
    
except Exception as e:
    print(f"❌ خطا: {e}")
