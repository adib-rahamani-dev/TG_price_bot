#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def build_message(prices, from_cache=False):
    if not prices:
        return "❌ داده‌ای موجود نیست"
    now = prices[0]["time"]
    cache_indicator = "📊 (کش‌شده)" if from_cache else "💰"
    msg = f"{cache_indicator} <b>آخرین قیمت‌ها</b>\n⏰ {now}\n\n"
    for item in prices:
        change_val = item.get("change_value")
        arrow = "🔺" if (change_val is not None and change_val >= 0) else "🔻"
        unit = item.get("unit", "تومان")
        change_pct = item.get("change_percent", 0)
        msg += f"<b>{item['name']}:</b> {item['price']} {unit} ({arrow} {change_pct}%)\n"
    return msg

# خواندن prices_history.json
print("=" * 70)
print("تست build_message با داده‌های جدید")
print("=" * 70)

try:
    with open('prices_history.json', 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    if history:
        latest = history[-1]
        msg = build_message(latest, from_cache=True)
        
        print("\n📨 پیام نمایش داده شده در تلگرام:\n")
        print(msg)
        print("\n" + "=" * 70)
except Exception as e:
    print(f"❌ خطا: {e}")
